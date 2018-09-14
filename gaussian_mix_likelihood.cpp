# include "CC_ini_likelihood.hpp"
# include <cmath>

//============================================================
// Gaussian mixture module likelihood in PolyChord format
//============================================================


// Main loglikelihood function
//
// Either write your likelihood code directly into this function, or call an
// external library from it. This should return the logarithm of the
// likelihood, i.e:
//
// loglikelihood = log_e ( P (data | parameters, model ) )
//
// theta are the values of the input parameters (in the physical space 
// NB: not the hypercube space).
//
// nDims is the size of the theta array, i.e. the dimensionality of the parameter space
//
// phi are any derived parameters that you would like to save with your
// likelihood.
//
// nDerived is the size of the phi array, i.e. the number of derived parameters
//
// The return value should be the loglikelihood
//
// This function is called from likelihoods/fortran_cpp_wrapper.f90
// If you would like to adjust the signature of this call, then you should adjust it there,
// as well as in likelihoods/my_cpp_likelihood.hpp
// 
double log_sum_exp(double arr[], int count) 
{
   /**
   Helper function for calculating log-sum-exp of array values while protecting from overflow.

   Based on the answer at https://stackoverflow.com/questions/45943750/calculating-log-sum-exp-function-in-c

   @param arr: array containing values on which to perform log-sum-exp
   @param count: number of elements of array to sum
   @return log-sum-exp of arr (float)
   **/
   if(count > 0 ){
      double maxVal = arr[0];
      double sum = 0;
      for (int i = 1 ; i < count ; i++){
         if (arr[i] > maxVal){
            maxVal = arr[i];
         }
      }
      for (int i = 0; i < count ; i++){
         sum += exp(arr[i] - maxVal);
      }
      return log(sum) + maxVal;
   }
   else
   {
      return 0.0;
   }
}


double gaussian (double theta[], double mu[], double sigma, int nDims)
{
   /**
   Simple spherically symmetric Gaussian likelihood.

   @param theta: parameter values
   @param mu: likelihood mean
   @param sigma: Gaussian likelihood's standard deviation
   @param nDims: number of dimensions
   @return logL: loglikelihood
   **/
    double logL= -std::log(3.14159265358979323846 * 2. * sigma * sigma) * nDims / 2.;
    double rad2 = 0.;
    for (auto i=0;i<nDims;i++)
        rad2 += (theta[i]-mu[i])*(theta[i]-mu[i]);
    logL -= rad2 / (2.0 * sigma * sigma);
    return logL;
}


double loglikelihood (double theta[], int nDims, double phi[], int nDerived)
{
   /**
   4-component Gaussian mixture model used in the dynamic nested sampling paper.

   @param theta: parameter values
   @param nDims: number of dimensions
   @param: phi: derived parameters
   @param: nDerived: number of derived parameters
   @return logL: loglikelihood
   **/
    double sep = 4.0;
    double sigma = 1.0;
    double mu1[4] = {0.0, 0.0, sep, -sep};
    double mu2[4] = {sep, -sep, 0.0, 0.0};
    double weights[4] = {0.4, 0.3, 0.2, 0.1};

    double comp_logls[4] = { };
    for (int k=0; k<4; k++) {
        double mu[100] = { };  // as we don't know nDim at compile time, just make bigger than we need
        mu[0] = mu1[k];
        mu[1] = mu2[k];
        comp_logls[k] = gaussian(theta, mu, sigma, nDims) + std::log(weights[k]);
    }
    
    return log_sum_exp(comp_logls, 4);
}

// double loglikelihood (double theta[], int nDims, double phi[], int nDerived)
// {
//     double mu = 5e-1;
//     double sigma = 1e-1;
//     double logL = gaussian(theta, mu, sigma, nDims);
//     
//     return logL;
// 
// }

// Prior function
//
// Either write your prior code directly into this function, or call an
// external library from it. This should transform a coordinate in the unit hypercube
// stored in cube (of size nDims) to a coordinate in the physical system stored in theta
//
// This function is called from likelihoods/fortran_cpp_wrapper.f90
// If you would like to adjust the signature of this call, then you should adjust it there,
// as well as in likelihoods/my_cpp_likelihood.hpp
// 
void prior (double cube[], double theta[], int nDims)
{
    //============================================================
    // insert prior code here
    //
    //
    //============================================================
    for(int i=0;i<nDims;i++)
        theta[i] = cube[i];

}

// Dumper function
//
// This function gives you runtime access to variables, every time the live
// points are compressed by a factor settings.compression_factor.
//
// To use the arrays, subscript by following this example:
//
//    for (auto i_dead=0;i_dead<ndead;i_dead++)
//    {
//        for (auto j_par=0;j_par<npars;j_par++)
//            std::cout << dead[npars*i_dead+j_par] << " ";
//        std::cout << std::endl;
//    }
//
// in the live and dead arrays, the rows contain the physical and derived
// parameters for each point, followed by the birth contour, then the
// loglikelihood contour
//
// logweights are posterior weights
// 
void dumper(int ndead,int nlive,int npars,double* live,double* dead,double* logweights,double logZ, double logZerr)
{
}


// Setup of the loglikelihood
// 
// This is called before nested sampling, but after the priors and settings
// have been set up.
// 
// This is the time at which you should load any files that the likelihoods
// need, and do any initial calculations.
// 
// This module can be used to save variables in between calls
// (at the top of the file).
// 
// All MPI threads will call this function simultaneously, but you may need
// to use mpi utilities to synchronise them. This should be done through the
// integer mpi_communicator (which is normally MPI_COMM_WORLD).
//
// This function is called from likelihoods/fortran_cpp_wrapper.f90
// If you would like to adjust the signature of this call, then you should adjust it there,
// as well as in likelihoods/my_cpp_likelihood.hpp
//
void setup_loglikelihood()
{
    //============================================================
    // insert likelihood setup here
    //
    //
    //============================================================
}
