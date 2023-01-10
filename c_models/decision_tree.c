#include<stdio.h>
#include<stdlib.h>
#include<math.h>

//DECISION TREE REGRESSOR (unfinished)

//a node of a DecisionTree
struct Node {
	int dimension; //the dimension this Node's condition exists on. If it is a return node, this is -1.
	double compare_value; //the value used as the center of comparison
	struct Node *greater_pointer; //pointer to next node if the x value is greater than compare_value, only important if not a return node
	struct Node *less_pointer; //pointer to next node if the x value is less than compare_value, only important if not a return node
	double *return_value; //the return value of this node, only important if it is a return node.
	int return_length; //the number of dimensions on the return value
};

struct DecisionTree {
	int number_observations; //maximum number of observations in a split before ending recursion
	struct Node *first_node; //pointer to first node
};

//navigate through a tree of nodes
double *navigate_nodes(struct Node current_node, double *x, int length) {
	//if this is a return node, return its return value
	if (current_node.dimension == -1) {
		return current_node.return_value;
	}
	
	double current_value = x[current_node.dimension]; //get the value on this node's compare dimension
	if (current_value > current_node.compare_value) {
		navigate_nodes(&current_node.greater_pointer, x, length); //navigate to the next greater node if greater
	}
	else {
		navigate_nodes(&current_node.less_pointer, x, length); //navigate to the next less node if less
	}
}

//navigate through a tree
double *navigate_tree(struct DecisionTree model, double *x, int length) {
	return navigate_nodes(&model.first_node, x, length);
}