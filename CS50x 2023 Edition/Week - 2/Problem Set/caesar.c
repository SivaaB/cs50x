#include <cs50.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, string argv[1])
{
    if (argc != 2)
    {
        printf("Usage: /caesar key \n");
        return 1;
    }

    for (int i = 0 ; i < strlen (argv [1]) ; i++)
    {
        if (!isdigit(argv[1][i]))
        {
            printf("Usage: /caesar key \n");
            return 1;
        }
    }

    int k = atoi(argv[1]);

    string plaintext = get_string("Plain Text : ");
    printf("ciphertext: ");

    for (int j = 0 ; j < strlen(plaintext) ; j++)
    {
        if (isupper (plaintext [j]))
        {
            printf("%c", ((plaintext [j] - 65 + k) % 26) + 65);
        }
        else if (islower(plaintext [j]))
        {
            printf("%c", ((plaintext [j] - 97 + k) % 26) + 97);
        }
        else
        {
            printf("%c", plaintext [j]);
        }
    }
    printf("\n");
}