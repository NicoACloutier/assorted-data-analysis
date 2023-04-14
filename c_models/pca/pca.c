#include<stdlib.h>
#include<stdio.h>
#include<math.h>

//PRINCIPAL COMPONENT ANALYSIS

typedef struct Matrix {
	int n;
	int dimensions;
	double **data;
} Matrix;

typedef struct Vector {
	int dimensions;
	double *data;
} Vector;

//find mean data along a certain dimension
double dimension_mean(Matrix matrix, int dimension) {
	double mean = 0;
	for (int i = 0; i < matrix.n; i++) {
		mean += matrix.data[i][dimension];
	}
	mean /= matrix.n;
}

//find the standard deviation of a particular dimension
double dimension_std(Matrix matrix, int dimension, double mean) {
	double std = 0;
	for (int i = 0; i < matrix.n; i++) {
		std += matrix.data[i][dimension] - mean;
	}
	std /= matrix.n-1;
	return std;
}

//normalize a dimension of a matrix in-place
void normalize_dimension(Matrix matrix, int dimension) {
	double mean = dimension_mean(matrix, dimension);
	double std = dimension_std(matrix, dimension, mean);
	for (int i = 0; i < matrix.n; i++) {
		matrix.data[i][dimension] -= mean;
		matrix.data[i][dimension] /= std;
	}
}

//normalize every dimension of a matrix
void normalize_matrix(Matrix matrix) {
	for (int i = 0; i < matrix.dimensions; i++) {
		normalize_dimension(matrix, i);
	}
}

//find the covariance between two dimensions of a matrix
double find_covariance(Matrix matrix, int dimension1; int dimension2; double mean1; double mean2;) {
	double covariance = 0;
	for (int = 0; i < matrix.n; i++) {
		double temp_term = matrix.data[i][dimension1];
		temp_term *= matrix.data[i][dimension2];
		covariance += temp_term;
	}
	covariance /= matrix.n-1;
	return covariance
}

//find the covariance matrix of a matrix
Matrix find_cov_matrix(Matrix matrix){
	//find means
	double *means = malloc(sizeof(double) * matrix.dimensions);
	for (int i = 0; i < matrix.dimensions; i++) {
		means[i] = dimension_mean(matrix, i);
	}
	
	Matrix cov;
	cov.dimensions = matrix.dimensions;
	cov.n = matrix.dimensions;
	cov.data = malloc(sizeof(double*) * cov.n);
	for (int i = 0; i < cov.dimensions; i++) {
		for (int j = 0; j < cov.dimensions; j++) {
			cov.data[i][j] = find_covariance(matrix, i, j, means[i], means[j]);
		}
	}
	
	return cov;
}

Vector find_eigenvalues(Matrix matrix) {}
Vector *find_eigenvectors(Matrix matrix, Vector eigenvalues) {}