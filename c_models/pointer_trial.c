#include<stdio.h>
#include<stdlib.h>

int main() {
	
	int new_array[2][3] = {{1, 2, 3}, {4, 5, 6}};
	int* pointer_array = new_array[0];
	int **double_pointer_array = malloc(sizeof(int*) * 2);
	
	for (int i = 0; i < 3; i++) {
		printf("%d,", pointer_array[i]);
		double_pointer_array[i] = new_array[i];
	}
	printf("\n");
	
	for (int i = 0; i < 2; i++) {
		for (int j = 0; j < 3; j++) {
			printf("%d,", double_pointer_array[i][j]);
		}
		printf("\n");
	}
	
	
	return 0;
} 
