#!/usr/bin/env python
"""Generate results using dyPolyChord."""
# pylint: disable=wrong-import-position
import copy
import os
import sys
import traceback
from mpi4py import MPI  # initialise MPI
if 'ejh81' in os.getcwd().split('/'):  # running on cluster
    # Use non-interactive matplotlib backend. Must set this before pyplot
    # import.
    import matplotlib
    matplotlib.use('pdf')
import nestcheck.parallel_utils
import dyPolyChord.pypolychord_utils
import dyPolyChord.polychord_utils
import bsr.basis_functions as bf
import bsr.likelihoods
import bsr.priors
import bsr.data


def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Get dyPolyChord runs (and standard nested sampling runs to compare them
    to). Optionally also make results plots. Edit the settings variables at the
    start of the function to determine what to run.

    Compiled C++ vs Python likelihoods
    ----------------------------------

    Whether to use the Python or compiled C++ likelihoods is determined by the
    "compiled" (bool) variable. The results should be the same but the C++
    likelihood is faster. All results can be run in either Python or C++ except
    those using bf.adfam_gg_ta_1d which are currently only set up in Python.

    The C++ likelihood is contained in the "CC_ini_likelihood.cpp" file and
    must be compiled before use. With PolyChord v1.15 already installed with
    MPI, this can be done with the following commands:

        $ cp CC_ini_likelihood.cpp
        ~/path_to_pc/PolyChord/likelihoods/CC_ini/CC_ini_likelihood.cpp
        $ cd ~/path_to_pc/PolyChord
        $ make polychord_CC_ini

    This creates an executable at PolyChord/bin/polychord_CC_ini. The ex_path
    variable must be updated to point to this. For more details see the
    PolyChord and dyPolyChord documentation.

    Parallelisation for compiled C++ likelihoods is performed through the
    mpi_str argument, and compute_results.py (this module) should not be
    executed with an mpirun command. In contrast Python likelihoods are run
    with parallelisation using an mpirun command on this module; for example

        $ mpirun -np 6 python3 compute_results.py

    Data Sets and Fitting Functions
    -------------------------------

    * fit_func is the function with which to fit the data (e.g. a basis
      function or neural network).
    * data_func specifies the type of data (basis function from which the true
      signal was sampled, or alternatively bsr.data.get_image for astronomical
      images).
    * data_type specifies which of the data sets using that data_func to use.
      For signals made from a mixture model of basis functions, this is the
      number of mixture components. For astronomical images it specifies which
      of the .jpeg images in bsr/images/ to use.

    Method settings
    ---------------

    * dynamic_goal is None for standard nested sampling and otherwise
      corresponds to dyPolyChord's dynamic_goal setting.
    * nlive is the number of live points.
    * num_repeats is the PolyChord/dyPolyChord num_repeats setting.
    """
    # ###################################################################
    # Settings
    # ###################################################################
    # Runtime settings
    # ----------------
    compiled = False  # Whether to use compiled C++ likelihood or Python
    nlive = 40
    ninit = 20
    num_repeats = 10
    inds = list(range(1, 6))
    dg_list = [0.25]  # [None, 0, 0.25, 1]
    # PolyChord settings
    # ------------------
    use_mpi = True  # only affects compiled == True
    settings_dict = {
        'nlive': nlive,
        'num_repeats': num_repeats,
        'max_ndead': -1,
        'do_clustering': True,
        'posteriors': False,
        'equals': False,
        'base_dir': 'chains',
        'feedback': -1,
        'precision_criterion': 0.001,
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
    # Likelihood and prior
    # --------------------
    fit_func = bf.gg_1d
    nfunc = 3
    y_error_sigma = 0.05
    x_error_sigma = None
    # ###################################################################
    # Run program
    # ###################################################################
    data = bsr.data.generate_data(
        fit_func, nfunc, y_error_sigma, x_error_sigma=x_error_sigma)
    likelihood = bsr.likelihoods.FittingLikelihood(
        data, fit_func, nfunc, adaptive=False)
    prior = bsr.priors.get_default_prior(
        fit_func, nfunc, adaptive=False)
    # Initialise MPI
    comm = MPI.COMM_WORLD
    if compiled:
        assert comm.Get_size() == 1, (
            'compiled likelihoods should use mpi via mpi_str. '
            'comm.Get_size()={}').format(comm.Get_size())
        mpi_str = None
        # Work out if we are running on cluster or laptop
        if 'ed' in os.getcwd().split('/'):
            ex_path = '/home/ed/code/'
            if use_mpi:
                mpi_str = 'mpirun -np 6'
        else:
            ex_path = '/home/ejh81/'
            if use_mpi:
                mpi_str = 'mpirun -np 32'
        ex_path += 'PolyChord/bin/polychord_CC_ini'
    # Before running in parallel make sure base_dir exists, as if
    # multiple threads try to make one at the same time mkdir
    # throws an error.
    if comm.Get_rank() == 0:
        print('compiled={} mpi={}'.format(
            compiled, comm.Get_size() if not compiled else mpi_str))
        sys.stdout.flush()  # Make sure message prints
        try:
            if not os.path.exists(settings_dict['base_dir']):
                os.makedirs(settings_dict['base_dir'])
            if not os.path.exists(settings_dict['base_dir'] + '/clusters'):
                os.makedirs(settings_dict['base_dir'] + '/clusters')
        except:  # pylint: disable=bare-except
            if comm is None or comm.Get_size() == 1:
                raise
            else:
                # print error info
                traceback.print_exc(file=sys.stdout)
                print('Error in process with rank == 0: forcing MPI abort.')
                sys.stdout.flush()  # Make sure message prints before abort
                comm.Abort(1)  # Force all processes to abort
    # Generate nested sampling runs
    # -----------------------------
    # pylint: disable=too-many-nested-blocks
    for dynamic_goal in dg_list:
        # Do the nested sampling
        # ----------------------
        # make list of settings dictionaries for the different repeats
        file_root = likelihood.get_file_root(
            settings_dict['nlive'], settings_dict['num_repeats'],
            dynamic_goal=dynamic_goal)
        settings_list = []
        for extra_root in inds:
            settings = copy.deepcopy(settings_dict)
            if comm is None or comm.Get_size() == 1:
                settings['seed'] = extra_root * (10 ** 3)
            else:
                settings['seed'] = -1
            settings['file_root'] = (file_root + '_'
                                     + str(extra_root).zfill(3))
            settings_list.append(settings)
        # concurret futures parallel settings
        parallel = False  # if already running with MPI, set to False
        parallel_warning = False
        max_workers = 6
        tqdm_kwargs = {'disable': True}
        if not compiled:
            run_func = dyPolyChord.pypolychord_utils.RunPyPolyChord(
                likelihood, prior, likelihood.ndim)
        else:
            prior_str = bsr.priors.bsr_prior_to_str(prior)
            run_func = (dyPolyChord.polychord_utils
                        .RunCompiledPolyChord(
                            ex_path, prior_str, mpi_str=mpi_str,
                            config_str=likelihood.cpp_config_str()))
        if dynamic_goal is None:
            # For standard nested sampling just run PolyChord
            nestcheck.parallel_utils.parallel_apply(
                run_func, settings_list,
                parallel=parallel, parallel_warning=parallel_warning,
                max_workers=max_workers, tqdm_kwargs=tqdm_kwargs)
        else:
            if comm.Get_size() > 1:
                seed_increment = -1
            else:
                seed_increment = 1
            # Dynamic nested sampling with dyPolyChord
            nestcheck.parallel_utils.parallel_apply(
                dyPolyChord.run_dynamic_ns.run_dypolychord,
                settings_list,
                func_pre_args=(run_func, dynamic_goal),
                func_kwargs={'ninit': ninit,
                             'seed_increment': seed_increment,
                             'clean': True,
                             'nlive_const': settings_dict['nlive'],
                             'comm': None if compiled else comm},
                parallel=parallel, parallel_warning=parallel_warning,
                max_workers=max_workers, tqdm_kwargs=tqdm_kwargs)


if __name__ == '__main__':
    main()
