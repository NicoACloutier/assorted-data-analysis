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

//return the sum of the variances multiplied by the count of two prospective leaves
double find_count_variance(double compare_value, int dimension, struct MaskedDataset input) {
	int under_count = 0; //number of points over the compare value
	double under_sum = 0; //sum of all point values in this dimension for points above compare value
	double under_sqrsum = 0; //sum of square point values of above
	
	int over_count = 0; //number of points under
	double over_sum = 0; //the sum of points under in this dimension
	double under_sqrsum = 0; //sum of square points under in this dimension
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list[i]) {
			if (input.x[i][dimension] > compare_value) {
				over_count++;
				over_sum += input.x[i][dimension];
				over_sqrsum += pow(input.x[i][dimension], 2);
			}
			else {
				under_count++;
				under_sum += input.x[i][dimension];
				under_sqrsum += pow(input.x[i][dimension], 2);
			}
		}
	}
	
	double under_var = (under_sqrsum - (pow(under_sum, 2)/under_count)); //the variance of points under the compare value multiplied by the count
	double over_var = (over_sqrsum - (pow(over_sum, 2)/over_count)); //the variance of points over the compare value multiplied by the count
	
	return over_var + under_var;
}

//checks if every unmasked value in a masked dataset is equivalent to every other
int is_the_same(struct MaskedDataset input) {
	double **subset = malloc(sizeof(double*) * input.remaining);
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list[i]) {subset[i] = input.x[i];}
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

//fit a particular node. If the number of observations left that fall under that node is greater
//than the minimum observations previously specified in the fit function, make two new nodes,
//one if it is greater than a compare value and one if it is less. keep going until the minimum
//number has been reached. At that point, find the mean y-value on each dimension and put it as the
//return value on a return node. (These nodes will have a dimension of -1).
struct Node *best_fit(struct Node node, struct MaskDataset input, struct MaskDataset output) {
	if ((input.remaining <= node.minimum_observations) || (is_the_same(input))) {
		double *output_vector = malloc(sizeof(double) * output.dimensions);
		for (int i = 0; i < output.dimensions; i++) {
			output_vector[i] = dimension_mean(output, i);
		}
		
		node.dimension = -1;
		node.return_value = output_vector;
		free(input.mask_list);
		free(output.mask_list);
		return &node;
	}
	
	double temp_mean;
	double temp_var;
	
	double minimum_variance = DBL_MAX;
	double minimum_mean;
	int minimum_dimension;
	
	//find the best split (test for minimum variance multiplied by remaining values for each dimension mean as a compare value)
	for (int i = 0; i < input.dimensions; i++) {
		temp_mean = dimension_mean(input, i);
		temp_var = find_count_variance(temp_mean, i, input);
		
		if (temp_var < minimum_variance) {
			minimum_variance = temp_var;
			minimum_mean = temp_mean;
			minimum_dimension = i;
		}
	}
	
	int *greater_mask_list = malloc(sizeof(int) * input.n);
	int *less_mask_list = malloc(sizeof(int) * input.n);
	
	int greater_remaining;
	int less_remaining;
	
	for (int i = 0; i < input.n; i++) {
		if (input.mask_list) {
			greater_mask_list[i] = (input.x[i][minimum_dimension]);
			greater_remaining += (input.x[i][minimum_dimension]);
			
			less_mask_list[i] = !(input.x[i][minimum_dimension]);
			less_remaining += !(input.x[i][minimum_dimension]);
		}
		else {
			greater_mask_list[i] = 0;
			less_mask_list[i] = 0;
		}
	}
	
	node.dimension = minimum_dimension;
	node.compare_value = minimum_mean;
	
	//Declare masked datasets
	
	struct MaskedDataset greater_input = {.mask_list = greater_mask_list, .n = input.n, 
										  .remaining = greater_remaining, .x = input.x, 
										  .dimensions = input.dimensions};
	
	struct MaskedDataset less_input = {.mask_list = less_mask_list, .n = input.n, 
									   .remaining = less_remaining, .x = input.x, 
									   .dimensions = input.dimensions};
	
	struct MaskedDataset greater_output = {.mask_list = greater_mask_list, .n = output.n, 
										   .remaining = greater_remaining, .x = output.x, 
										   .dimensions = output.dimensions};
	
	struct MaskedDataset less_output = {.mask_list = less_mask_list, .n = output.n, 
										.remaining = less_remaining, .x = output.x, 
										.dimensions = output.dimensions};
	
	struct Node greater_node;
	greater_node.return_length = node.return_length;
	greater_node.minimum_observations = node.minimum_observations;
	node.greater_pointer = best_fit(greater_node, greater_input, greater_output);
	
	struct Node less_node;
	less_node.return_length = node.return_length;
	less_node.minimum_observations = node.minimum_observations;
	node.less_pointer = best_fit(less_node, less_input, less_output);
	
	free(input.mask_list);
	free(output.mask_list);
	return &node;
}

//fit a Decision Tree model
struct DecisionTree fit(double **x, int x_length, double **y, int y_length, 
						int n, int minimum_observations) {
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