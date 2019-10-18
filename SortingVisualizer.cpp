/*
Made by Lowenn in 2019 for uni 1-year study project
*/

#include <SDL.h>
#include <iostream>
#include <vector>
#include <random>
#include <chrono>

using namespace std;
int s = 300;
vector<int> numbers;
int gap = 4;


void swap(SDL_Renderer* renderer, int i, int j, int x, int y)
{
	// Swapping the first line with the correct line 
	// by making it black again and then draw the pixel 
	// for white color. 
	SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); //RED
	SDL_RenderDrawLine(renderer, i, s, i, s - x);
	SDL_RenderPresent(renderer);

	SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); //BLACK
	SDL_RenderDrawLine(renderer, i, s, i, s - x);
	SDL_RenderPresent(renderer);

	SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255); //WHITE
	SDL_RenderDrawLine(renderer, i, s, i, s - y);
	SDL_RenderPresent(renderer);


	SDL_SetRenderDrawColor(renderer, 255, 0, 0, 255); //RED
	SDL_RenderDrawLine(renderer, j, s, j, s - y);
	SDL_RenderPresent(renderer);

	SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); //BLACK
	SDL_RenderDrawLine(renderer, j, s, j, s - y);
	SDL_RenderPresent(renderer);

	SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255); //WHITE
	SDL_RenderDrawLine(renderer, j, s, j, s - x);
	SDL_RenderPresent(renderer);
}

void stupidSort(SDL_Renderer* renderer)
{
	int i, j, temp;

	for (i = 1; i < s; i++) {
		for (j = 0; j < s - i; j++) {
			if (numbers[j] > numbers[j + 1]) {
				temp = numbers[j];
				numbers[j] = numbers[j + 1];
				numbers[j + 1] = temp;

				swap(renderer, gap * j + 1,
					gap * (j + 1) + 1,
					numbers[j + 1],
					numbers[j]);

				i = 1;
				j = 0;
			}
		}
	}
}

void bubbleSort(SDL_Renderer* renderer)
{
	int i, j, temp;

	for (i = 1; i < s; i++) {
		for (j = 0; j < s - i; j++) {
			if (numbers[j] > numbers[j + 1]) {
				temp = numbers[j];
				numbers[j] = numbers[j + 1];
				numbers[j + 1] = temp;

				swap(renderer, gap * j + 1,
					gap * (j + 1) + 1,
					numbers[j + 1],
					numbers[j]);
			}
		}
	}
}

//TODO: Add more sorters

int main(int argc, char *argv[])
{
	SDL_Init(SDL_INIT_EVERYTHING);

	SDL_Window* window = SDL_CreateWindow("SoVi C++", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 1200, 300, SDL_WINDOW_SHOWN);
	SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, 0);
	
	SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); //setting a black color for renderer
	SDL_RenderClear(renderer);

	SDL_RenderPresent(renderer); //drawing a bg

	for (int i = 1; i <= s; i++)
		numbers.push_back(i);

	//Find a seed and shuffle the array
	unsigned seed = chrono::system_clock::now().time_since_epoch().count();
	shuffle(numbers.begin(), numbers.end(), default_random_engine(seed));

	SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
	for (int i = 1; i <= gap * s; i += gap) {
		SDL_RenderDrawLine(renderer, i, s, i, (s - numbers[i / gap]));
		SDL_RenderPresent(renderer);
	}

	SDL_Delay(3000);
	stupidSort(renderer);
	//bubbleSort(renderer);

	SDL_Delay(5000); //Delay before a window closes

	return 0;
}

