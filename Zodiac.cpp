#include <iostream>

using namespace std;


int main()
{
	int day, month;

	cout << "Enter month and day of your birth \n" << endl;

	while (true)
	{
		cout << "Month: ";
		cin >> month;
		if (month > 12)
			cout << "Month is out of the year range! Please, try again! ";
		else
			break;
	}

	while (true)
	{
		cout << "Day: ";
		cin >> day;
		if (day > 31 || month == 2 && day > 28)
			cout << "Day is out of month range! Please, try again! ";
		else
			break;
	}

	//Copied from stackoverflow because lazy :^)
	if ((month == 3 && day >= 21) || (month == 4 && day <= 19))
		cout << "You Are an Aries! \n";
	else if ((month == 4 && day >= 20) || (month == 4 && day <= 20))
		cout << "You Are an Taurus! \n";
	else if ((month == 5 && day >= 21) || (month == 6 && day <= 21))
		cout << "You Are an Gemini! \n";
	else if ((month == 6 && day >= 22) || (month == 7 && day <= 22))
		cout << "You Are an Cancer! \n";
	else if ((month == 7 && day >= 23) || (month == 8 && day <= 22))
		cout << "You Are an Leo! \n";
	else if ((month == 8 && day >= 23) || (month == 9 && day <= 22))
		cout << "You Are an Virgo! \n";
	else if ((month == 9 && day >= 23) || (month == 10 && day <= 22))
		cout << "You Are an Libra! \n";
	else if ((month == 10 && day >= 23) || (month == 11 && day <= 21))
		cout << "You Are an Scorpio! \n";
	else if ((month == 11 && day >= 22) || (month == 12 && day <= 21))
		cout << "You Are an Saggitarius! \n";
	else if ((month == 12 && day >= 22) || (month == 1 && day <= 19))
		cout << "You Are an Capricorn! \n";
	else if ((month == 1 && day >= 20) || (month == 2 && day <= 18))
		cout << "You Are an Aquarius! \n";
	else if ((month == 2 && day >= 19) || (month == 3 && day <= 20))
		cout << "You Are an Pisces! \n";


	return 0;
}
