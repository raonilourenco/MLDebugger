# MLDebugger

MLDebugger is a framework for finding root causes of erros in machine learning pipelines. For more detailed information about the framework, please refer to our DEEM paper:

[*Debugging Machine Learning Pipelines. R. Lourenco, J. Freire, and D. Shasha. In Proceedings of the 3rd International Workshop on Data Management for End-to-End Machine Learning (DEEM),2019*](https://dl.acm.org/citation.cfm?id=3329489)


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

To run our example:

    $ mldebugger examples/classification_pipeline.vt examples/params.json

More detailed documentation is coming soon.