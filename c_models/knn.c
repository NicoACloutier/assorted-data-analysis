#include<stdio.h>
#include<math.h>
#include<stdlib.h>

//K-NEAREST NEIGHBOR
//initialize  KNearestNeighbor struct and call the classify function with the model and a vector of data to predict

struct KNearestNeighbor {
	double **x; //n by x_length matrix with input data
	double **y; //n by y_length matrix with output data
	int y_length; //number of output variables
	int x_length; //number of input variables
	int n; //number of observations in the dataset
} KNearestNeighbor;

//find the distance between two vectors using the dot product
double vector_distance(double *x, double *y, int length) {
	double sum = 0;
	for (int i = 0; i < length; i++) {
		sum += pow(x[i]-y[i], 2);
	}
	sum = pow(sum, 0.5);
	return sum;
}

//find the closest x-observation in a KNN dataset, return the y-observation
//for this classification
double *classify(struct KNearestNeighbor model, double *x) {
	double minimum;
	double *distance_vector = malloc(model.n * sizeof(double));
	int minimum_index = 0;
	for (int i = 0; i < model.n; i++) {
		double distance = vector_distance(x, model.x[i], model.x_length);
		distance_vector[i] = distance;
		if (i == 0) {
			minimum = distance;
		}
		if (distance < minimum) {
			minimum = distance;
			minimum_index = i;
		}
	}
	
	return model.y[minimum_index];
}
