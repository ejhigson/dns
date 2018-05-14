#!/usr/bin/env python
"""
Run dyPolyChord results for a Gaussian mixture likelihood. This script
was used to make the Gaussian mixture model results in the dynamic
nested sampling paper (Higson et al., 2017).

Random seeding is used for reproducible results, which is only
possible when PolyChord is installed *without* MPI due to the unpredictable
order in which threads will provide samples (see the PolyChord
documentation for more details). As generating repeated runs is embarrassingly
parallel we can instead parallelise using concurrent.futures via nestcheck's
parallel_apply function.

Note also that PolyChord's random number generator can vary between systems and
compilers, so your results may not exactly match those in the paper (which were
run on Ubuntu 18.04 with PolyChord compiled using gfortran 7.3.0).

These results can be run with a python or C++ likelihood by setting the
'compiled' variable to True or False. C++ is *much* faster but requires
compiling with PolyChord.

Compiling the C++ likelihood
----------------------------

With PolyChord 1.14, gaussian_mix_likelihood.cpp can be compiled with the
following commands. This assumes PolyChord is already installed, without
MPI, in location path_to_pc/PolyChord.

    $ cp gaussian_mix_likelihood.cpp
    ~/path_to_pc/PolyChord/likelihoods/CC_ini/CC_ini_likelihood.cpp
    $ cd ~/path_to_pc/PolyChord
    $ make polychord_CC_ini

This produces an executable at PolyChord/bin/polychord_CC_ini which you can
move back to the current directory to run (or edit RunCompiledPolyChord's
executable path accordingly).
For more details see PolyChord's README.
"""
import copy
import os
import nestcheck.parallel_utils
import dyPolyChord.python_likelihoods as likelihoods
import dyPolyChord.python_priors as priors
import dyPolyChord.output_processing
import dyPolyChord.polychord_utils
import dyPolyChord


def main():
    """Get dyPolyChord runs (and standard nested sampling runs to compare them
    to)."""
    start_ind = 200
    end_ind = 500
    parallel = True
    max_workers = 6
    dg_list = [None, 0, 0.25, 1]
    nlive_const = 500
    num_repeats = 50
    compiled = True
    # Set up problem
    # --------------
    ndim = 10
    prior_scale = 10
    if not compiled:
        likelihood = likelihoods.GaussianMix()
        prior = priors.Gaussian(prior_scale)
        from dyPolyChord.pypolychord_utils import RunPyPolyChord
        run_func = RunPyPolyChord(likelihood, prior, ndim)
    else:
        prior_str = dyPolyChord.polychord_utils.get_prior_block_str(
            'gaussian', [0.0, float(prior_scale)], ndim)
        run_func = dyPolyChord.polychord_utils.RunCompiledPolyChord(
            './polychord_CC_ini', prior_str)
    # dynamic settings - only used if dynamic_goal is not None
    seed_increment = 1
    ninit = 100
    clean = True
    init_step = ninit
    # PolyChord settings
    settings_dict = {
        'do_clustering': True,
        'posteriors': False,
        'equals': False,
        'num_repeats': num_repeats,
        'base_dir': 'chains',
        'feedback': -1,
        'precision_criterion': 0.001,
        'nlive': nlive_const,
        'nlives': {},
        'write_dead': True,
        'write_stats': True,
        'write_paramnames': False,
        'write_prior': False,
        'write_live': False,
        'write_resume': False,
        'read_resume': False,
        'cluster_posteriors': False,
        'boost_posterior': 0.0}
    for dynamic_goal in dg_list:
        # Set max_ndead for dynamic runs so they use slightly fewer samples
        # than the standard runs
        if dynamic_goal is None:
            settings_dict['max_ndead'] = -1
        else:
            settings_dict['max_ndead'] = 14500
        # make list of settings dictionaries for the different repeats
        file_root = dyPolyChord.output_processing.settings_root(
            'gaussian_mix_4comp_4sep',
            'gaussian', ndim,
            prior_scale=prior_scale,
            dynamic_goal=dynamic_goal,
            ninit=ninit, init_step=init_step,
            nrepeats=num_repeats,
            nlive_const=nlive_const).replace('.', '_')
        settings_list = []
        for extra_root in range(start_ind + 1, end_ind + 1):
            settings = copy.deepcopy(settings_dict)
            settings['seed'] = extra_root * (10 ** 3)
            settings['file_root'] = file_root + '_' + str(extra_root).zfill(3)
            settings_list.append(settings)
        # Before running in parallel make sure base_dir exists, as if multiple
        # threads try to make one at the same time mkdir throws an error.
        if not os.path.exists(settings_dict['base_dir']):
            os.makedirs(settings_dict['base_dir'])
        # Do the nested sampling
        # ----------------------
        if dynamic_goal is None:
            # For standard nested sampling just run PolyChord
            nestcheck.parallel_utils.parallel_apply(
                run_func, settings_list,
                max_workers=max_workers,
                parallel=parallel,
                tqdm_kwargs={'desc': 'dg=' + str(dynamic_goal),
                             'leave': True})
        else:
            # Dynamic nested sampling with dyPolyChord
            nestcheck.parallel_utils.parallel_apply(
                dyPolyChord.run_dypolychord, settings_list,
                max_workers=max_workers,
                func_pre_args=(run_func, dynamic_goal),
                func_kwargs={'ninit': ninit,
                             'init_step': init_step,
                             'seed_increment': seed_increment,
                             'clean': clean,
                             'nlive_const': nlive_const},
                parallel=parallel,
                tqdm_kwargs={'desc': 'dg=' + str(dynamic_goal),
                             'leave': True})


if __name__ == '__main__':
    main()
