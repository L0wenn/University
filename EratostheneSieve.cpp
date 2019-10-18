#include <iostream>

using namespace std;

int main()
{
	bool arr[31];

	for (size_t i = 0; i < 31; i++)
		arr[i] = true; //initialize an array with all true entries

	for (int j = 2; j * j <= 30; j++)
	{
		if (arr[j] == true) //if arr[j] not changed, then it's prime
		{
			for (int p = j * 2; p <= 30; p += j)
				arr[p] = false; //updade all multiples of j
		}
	}

	//printing all primes
	for (int i = 2; i <= 30; i++)
	{
		if (arr[i])
			cout << i << " ";
	}

	return 0;
}