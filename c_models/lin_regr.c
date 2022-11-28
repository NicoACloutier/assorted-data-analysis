#include<stdio.h>
#include<math.h>
#include<stdlib.h>

//LINEAR REGRESSION

struct LinearRegressor {
	int x_vars;
	int y_vars;
	double **coefs;
	double *constants;
};

//find the arithmetic mean of a vector
double mean(double *vector, int n) {
	double sum = 0;
	for (int i = 0; i < n; i++) {
		sum += vector[i];
	}
	double avg = sum / n;
	return avg;
}

//find the linear coefficient between an input and output variable
double coef(double *x, double *y, int n) {
	double x_mean = mean(x, n);
	double y_mean = mean(y, n);
	
	double numerator = 0;
	for (int i = 0; i < n; i++) {
		numerator += (x[i] - x_mean) * (y[i] - y_mean);
	}
	
	double denominator = 0;
	for (int i = 0; i < n; i++) {
		denominator += pow((x[i] - x_mean), 2);
	}
	
	return numerator / denominator;
}

//find all coefficients between input and output variables
double **coefs(double **x, double **y, int x_vars, int y_vars, int n) {
	double **coefs = malloc(sizeof(double*) * y_vars);
	
	for (int i = 0; i < y_vars; i++) {
		double *temp_y = y[i];
		double *temp_coefs = malloc(sizeof(double) * x_vars);
		for (int j = 0; j < x_vars; j++) {
			double *temp_x = x[i];
			double temp_coef = coef(temp_x, temp_y, n);
			temp_coefs[j] = temp_coef;
		}
		coefs[i] = temp_coefs;
	}
	return coefs;
}

//multiply a matrix by a vector
double *matrix_by_vector(double **matrix, double *vector, int rows, int columns) {
	double *return_vector = malloc(sizeof(double) * columns);
	for (int row = 0; row < rows; row++) {
		double *current_row = matrix[row];
		double sum = 0;
		for (int column = 0; column < columns; column++) {
			sum += current_row[column] * vector[column];
		}
		return_vector[row] = sum;
	}
	return return_vector;
}

//find the constant for a single output variable
double constant(double *x_means, double y_mean, double *coefs, int x_vars) {
	double sum = 0;
	for (int i = 0; i < x_vars; i++) {
		sum += coefs[i] * x_means[i];
	}
	return y_mean - sum;
}

//find the constants given input and output means, as well as already-computed coefficients
double *constants(double *x_means, double *y_means, int x_vars, int y_vars, double **coefs) {
	double *constants = malloc(sizeof(double) * y_vars);
	
	for (int i = 0; i < y_vars; i++) {
		double y_mean = y_means[i];
		double *temp_coefs = coefs[i];
		double temp_constant = constant(x_means, y_mean, temp_coefs, x_vars);
		constants[i] = temp_constant;
	}
	return constants;
}
	

//make a prediction from a linear model
double *predict(double *inputs, struct LinearRegressor regressor) {
	double *predictions = malloc(sizeof(double) * regressor.y_vars);
	for (int i = 0; i < regressor.y_vars; i++){
		double sum = 0;
		for (int j = 0; j < regressor.x_vars; j++) {
			sum += inputs[j] * regressor.coefs[i][j];
		}
		predictions[i] = sum;
	}
	return predictions;
}

//fit linear regressor
struct LinearRegressor fit(double **x, double **y, int x_vars, int y_vars, int n) {
	struct LinearRegressor regressor;
	regressor.coefs = coefs(x, y, x_vars, y_vars, n);
	regressor.x_vars = x_vars;
	regressor.y_vars = y_vars;
	
	double *x_means = malloc(sizeof(double) * x_vars);
	for (int i = 0; i < x_vars; i++) {
		x_means[i] = mean(x[i], n);
	}
	
	double *y_means = malloc(sizeof(double) * y_vars);
	for (int i = 0; i < y_vars; i++) {
		y_means[i] = mean(y[i], n);
	}
	
	regressor.constants = constants(x_means, y_means, x_vars, y_vars, regressor.coefs);
	
	return regressor;
}
