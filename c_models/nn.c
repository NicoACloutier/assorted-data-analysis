#include<stdio.h>
#include<stdlib.h>
#include<math.h>

//generate a random length-dimensional vector
double *random_vector(int length) {
	double *vector = malloc(length * sizeof(double));
	for (int i = 0; i < length; i++) {
		double value = rand();
		value *= 2;
		value /= RAND_MAX;
		value--;
		vector[i] = value;
	}
	return vector;
}

//find dot product of two vectors
double dot(double first_vector[], double second_vector[], int length) {
	double sum = 0;
	for (int i = 0; i < length; i++) {
		product = first_vector[i] * second_vector[i];
		sum += product;
	}
	return sum;
}

//add two vectors
double *element_add(double first_vector[], double second_vector[], int length) {
	for (int i = 0; i < length; i++) {
		first_vector[i] += second_vector[i];
	}
	return first_vector;

//scale a vector by a scalar
double *scale(double vector[], int length, double scalar) {
	for (int i = 0; i < length; i++) {
		vector[i] *= scalar;
	}
	return vector;
}