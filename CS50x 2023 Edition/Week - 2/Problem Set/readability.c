#include <cs50.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    string s = get_string("Sentence: ");

    int Letters = 0;
    int Words = 1;
    int Sentences = 0;
    int grade;

    for (int i = 0 ; i < strlen(s) ; i++)
    {

        if (s[i] == ' ')
        {
            Words++ ;
        }
        else if (isalpha(s[i]))
        {
            Letters++ ;
        }
        else if (s[i] == '.' || s[i] == '!' || s[i] == '?')
        {
            Sentences++ ;
        }
    }

    float L = ((float) Letters) / ((float) Words) * 100;
    float S = ((float) Sentences) / ((float) Words) * 100;
    grade = round((0.0588 * L) - (0.296 * S) - 15.8);

    if (grade < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (grade > 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %d\n", grade);
    }



}