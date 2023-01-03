#include<stdio.h>
#include<math.h>
#include<stdlib.h>

//GAUSSIAN NAÏVE BAYES CLASSIFIER

#define ROOT_TWO_PI 2.506628274 //define the constant sqrt(2*pi)

//a univariate Gaussian distribution
struct Gaussian {
	double mean; //the mean
	double std_dev; //the standard deviation
};

//a multivariate Gaussian distribution
struct MultipleGaussian {
	int dimensions; //the number of dimensions in the distribution
	struct Gaussian *gaussians; //an array of univariate Gaussians
};

//a Gaussian Naive Bayes classifier
struct GaussianNaiveBayes {
	struct MultipleGaussian *gaussian_list; //the array of multivariate Gaussians
	int number_distributions; //the number of distributions in the array
	int dimensions;
};

//get the overall probability in a list of probabilities
double overall_probability(double *vector, int length) {
	double probability = vector[0];
	for (int i = 1; i < length; i++) {
		probability *= vector[i];
	}
	return probability;
}

//raise Euler's constant to a power
double exp(double power) {
	return pow(M_E, power);
}

//get the probability of an x coordinate in a univariate Gaussian
double get_probability(struct Gaussian distribution, double x) {
	
	double normalized_square_distance = (x - distribution.mean);
	normalized_square_distance /= distribution.std_dev;
	normalized_square_distance = pow(normalized_square_distance, 2);
	
	double answer = 1 / (distribution.std_dev * ROOT_TWO_PI);
	answer *= exp(-0.5 * normalized_square_distance);
	
	return answer;
}

//get a vector of probabilities for each dimension with a multivariate Gaussian
double *get_probabilities(struct MultipleGaussian distributions, double *x) {
	double *probabilities = malloc(sizeof(double) * distributions.dimensions);
	struct Gaussian distribution;
	double temp_x;
	for (int i = 0; i < distributions.dimensions; i++) {
		distribution = distributions.gaussians[i];
		temp_x = x[i];
		probabilities[i] = get_probability(distribution, temp_x);
	}
	return probabilities;
}

//predict which class it falls under
int predict(struct GaussianNaiveBayes model, double *x) {
	int maximum_index;
	double maximum_probability;
	double *temp_vector;
	double temp_probability;
	struct MultipleGaussian distributions;
	
	for (int i = 0; i < model.number_distributions; i++) {
		distributions = model.gaussian_list[i];
		temp_vector = get_probabilities(distributions, x);
		temp_probability = overall_probability(temp_vector, model.dimensions);
		free(temp_vector);
		
		if (i == 0 || temp_probability > maximum_probability) {
			maximum_index = i;
			maximum_probability = temp_probability;
		}
	}
	
	return maximum_index;
}

//fit arrays of means and standard deviations given a number of distributions and
//dimensions of those distributions to a Gaussian Naive Bayes classification model
struct GaussianNaiveBayes fit(double **means, double **std_devs, 
							  int dimensions, int number_distributions) {
	struct GaussianNaiveBayes model;
	
	model.dimensions = dimensions;
	model.number_distributions = number_distributions;
	
	struct MultipleGaussian *gaussian_list = malloc((sizeof(double*) + 2*sizeof(int)) * model.number_distributions);
	struct Gaussian *gaussians;
	double *temp_means;
	double *temp_std_devs;
	for (int i = 0; i < model.number_distributions; i++) {
		gaussians = malloc(2 * sizeof(double) * model.dimensions);
		temp_means = means[i];
		temp_std_devs = std_devs[i];
		for (int j = 0; j < model.dimensions; j++) {
			struct Gaussian temp_gaussian = { .mean = temp_means[j], .std_dev = temp_std_devs[j] };
			gaussians[j] = temp_gaussian;
		}
		struct MultipleGaussian multi_gaussian = { .dimensions = dimensions, .gaussians = gaussians };
		gaussian_list[i] = multi_gaussian;
	}
	
	model.gaussian_list = gaussian_list;
	
	return model;
}