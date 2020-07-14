import io
import os
from setuptools import setup


os.chdir(os.path.abspath(os.path.dirname(__file__)))

# todo: update urls
with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
setup(name='openclean',
      version='0.1',
      packages=['openclean_re'],
      description="OpenClean Regex Anomaly Detection",
      author="Munaf Qazi",
      author_email='munaf@nyu.edu',
      maintainer="Munaf Qazi",
      maintainer_email='munaf@nyu.edu',
      url='https://gitlab.com/ViDA-NYU/',
      project_urls={
          'Homepage': 'https://gitlab.com/ViDA-NYU/',
          'Source': 'https://gitlab.com/ViDA-NYU/',
          'Tracker': 'https://gitlab.com/ViDA-NYU/',
      },
      long_description=description,
      license='BSD-3-Clause',
      keywords=['openclean'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Science/Research',
          'License :: Free for non-commercial use',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Database'])
