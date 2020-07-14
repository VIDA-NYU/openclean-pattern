from openclean import GAP_SYMBOL
from openclean.align import Aligner, ALIGNER_COMB
from openclean.align.distance import DISTANCE_TDE, DISTANCE_ETDE
from openclean.align.distance.factory import DistanceFactory
import os, concurrent, csv, math, ast

from openclean.regex.regex_objects import RegexToken, RegexRow
from openclean.regex import GAP

import numpy as np

ALIGNER_COMB_PERM = 'perm'
ALIGNER_COMB_COMB = 'comb'

ALIGNER_COMB_SUPPORTED = [ALIGNER_COMB_PERM, ALIGNER_COMB_COMB]

class CombAligner(Aligner):
    '''
    Create sets of permutation/combination alignments
    '''
    def __init__(self,
                 comb_type: str = ALIGNER_COMB_COMB,
                 distance: str = DISTANCE_TDE,
                 ) -> None:
        super(CombAligner, self).__init__(ALIGNER_COMB)
        if comb_type not in ALIGNER_COMB_SUPPORTED:
            raise NotImplementedError(comb_type)
        self._comb_type = comb_type
        self._distance = DistanceFactory(distance).get_distance()
        self._gap_char = GAP_SYMBOL if distance != DISTANCE_ETDE else RegexToken(regex_type=GAP,size=1,token=GAP_SYMBOL,freq=1)

    def get_alignment_permutations(self, my_list, dash):
        def __insert_dash(this_list):
            dashed = list()
            dash_out = self._gap_char
            for i in range(len(this_list), -1, -1):
                dashed.append(this_list[:i] + [dash_out] + this_list[i:])
            return dashed

        if dash <= 0:
            return my_list

        new_list = list()
        for ml in my_list:
            [new_list.append(i) for i in __insert_dash(ml)]

        return self.get_alignment_permutations(new_list, dash - 1)

    def get_alignment_combinations(self, my_list, dash):
        mla = self.get_alignment_permutations([my_list], dash)
        return set(tuple(x) for x in mla)

    def _get_aligned_distance(self, i, j, u, v):
        '''
            take in tokens lists and return distance min avg distances
            i and j keep track of the job incase order changes in a multithreaded env
            only does alignment if one row is bigger than the other
            todo: allow same sized rows to be aligned too:
            e.g.:
            HAPPY NEW YEAR
            HAPPY 12 BIRTHDAY
            =================
            HAPPY - NEW YEAR
            HAPPY 12 - BIRTHDAY

            OR

            HAPPY - NEW YEAR
            HAPPY 12 BIRTHDAY -

            ETC (THERE ARE OTHERS TOO)
        '''

        distance = self._distance
        smaller = u if len(u) == min(len(u), len(v)) else v
        larger = v if smaller == u else u

        ind0, ind1 = (i, j) if larger == v else (j, i)

        dashes = len(larger) - len(smaller)
        avg_min_dist = 1 # todo change this. this no. goes over 1 for some combinations
        alignment = None

        # check if doing permutations worth it or are they too different already
        try:
            perms = math.factorial(len(larger)) / math.factorial(dashes)
        except Exception:
            perms = 100000 # dont do the next steps unless no dashes because rows are too long

        if perms > 50000:
            pass
            # print('more than 50k permutations: {},{}'.format(smaller, larger))
        if (perms < 50000 and dashes < 5) or dashes == 0:
            if self._comb_type == ALIGNER_COMB_PERM:
                combinations = self.get_alignment_permutations(smaller, dashes)
            elif self._comb_type == ALIGNER_COMB_COMB:
                combinations = self.get_alignment_combinations(smaller, dashes)
            for combo in combinations:
                try:
                    combo = RegexRow(regex_row=list(combo), frequency=smaller.frequency) if isinstance(larger, RegexRow) else list(combo)
                    dist = distance.get_distance(combo, larger) / len(combo)
                except Exception as e:
                    print(combo, larger, e)
                if dist < avg_min_dist:
                    avg_min_dist = dist
                    alignment = {ind0: combo, ind1: larger}

        return i, j, avg_min_dist, alignment

    def _cluster(self, tokenized, distance_array, pattern_array):
        from sklearn.cluster import DBSCAN
        import pandas as pd

        # todo: make DBSCAN configurable
        db = DBSCAN(metric="precomputed", eps=.1, n_jobs=-1, min_samples=5).fit(distance_array)
        clusters = pd.DataFrame([tokenized]).T.join(pd.DataFrame(db.labels_), lsuffix='_l', rsuffix='_r')

        clusters.columns = ['tokens', 'cluster']

        # add an extra column to push aligned patterns into it
        clusters['aligned'] = np.nan
        clusters.aligned = clusters.aligned.astype(object) # requirement to use 'df.at'
        for c in clusters.cluster.unique():
            cluster_indices = clusters[clusters.cluster == c].index
            for ci in cluster_indices:
                try:
                    if ci == cluster_indices[0]:
                        if len(cluster_indices) > 1:
                            clusters.at[ci, 'aligned'] = pattern_array[cluster_indices[1], ci][ci]
                        else:
                            clusters.at[ci, 'aligned'] = pattern_array[ci, ci][ci]
                        continue
                    clusters.at[ci, 'aligned'] = pattern_array[cluster_indices[0], ci][ci]
                except TypeError as te:
                    clusters.at[ci,'aligned'] = np.nan # null when too many combinations
                    # i.e. values were too different. this is mostly classified as noise
        return clusters

    def get_aligned(self, rows):
        MAX_JOBS_IN_QUEUE = os.cpu_count()
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() - 1) as executor, \
                open('inter_result.csv', 'w') as csv_file:
            # A dictionary which will contain a list the future info in the key, and the filename in the value
            jobs = {}
            filewriter = csv.writer(csv_file, delimiter='\t')
            filewriter.writerow(['i', 'j', 'dist', 'alignment'])

            # all possible combinations of comparisons
            inputs = [(i, j) for i in range(len(rows)) for j in range(i+1)]

            # run the function for each input, the results of can come back in any order - so keep track of them by returning position
            inputs_left = len(inputs)
            inputs_iter = iter(inputs)

            while inputs_left:
                for inp in inputs_iter:
                    job = executor.submit(self._get_aligned_distance, inp[0], inp[1], rows[inp[0]],
                                          rows[inp[1]])
                    jobs[job] = inp
                    if len(jobs) > MAX_JOBS_IN_QUEUE:
                        break  # limit the job submission for now job

                # Get the completed jobs whenever they are done
                for job in concurrent.futures.as_completed(jobs):
                    inputs_left -= 1  # one down - many to go...
                    # print(inputs_left)
                    # Send the result of the file the job is based on (jobs[job]) and the job (job.result)
                    i, j, dist, alignment = job.result()

                    # delete the result from the dict as we don't need to store it.
                    del jobs[job]

                    # post-processing (putting the results into a database)
                    filewriter.writerow([i, j, dist, alignment])
                    break  # give a chance to add more jobs

        distance_array = (np.identity(len(rows))-1)*-1 # default/unprocessed distance = 1 except diagonal
        pattern_array = np.empty((len(rows), len(rows)), dtype=object)
        with open('inter_result.csv', 'r') as csv_file:
            filereader = csv.reader(csv_file, delimiter='\t')
            for row in filereader:
                try:
                    i, j, dist, alignment = int(float(row[0])), int(float(row[1])), float(row[2]), ast.literal_eval(row[3])
                    distance_array[i, j] = distance_array[j, i] = dist
                    pattern_array[i, j] = pattern_array[j, i] = alignment
                except Exception:
                    try:
                        i, j, dist, alignment = int(float(row[0])), int(float(row[1])), float(row[2]), eval(row[3])
                        distance_array[i, j] = distance_array[j, i] = dist
                        pattern_array[i, j] = pattern_array[j, i] = alignment
                    except Exception as exc2:
                        pass
                        # print(exc2, row[3]) # errors for where combinations too many, alignment not parsed to RegexToken and file header

        return self._cluster(rows, distance_array, pattern_array)
