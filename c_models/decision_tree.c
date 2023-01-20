#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<float.h>

//DECISION TREE REGRESSOR (unfinished)

//a node of a DecisionTree
struct Node {
	int dimension; //the dimension this Node's condition exists on. If it is a return node, this is -1.
	double compare_value; //the value used as the center of comparison
	struct Node *greater_pointer; //pointer to next node if the x value is greater than compare_value, only important if not a return node
	struct Node *less_pointer; //pointer to next node if the x value is less than compare_value, only important if not a return node
	double *return_value; //the return value of this node, only important if it is a return node.
	int return_length; //the number of dimensions on the return value
	int minimum_observations;
};

struct DecisionTree {
	int minimum_observations; //maximum number of observations in a split before ending recursion
	struct Node *first_node; //pointer to first node
};

//a masked dataset, which has information on which observations in a dataset should be ignored.
//This allows different leaves of a decision tree that each have different observations applying to them
//to share the same double pointer to the dataset.
struct MaskedDataset {
	int *mask_list; //list of 1s if it should be payed attention to, 0s if it shouldn't, length `n`
	int n; //number of observations
	int remaining; //number of unmasked observations
	double **x; //the dataset itself (in full)
	int dimensions; //number of dimensions
};

//navigate through a tree of nodes
double *navigate_nodes(struct Node current_node, double *x, int length) {
	//if this is a return node, return its return value
	if (current_node.dimension == -1) {
		return current_node.return_value;
	}
	
	double current_value = x[current_node.dimension]; //get the value on this node's compare dimension
	if (current_value > current_node.compare_value) {
		navigate_nodes(*current_node.greater_pointer, x, length); //navigate to the next greater node if greater
	}
	else {
		navigate_nodes(*current_node.less_pointer, x, length); //navigate to the next less node if less
	}
}

//get the mean value in a vector
double dimension_mean(struct MaskedDataset input, int dimension) {
	double avg = 0;
	for (int i = 0; i < input.n; i++) {
		if (x.mask_list[i]) {
			avg += input.x[i][dimension];
		}
	}
	avg /= input.n;
	return avg;
}

//navigate through a tree
double *navigate_tree(struct DecisionTree model, double *x, int length) {
	return navigate_nodes(*model.first_node, x, length);
}

//return the variance of the dataset within a particular dimension multiplied by the count
double find_count_variance(double compare_value, int dimension, struct MaskedDataset input) {
	double sum = 0; //sum of all point values
	double sqrsum = 0; //sum of square point values
	
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list[i]) {
			sum += input.x[i][dimension];
			sqrsum += pow(input.x[i][dimension], 2);
		}
	}
	
	double variance = (sqrsum - (pow(sum, 2)/input.remaining));
	
	return variance;
}

//checks if every unmasked value in a masked dataset is equivalent to every other
int is_the_same(struct MaskedDataset input) {
	double **subset = malloc(sizeof(double*) * input.remaining);
	int subset_index = 0;
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list[i]) {
			subset[subset_index] = input.x[i];
			subset_index++;
		}
	}
	
	for (int i = 1; i < input.remaining; i++) {
		for (int j = 0; j < input.dimensions; j++) {
			if (subset[i][j] != subset[i-1][j]) {
				free(subset);
				return 0;
			}
		}
	}
	
	free(subset);
	return 1;
}

//copy the return length and minimum observations of a node to another newly initialized one
struct Node copy_node(struct Node to_copy) {
	struct Node return_node;
	return_node.return_length = to_copy.return_length;
	return_node.minimum_observations = to_copy.minimum_observations;
	return return_node;
}

//find the return vector of a node with an output dataset
struct Node *get_return_vector(struct Node node, struct MaskedDataset output) {
	double *output_vector = malloc(sizeof(double) * output.dimensions);
	for (int i = 0; i < output.dimensions; i++) {
		output_vector[i] = dimension_mean(output, i);
	}
	
	node.dimension = -1;
	node.return_value = output_vector;
	free(output.mask_list);
	return &node;
}

//get the dimension of a dataset that has the highest variance
//(among unmasked values)
int get_maximum_variance_dimension(struct MaskedDataset input) {
	double temp_mean;
	double temp_var;
	
	double maximum_variance = 0;
	int maximum_var_dimension;
	
	//find the best split (test for maximum variance multiplied by remaining values for each dimension mean as a compare value)
	for (int i = 0; i < input.dimensions; i++) {
		temp_mean = dimension_mean(input, i);
		temp_var = find_count_variance(temp_mean, i, input);
		
		if (temp_var > maximum_variance) {
			maximum_variance = temp_var;
			maximum_var_dimension = i;
		}
	}

	return maximum_var_dimension;
}

struct MaskedDataset change_mask_list(struct MaskedDataset input, double compare_value, int greater) {
	int *mask_list = malloc(sizeof(int) * input.n);
	
	struct MaskedDataset return_dataset;
	return_dataset.n = input.n;
	return_dataset.x = input.x;
	return_dataset.dimensions = input.dimensions;
	
	int remaining;
	int is_greater;
	
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list) {
			is_greater = (input.x[i][compare_value] > maximum_var_mean);
			mask_list[i] = (greater) ? is_greater : !is_greater;
			remaining += (greater) ? is_greater : !is_greater;
		}
		else {
			mask_list[i] = 0;
		}
	}
	
	return_dataset.mask_list = mask_list;
	return_dataset.remaining = remaining;
	
	return return_dataset;
}

//Fit a particular node (get its compare value and dimension).
//Node should already have specifications for the dimensions of the return vector and the minimum observations for stopping.
//Recurse until a stopping condition is met,
//Conditions: a certain number or less of datapoints remain, or all datapoint inputs are equal to each other
//When a stopping condition is met, get the return vector for the node, and return pointer to it.
//Overall, function returns a pointer to the first node that contains pointers to the next two, etc.
struct Node *best_fit(struct Node node, struct MaskedDataset input, struct MaskedDataset output) {
	if ((input.remaining <= node.minimum_observations) || (is_the_same(input))) {
		free(input.mask_list);
		return get_return_vector(node, output); //output mask list gets freed in the function
	}
	
	int maximum_var_dimension = get_maximum_variance_dimension(input);
	double maximum_var_mean = dimension_mean(input, maximum_var_dimension);
	
	node.dimension = maximum_var_dimension;
	node.compare_value = maximum_var_mean;
	
	//Declare masked datasets (the function makes a copy of the dataset with an updated mask list)
	struct MaskedDataset greater_input = change_mask_list(input, maximum_var_mean, 1);
	struct MaskedDataset less_input = change_mask_list(input, maximum_var_mean, 0);
	struct MaskedDataset greater_output = change_mask_list(output, maximum_var_mean, 1);
	struct MaskedDataset less_output = change_mask_list(output, maximum_var_mean, 0);
	
	node.greater_pointer = best_fit(copy_node(node), greater_input, greater_output);
	node.less_pointer = best_fit(copy_node(node), less_input, less_output);
	
	free(input.mask_list);
	free(output.mask_list);
	return &node;
}

//fit a Decision Tree model
struct DecisionTree fit(double **x, int x_length, double **y, int y_length, 
						int n, int minimum_observations) {
	
	//initialize a mask list where no values are masked
	int *ones = malloc(sizeof(int) * n);
	for (int i = 0; i < n; i++) {
		ones[i] = 1;
	}
	
	struct MaskedDataset input = {.mask_list = ones, .n = n, .remaining = n, .x = x, .dimensions = x_length};
	struct MaskedDataset output = {.mask_list = ones, .n = n, .remaining = n, .x = y, .dimensions = y_length};
	
	struct Node first_node;
	first_node.return_length = y_length;
	first_node.minimum_observations = minimum_observations;
	
	struct DecisionTree model = {.minimum_observations = minimum_observations,
								 .first_node = best_fit(first_node, input, output)};
	
	return model;
}