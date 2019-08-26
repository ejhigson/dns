# Dynamic nested sampling

[![DOI](http://img.shields.io/badge/DOI-10.1007/s11222--018--9844--0-darkblue.svg)](https://doi.org/10.1007/s11222-018-9844-0)
[![arXiv](http://img.shields.io/badge/arXiv-1704.03459-B31B1B.svg)](https://arxiv.org/abs/1704.03459)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ejhigson/dns/blob/master/LICENSE)

This repository contains the code used for making the results and plots in the dynamic nested sampling paper ([Higson et. al, 2019](https://doi.org/10.1007/s11222-018-9844-0)).

If you have any questions then feel free to email <e.higson@mrao.cam.ac.uk>. However, note that this is research code and is not actively maintained.

### Requirements

The results in the paper (except those in Section 6.2) were run in Python 3.6 using:

* [perfectns](https://github.com/ejhigson/perfectns) v2.0.1;
* [dyPolyChord](https://github.com/ejhigson/dyPolyChord) v0.0.0;
* [PolyChord](https://ccpforge.cse.rl.ac.uk/gf/project/polychord/) v1.14;
* [nestcheck](https://github.com/ejhigson/nestcheck) v0.1.0.

Later versions of the above software should give the same results. The signal reconstruction example in Section 6.2 were added in a later draft and used:

* [dyPolyChord](https://github.com/ejhigson/dyPolyChord) v0.0.5;
* [PolyChord](https://ccpforge.cse.rl.ac.uk/gf/project/polychord/) v1.15;
* [nestcheck](https://github.com/ejhigson/nestcheck) v0.1.9;
* [bsr](https://github.com/ejhigson/bsr) v0.0.0.

Aside from dependencies of the above modules (such as `scipy`, `numpy`, `pandas` and `matplotlib`), the only other package required is `getdist`; this is used for the triangle plots of Gaussian mixture posteriors.

### Code

The code is divided into two Jupyter notebooks:

* `perfectns_paper_results.ipynb` contains perfect nested sampling results and plots. Some results tables are cached in the `perfectns_results` directory so this should not take long to run. Alternatively you can reproduce the nested sampling run data yourself using `make_perfectns_results.py`, although this is quite computationally intensive. `numpy` random seeding is used by default, so all results should be reproducible.
* `dypolychord_paper_results.ipynb` contains the code used for the Gaussian mixture model and signal reconstruction results. It requires nested sampling runs which can be generated using `make_gaussian_mix_results.py` and `make_fit_results.py`; see the module docstrings for more details, including about the random seeding used. This can be done with either the Python or C++ versions of the likelihood (the results are identical up to numerical precision errors, but latter runs much faster).

### Attribution

If it is useful for your research, then please cite the dynamic nested sampling paper. The BibTeX is:

```latex
@article{Higson2019dynamic,
author={Higson, Edward and Handley, Will and Hobson, Michael and Lasenby, Anthony},
title={Dynamic nested sampling: an improved algorithm for parameter estimation and evidence calculation},
year={2019},
journal={Statistics and Computing},
volume={29},
number={5},
pages={891--913},
doi={10.1007/s11222-018-9844-0},
url={https://doi.org/10.1007/s11222-018-9844-0},
archivePrefix={arXiv},
arxivId={1704.03459}}
```
