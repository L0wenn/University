#include <iostream>

using namespace std;


void holeAndBrick() //task 6
{
	float holeA, holeB, brickX, brickY, brickZ;

	cout << "Enter hole size A and B: ";
	cin >> holeA;
	cin >> holeB;
	cout << "Enter size of a brick X, Y and Z: ";
	cin >> brickX;
	cin >> brickY;
	cin >> brickZ;

	if (holeB > brickX && holeA > brickZ)
	{
		if (holeB > brickX && holeA > brickY)
		{
			if (holeB > brickY && holeA > brickX)
				cout << "The brick fits into the hole!";
		}
	}
	else
		cout << "The brick doesn't fit into the hole!";
}


void ascendingOrder() //task 7
{
	int arr[3];
	int temp;

	cout << "Enter A, B and C numbers: ";
	for (int i = 0; i < 3; i++)
		cin >> arr[i];


	for (int i = 1; i < 3; i++) { //Bubble sort
		for (int j = 0; j < 3 - i; j++) {
			if (arr[j] > arr[j + 1]) {
				temp = arr[j];
				arr[j] = arr[j + 1];
				arr[j + 1] = temp;
			}
		}
	}

	cout << "\n\nSorted array: ";
	for (int i = 0; i < 3; i++)
		cout << " " << arr[i];
}


void numberToWord() //task 12
{
	int num;
	const string teens[] = { "one", "two" , "three", "four", "five", "six", "seven", "eight", "nine" };
	const string specialCases[] = { "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen" };
	const string tens[] = {"twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninety"};

	cout << "Enter any number from 100 to 999: ";
	cin >> num;

	if (num > 999 || num < 100)
		throw "unsuported";


	if (num % 10 == 0)
		cout << teens[num / 100 - 1] << " hundred " << tens[num % 100 / 10 - 2];
	else
		if (num % 100 >= 10 && num % 100 <= 19)
			cout << teens[num / 100 - 1] << " hundred " << specialCases[num % 100 - 10];
		else
			cout << teens[num / 100 - 1] << " hundred " << tens[num % 100 / 10 - 2] << " " << teens[num % 10 - 1];
}


void ageToWords() //task 19
{
	setlocale(LC_ALL, "Russian");

	int age;
	const string teens[] = {"один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"};
	const string tens[] = {"Двадцать", "Тридцать", "Сорок", "Пятьдесят", "Шестьдесят"};
	const string ageWord[] = { "год", "года", "лет" };

	cout << "Ваш возраст: ";
	cin >> age;

	if (age > 69 || age < 20)
		throw "unsuported";

	if (age % 10 == 0)
		cout << tens[age / 10 - 2];
	else
	{	

		if ((age % 10) == 1)
			cout << tens[age / 10 - 2] << " " << teens[age % 10 - 1] << " " << ageWord[0];
		else if ((age % 10) > 1 && (age % 10) < 5)
			cout << tens[age / 10 - 2] << " " << teens[age % 10 - 1] << " " << ageWord[1];
		else
			cout << tens[age / 10 - 2] << " " << teens[age % 10 - 1] << " " << ageWord[2];
	}
		
}


int main()
{
	//holeAndBrick();
	//ascendingOrder();
	//numberToWord();
	//ageToWords();
	return 0;
}
