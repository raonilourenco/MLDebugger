# MLDebugger [![Build Status](https://travis-ci.com/raonilourenco/MLDebugger.svg?branch=master)](https://travis-ci.com/raonilourenco/MLDebugger)

MLDebugger is a framework for finding root causes of errors in machine learning pipelines. For more detailed information about the framework, please refer to our DEEM paper:

[*Debugging Machine Learning Pipelines. R. Lourenco, J. Freire, and D. Shasha. In Proceedings of the 3rd International Workshop on Data Management for End-to-End Machine Learning (DEEM),2019*](https://arxiv.org/abs/2002.04640)


The team includes:

* [Raoni Lourenço][rl] (New York University)
* [Juliana Freire][jf] (New York University)
* [Dennis Shasha][ds] (New York University)

[rl]: https://engineering.nyu.edu/raoni-lourenco
[jf]: http://vgc.poly.edu/~juliana/
[ds]: http://cs.nyu.edu/shasha/
We strongly suggest users to read our paper before using our code.


* [1. How To Build](#4-how-to-build)
* [2. How To Run](#5-how-to-run)

## 1. How To Build

To install latest development version:

    $ pip install -e .
    
## 2. How to Run

To run our example with a machine learning pipeline written in VisTrail, first you need to start a worker:

    $ worker &

Then run the executable passing the pipeline path and property-value search space:

    $ mldebugger examples/classification_pipeline.vt examples/params.json

More detailed documentation is coming soon.
