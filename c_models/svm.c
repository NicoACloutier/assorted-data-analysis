#include<stdio.h>
#include<stdlib.h>
#include<math.h>

//SUPPORT VECTOR MACHINE (in progress)

struct SupportVectorMachine {
	double *coefs; //coefficients of the hyperplane with respect to each input variable
	double constant; //constant added to the hyperplane
}

//get the dot product of two length-dimensional vectors
double dot(double *vector1, double *vector2, int length) {
	double sum = 0;
	for (int i = 0; i < length; i++) {
		sum += vector1[i] * vector2[i];
	}
	return sum;
}

//scale a vector by a scalar
double *scale(double *vector, int length, double scalar) {
	for (int i = 0; i < length; i++) {
		vector[i] *= scalar;
	}
	return vector;
}

//return the magnitude of a vector
double pythagorean(double *vector, int length) {
	double sum = 0;
	for (int i = 0; i < length; i++) {
		sum += pow(vector[i], 2);
	}
	sum = pow(sum, 0.5);
	return sum;
}

//normalize a vector, keeping only its direction information
double *normalize(double *vector, int length) {
	double magnitude = pythagorean(vector, length);
	vector = scale(vector, length, 1/magnitude);
	return vector;
}

struct SupportVectorMachine fit() {
	
}