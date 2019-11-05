#include <iostream>
#include <random>

using namespace std;

int main()
{
	int playerAmount, totalMatches = 0;
	bool lastTurn = true;

	while(totalMatches < 100)
	{	
		cout << "\nTotal Score: " << totalMatches << endl;
		cout << "\nYour turn(from 1 to 10): ";
		while (true)
		{
			cin >> playerAmount;
			if (playerAmount > 10 || playerAmount <= 0)
				cout << "Only from 1 to 10: ";
			else
				break;
		}
		totalMatches += playerAmount;
		lastTurn = true;

		if (totalMatches >= 100)
			break;

		playerAmount = rand() % 10 + 1;
		totalMatches += playerAmount;
		cout << "Bot turn: " << playerAmount << endl;
		lastTurn = false;
	}

	if (lastTurn)
		cout << "\n\nPlayer wins!";
	else
		cout << "\n\nBot wins!";

	return 0;
}

