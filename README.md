# Dynamic nested sampling

[![arXiv](http://img.shields.io/badge/arXiv-1704.03459-B31B1B.svg)](https://arxiv.org/abs/1704.03459)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ejhigson/dns/blob/master/LICENSE)

This repository contains the code used for making the results and plots in the dynamic nested sampling paper ([Higson et. al, 2017](https://arxiv.org/abs/1704.03459)).

If you have any questions then feel free to email e.higson@mrao.cam.ac.uk. However, note that is research code and is not actively maintained.

### Requirements

The results in the paper were run in python 3.6 using:

* [perfectns](https://github.com/ejhigson/perfectns) v2.0.1;
* [dyPolyChord](https://github.com/ejhigson/dyPolyChord) v0.0.0;
* [PolyChord](https://ccpforge.cse.rl.ac.uk/gf/project/polychord/) v1.14;
* [nestcheck](https://github.com/ejhigson/nestcheck) v0.1.0.

Aside from dependencies of the above modules (such as `scipy`, `numpy`, `pandas` and `matplotlib`), the only other package required is `getdist`; this is used for the triangle plots of Gaussian mixture posteriors.

### Code

The code is divided into two jupyter notebooks:

* `perfectns_paper_results.ipynb` contains perfect nested sampling results and plots. Some results tables are cached in the `perfectns_results` directory so this should not take long to run. Alternatively you can reproduce the nested sampling run data yourself using `make_perfectns_results.py`, although this is quite computationally intensive. `numpy` random seeding is used by default, so all results should be reproducible.
* `dypolychord_paper_results.ipynb` contains the Gaussian mixture model results. It requires nested sampling runs which can be generated using `make_dypolychord_results.py`; see the module docstring for more details, including about the random seeding used. This can be done with either the python or C++ versions of the likelihood (the results are identical up to numerical precision errors, but latter runs much faster).

### Attribution

If it is useful for your research then please cite the dynamic nested sampling paper. The BibTeX is:

```latex
@article{Higson2017,
author={Higson, Edward and Handley, Will and Hobson, Mike and Lasenby, Anthony},
title={Dynamic nested sampling: an improved algorithm for parameter estimation and evidence calculation},
journal={arXiv preprint arXiv:1704.03459},
url={https://arxiv.org/abs/1704.03459},
year={2017}}
```
