#include <iostream>

using namespace std;


int euclid(int a, int b)
{
	if (a == 0)
		return b;

	return euclid(b % a, a);
}

int main()
{
	int a, b;

	cout << "A int: ";
	cin >> a;
	cout << "B int: ";
	cin >> b;

	int gcd = euclid(a, b);
	cout << "GCD: " << gcd;

	return 0;
}