#!/usr/bin/env python
"""
Saves the dynamic nested sampling run data from perfectns used in the
dynamic nested sampling paper (Higson et al., 2017). Uses numpy random
seeding by default so results should be reproducible.

This is ~500GB of data and takes ~1500 processor hours to run (most of
which is for the 1000d examples) so is best done on a high performance
cluster.
"""
import perfectns.priors as priors
import perfectns.likelihoods as likelihoods
import perfectns.settings
import perfectns.estimators as e
import perfectns.plots
import perfectns.results_tables


estimator_list = [e.LogZ(),
                  e.ParamMean(),
                  e.ParamSquaredMean(),
                  e.ParamCred(0.5),
                  e.ParamCred(0.84),
                  e.RMean(),
                  e.RCred(0.5),
                  e.RCred(0.84)]
settings = perfectns.settings.PerfectNSSettings()
settings.ninit = 10
settings.nlive_const = 200
settings.likelihood = likelihoods.Gaussian(likelihood_scale=1)
settings.prior = priors.Gaussian(prior_scale=10)
settings.n_dim = 10
likelihoods_list = [likelihoods.Gaussian(1),
                    likelihoods.ExpPower(1, 2),
                    likelihoods.ExpPower(1, 0.75)]
dim_scale_list = [(2, s) for s in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]]
dim_scale_list += [(d, 10) for d in [2, 5, 10, 20, 50, 100, 200, 500, 1000]]
# Generate the data
# -----------------
results_in = perfectns.results_tables.merged_dynamic_results(
    dim_scale_list, likelihoods_list, settings, estimator_list, save=True,
    load=True)

# # Alternatively, this can be run in several batches
# # -------------------------------------------------
# BATCH = 1  # Set this to 1, 2, 3, 4
# assert BATCH in [1, 2, 3, 4]
# if BATCH == 1:
#     dim_scale_list = []
#     dim_scale_list += [(2, s) for s in [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50,
#                                         100]]
#     dim_scale_list += [(d, 10) for d in [2, 5, 10, 20, 50, 100]]
# elif BATCH == 2:
#     dim_scale_list = [(d, 10) for d in [200, 500]]
# elif BATCH == 3:
#     likelihoods_list = [likelihoods.Gaussian(1),
#                         likelihoods.ExpPower(1, 0.75)]
#     dim_scale_list = [(1000, 10)]
# elif BATCH == 4:
#     likelihoods_list = [likelihoods.ExpPower(1, 2)]
#     dim_scale_list = [(1000, 10)]
# # Generate the data
# # -----------------
# results_in = perfectns.results_tables.merged_dynamic_results(
#     dim_scale_list, likelihoods_list, settings, estimator_list, save=True,
#     load=True)
