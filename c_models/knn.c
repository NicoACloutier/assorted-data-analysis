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
	int k; //number of neighbors being compared
};

//vector of particular length
struct LengthVector {
	double *values; //the vector itself
	int length; //its length
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

//find the distance between two vectors using the dot product
double vector_distance(double *x, double *y, int length) {
	double sum = 0;
	for (int i = 0; i < length; i++) {
		sum += pow(x[i]-y[i], 2);
	}
	sum = pow(sum, 0.5);
	return sum;
}

//get the index of the maximum value in a vector
int get_max_index(double *vector, int length) {
	int max_index = 0;
	for (int i = 0; i < length; i++) {
		if (vector[i] > vector[max_index]) {
			max_index = i;
		}
	}
	return max_index;
}

//return true if value is not in a vector, false otherwise
int not_occurs_in(double *vector, int length, double value) {
	for (int i = 0; i < length; i++) {
		if (vector[i] == value) {
			return 0;
		}
	}
	return 1;
}

//return only unique values in a vector
struct LengthVector unique(double *vector, int length) {
	
	//find unique values and number of unique values
	int counter = 0;
	double *unique_values = malloc(sizeof(double) * length);
	for (int i = 0; i < length; i++) {
		double value = vector[i];
		if (not_occurs_in(unique_values, length, value)) {
			unique_values[counter] = value;
			counter++;
		}
	}
	
	//create new vector of unique values that is of correct length
	int number_unique = counter+1;
	double *returned_values = malloc(sizeof(double) * number_unique);
	for (int i = 0; i < number_unique; i++) {
		double value = unique_values[i];
		returned_values[i] = value;
	}
	
	//get rid of incorrect length vector
	free(unique_values);
	struct LengthVector return_vector = {returned_values, number_unique};
	
	return return_vector;
}

//find the mode of a vector
double most_common(double *vector, int length) {
	int maximum_count = 0;
	double maximum_value;
	
	struct LengthVector unique_values = unique(vector, length);
	for (int i = 0; i < unique_values.length; i++) {
		int temp_counter = 0;
		double value = unique_values.values[i];
		for (int j = 0; j < length; j++) {
			if (value == vector[j]) {
				temp_counter++;
			}
		}
		if (temp_counter > maximum_count) {
			maximum_count = temp_counter;
			maximum_value = value;
		}
	}
	
	return maximum_value;
}

//find the indices of the k-nearest neighbors
int *find_knearest(struct KNearestNeighbor model, double *x) {
	double *k_neighbors = malloc(sizeof(double) * model.k); //distances of nearest points
	int *k_indeces = malloc(sizeof(int) * model.k); //indeces of nearest points
	double maximum; //maximum distance still within k smallest
	int maximum_index = 0;
	
	//initialize k_neighbors and k_indeces
	for (int i = 0; i < model.k; i++) {
		double distance = vector_distance(x, model.x[i], model.x_length);
		k_neighbors[i] = distance;
		k_indeces[i] = i;
		if (i == 0) {
			maximum = distance;
		}
		if (distance > maximum) {
			maximum = distance;
			maximum_index = i;
		}
	}
	
	//find the indeces of k nearest points
	for (int i = model.k; i < model.n; i++) {
		double distance = vector_distance(x, model.x[i], model.x_length);
		if (distance < maximum) {
			k_neighbors[maximum_index] = distance;
			k_indeces[maximum_index] = i;
			maximum_index = get_max_index(k_neighbors, model.k);
			maximum = k_neighbors[maximum_index];
		}
	}
	free(k_neighbors);
	
	return k_indeces;
}

//find the closest x-observation in a KNN dataset, return the y-observation
//for this classification
double *classify(struct KNearestNeighbor model, double *x) {
	int *k_indeces = find_knearest(model, x);
	
	//find the most common occurence for each output dimension
	double prediction;
	int index;
	double *predictions = malloc(sizeof(double) * model.y_length);
	for (int i = 0; i < model.y_length; i++) {
		double *occurences = malloc(sizeof(double) * model.k);
		for (int j = 0; j < model.k; j++) {
			index = k_indeces[j];
			occurences[j] = model.y[index][i];
		}
		prediction = most_common(occurences, model.k);
		predictions[i] = prediction;
		
		free(occurences);
	}
	
	free(k_indeces);
	
	return predictions;
}

//perform k-nearest regression
double *regress(struct KNearestNeighbor model, double *x) {
	int *k_indeces = find_knearest(model, x);
	
	//find the most common occurence for each output dimension
	double prediction;
	int index;
	double *predictions = malloc(sizeof(double) * model.y_length);
	for (int i = 0; i < model.y_length; i++) {
		double *occurences = malloc(sizeof(double) * model.k);
		for (int j = 0; j < model.k; j++) {
			index = k_indeces[j];
			occurences[j] = model.y[index][i];
		}
		prediction = mean(occurences, model.k);
		predictions[i] = prediction;
		
		free(occurences);
	}
	
	free(k_indeces);
	
	return predictions;
	
}
