from openclean.align.distance import Distance, DISTANCE_ABSOLUTE

class AbsoluteDistance(Distance):
    def __init__(self):
        super(AbsoluteDistance, self).__init__(DISTANCE_ABSOLUTE)

    def get_distance(self, u, v):
        if isinstance(u, list) or isinstance(v, list):
            raise TypeError("get_distance expects a list input")
        return abs(len(u)-len(v))