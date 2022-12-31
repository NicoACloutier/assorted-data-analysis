#include<stdio.h>
#include<math.h>
#include<stdlib.h>

//GAUSSIAN NAÏVE BAYES CLASSIFIER

struct Gaussian {
	double mean;
	double std_dev;
};

struct MultipleGaussian {
	int dimensions;
	struct Gaussian *gaussians;
};