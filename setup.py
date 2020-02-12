import os
from setuptools import setup

import sys

# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))

packages = []
for rootdir, dirs, files in os.walk('mldebugger'):
    if '__init__.py' in files:
        packages.append(rootdir.replace('\\', '.').replace('/', '.'))

req = ['numpy',
       'zmq',
       'certifi>=2017.4.17',
       'Pillow',
       'image',
       'scikit-learn==0.19.0',
       'sklearn==0.0',
       'vistrails==2.2.4',
       'nose==1.3.7',
       'pandas==0.24.0',
       'scipy == 0.19.1',
       'Django == 1.11.28']

if sys.version_info < (2, 7):
    req.append('argparse')

setup(name='MLDebugger',
      version='0.1',
      packages=['mldebugger'],
      entry_points={
          'console_scripts': [
              'mldebugger = mldebugger.run:main',
              'worker = mldebugger.workers.vistrails_worker',
              'python_worker = mldebugger.workers.python_worker']},
      install_requires=req,
      description="MlDebugger library",
      author="Raoni Lourenco",
      author_email='raoni@nyu.edu',
      maintainer='Raoni Lourenco',
      maintainer_email='raoni@nyu.edu',
      keywords=['Machine Learning Pipelines',
                'Provenance',
                'Heuristic Algorithms',
                'Debugging',
                'Combinatorial Design',
                'Parameter Exploration'])
