/*
Vigenere Encryptor / Decryptor
made with love by Lowenn
for 1st year university programming study program
*/

#include <iostream>
#include <string>

using namespace std;

//Generates the key till 
//it gets the same length as
//original text
string generateKey(string userStr, string keyWord)
{
	int x = userStr.size();

	for (int i = 0; ; i++)
	{
		if (x == i)
			i = 0;
		if (keyWord.size() == userStr.size())
			break;
		keyWord.push_back(keyWord[i]);
	}
	return keyWord;
}

string encrypt()
{
	string userString;
	string keyWord;
	string cryptedText;

	cout << "\n\nEnter your string (without spaces): ";
	cin >> userString;
	cout << "\n\nEnter a keyword for encryptor: ";
	cin >> keyWord;

	string key = generateKey(userString, keyWord);

	for (int i = 0; i < userString.size(); i++)
	{
		int x = (userString[i] + key[i]) % 26; //convert in range 0-25
		x += 'A'; //convert into alphabet (ASCII)

		cryptedText.push_back(x);
	}

	cout << "Encryption Complete: " << cryptedText << endl;

	return cryptedText; 
}

string decrypt()
{
	string cipherString;
	string keyWord;
	string decryptedText;

	cout << "\n\nEnter your crypted text: ";
	cin >> cipherString;
	cout << "\n\nEnter a keyword for decryptor: ";
	cin >> keyWord;

	string key = generateKey(cipherString, keyWord);

	for (int i = 0; i < cipherString.size(); i++)
	{
		int x = (cipherString[i] - key[i] + 26) % 26;
		x += 'A';

		decryptedText.push_back(x);
	}

	cout << "Decryption Complete: " << decryptedText << endl;

	return decryptedText;
}

int main()
{
	char userInput;
	bool mode = false;

	cout << "Welcome to C++ Vigenere Encryptor / Decryptor!\n" << endl;

	cout << "NOTE: This works only with English alphabet!!!" << endl;
	cout << "Please, choose a mode - Encrypt(e) / Decrypt(d): ";
	

	while (mode == !true) {
		
		cin >> userInput;

		if (userInput == 'E' || userInput == 'e')
		{
			encrypt();
			mode = true;
		}
		else if (userInput == 'D' || userInput == 'd')
		{
			decrypt();
			mode = true;
		}
		else
			cout << "Unknown command! Choose either Encrypt(e) or Decrypt(d): ";
	}


	return 0;
}