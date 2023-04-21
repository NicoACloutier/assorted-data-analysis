#include<stdlib.h>
#include<stdio.h>
#include<math.h>

//PRINCIPAL COMPONENT ANALYSIS (unfinished)

typedef struct Matrix {
	int n;
	int dimensions;
	double **data;
} Matrix;

typedef struct Vector {
	int dimensions;
	double *data;
} Vector;

typedef struct QRDecomposition {
	Matrix a;
	Matrix q;
	Matrix r;
} QRDecomposition;

//multiply two matrices, return new matrix
Matrix multiply_matrices(Matrix matrix1, Matrix matrix2) {
	Matrix output;
	output.n = matrix1.n;
	output.dimensions = matrix2.dimensions;
	
	output.data = malloc(sizeof(double*) * output.n);
	for (int i = 0; i < output.n; i++) {
		for (int j = 0; j < output.dimensions; j++) {
			double row = 0;
			for (int k = 0; k < matrix1.dimensions; k++) { row += matrix1.data[i][k] * matrix2.data[k][j]; }
			output.data[i][j] = row;
		}
	}
	return output;
}

//copy a matrix
Matrix copy_matrix(Matrix to_copy) {
	Matrix output;
	output.n = to_copy.n;
	output.dimensions = to_copy.dimensions;
	output.data = malloc(sizeof(double*) * output.n);
	for (int i = 0; i < output.n; i++) {
		for (int j = 0; j < output.dimensions; j++) { output.data[i][j] = to_copy.data[i][j]; }
	}
	return output;
}

//multiply pointer vectors given a dimension using dot product
double dot(Vector vector1, Vector vector2) {
	double sum = 0;
	for (int i = 0; i < vector1.dimensions; i++) {
		sum += vector1.data[i] * vector2.data[i];
	}
	return sum;
}

//make a vector of zeros with `number` dimensions
Vector zeros(int number) {
	Vector vector;
	vector.dimensions = number;
	vector.data = malloc(sizeof(double) * number);
	for (int i = 0; i < number; i++) { vector.data[i] = 0; }
	return vector
}

//get a row of a matrix (does not malloc)
Vector get_row(Matrix matrix, int row_num) {
	Vector output;
	output.dimensions = matrix.dimensions;
	output.data = matrix.data[row_num];
	return output;
}

//get a column of a matrix (does malloc)
Vector get_column(Matrix matrix, int column_num) {
	Vector output;
	output.dimensions = matrix.n;
	output.data = malloc(sizeof(double*) * matrix.n);
	for (int i = 0; i < matrix.n; i++) {
		output.data[i] = matrix.data[i][column_num];
	}
	return output;
}

//free a matrix
void free_matrix(Matrix to_free) {
	for (int i = 0; i < to_free.n; i++) {
		free(to_free.data[i]);
	}
}

//free a vector
void free_vector(Vector to_free) {
	free(to_free.data)
}

//scale a vector in place
void scale_in_place(Vector to_scale, double scalar) {
	for (int i = 0; i < to_scale.dimensions; i++) {
		to_scale.data[i] *= scalar;
	}
}

//subtract to_subtract from initial in-place
void subtract_in_place(Vector initial, Vector to_subtract) {
	for (int i = 0; i < initial.dimensions; i++) {
		initial.data[i] -= to_subtract.data[i];
	}
}

void subtract_matrix_in_place(Matrix initial, Matrix to_subtract) {
	for (int i = 0; i < initial.n; i++) {
		for (int j = 0; j < initial.dimensions; j++) { initial.data[i][j] -= to_subtract.data[i][j]; }
	}
}

//multiply a matrix by another in-place
void multiply_in_place(Matrix initial, Matrix to_multiply) {
	for (int i = 0; i < initial.n; i++) {
		for (int j = 0; j < initial.dimensions; j++) {
			double row = 0;
			for (int k = 0; k < initial.dimensions; k++) { row += initial.data[i][k] * to_multiply.data[k][j]; }
			intial.data[i][j] = row;
		}
	}
}

//multiply matrix by scalar in place
void multiply_by_scalar_in_place(Matrix matrix, double scalar) {
	for (int i = 0; i < matrix.n; i++) {
		for (int j = 0; j < matrix.dimensions; j++) { matrix.data[i][j] *= scalar; }
	}
}

//return number by number square matrix with one on diagonals, 0 elsewhere
Matrix eye(int number) {
	Matrix output;
	output.n = number;
	output.dimensions = number;
	output.data = malloc(sizeof(double*) * number);
	for (int i = 0; i < number; i++) {
		for (int j = 0; j < number; j++) {
			output.data[i][j] = (i==j);
		}
	}
	return output;
}

//decompose a matrix into Q*R
QRDecomposition qr_decompose(Matrix to_decompose) {
	QRDecomposition qr;
	Matrix q = copy_matrix(to_decompose);
	
	Matrix r;
	r.n = to_decompose.n;
	r.dimensions = to_decompose.dimensions;
	r.data = malloc(sizeof(double*) * r.n);
	
	for (int i = 0; i < to_decompose.dimensions; i++) {
		Vector to_decompose_i = get_column(to_decompose, i);
		for (int j = 0; j < i; j++) {
			Vector to_decompose_vec = get_row(to_decompose, i);
			Vector q_vec = get_row(q, j);
			r.data[i][j] = dot(to_decompose_vec, q_vec);
			
			Vector q_j = get_column(q, j);
			scale_in_place(q_j, r.data[i][j]);
			subtract_in_place(to_decompose_i, q_j);
			free_vector(q_j);
		}
		
		for (int j = 0; j < q.dimensions; j++) {
			q.data[j][i] = to_decompose_i.data[k];
		}
		Vector q_i = get_row(q, i);
		double magnitude = pow(dot(q_i, q_i), 0.5);
		scale_in_place(q_i, 1/magnitude);
		r.data[i][i] = magnitude;
		free_vector(to_decompose_i);
	}
	
	qr.a = to_decompose;
	qr.q = q;
	qr.r = r;
	
	return qr;
}

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

//find eigenvalues of matrix using qr decomposition
Vector find_eigenvalues(Matrix matrix, int iterations) {
	Matrix qq = eye(matrix.n);
	for (int i = 0; i < iterations; i++) {
		QRDecomposition decomposition = qr_decompose(temp_matrix);
		multiply_in_place(qq, decomposition.q);
	}
	
	Vector eigenvalues;
	eigenvalues.dimensions = qq.n;
	eigenvalues.data = malloc(sizeof(double*) * qq.n);
	for (int i = 0; i < eigenvalues.dimensions; i++) {
		eigenvalues.data[i] = qq.data[i][i];
	}
	
	free_matrix(qq);
	free_matrix(decomposition.q);
	free_matrix(decomposition.r);
	return eigenvalues;
}

//solve a linear equation with matrix and vector
Vector solve_linear(Matrix matrix, Vector vector) {
	Vector output;
	output.dimensions = vector.dimensions;
	output.data = malloc(sizeof(double*) * output.dimensions);
	
	for (int i = 0; i < vector.dimensions; i++) {
		output.data[i] = vector.data[i];
		for (int j = 0; j < i; j++) { output.data[i] -= matrix.data[i][j] * output.data[j]; }
		output.data[i] /= matrix.data[i][i]; //does not work if 0 on diagonal
	}
}

//solve the linear systems to get eigenvectors
Vector *find_eigenvectors(Matrix matrix, Vector eigenvalues) {
	Vector *eigenvectors = malloc(sizeof(Vector) * eigenvalues.dimensions);
	Vector zero_vector = zeros(matrix.n);
	
	for (int i = 0; i < eigenvalues.dimensions; i++) {
		Matrix temp_matrix = copy_matrix(matrix);
		Matrix id_matrix = eye(matrix.n);
		
		double eigenvalue = eigenvalues.data[i];
		multiply_by_scalar_in_place(id_matrix, eigenvalue);
		subtract_matrix_in_place(temp_matrix, id_matrix);
		
		eigenvectors[i] = solve_linear(temp_matrix, zero_vector);
	}
	
	free(zero_vector);
	return eigenvectors;
}