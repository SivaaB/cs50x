#include <cs50.h>
#include <stdio.h>
#include <math.h>


int main(void)
{
    int Ilamas_Start;
    int Ilamas_End;
    int n = 0;

    // TODO: Prompt for start size
    do
    {
        Ilamas_Start = get_float("Number of Ilamas initially : ");
    }
    while (Ilamas_Start <= 8);

    // TODO: Prompt for end size
    do
    {
        Ilamas_End = get_float("Number of Ilamas at the end: ");
    }
    while (Ilamas_End < Ilamas_Start);

    // TODO: Calculate number of years until we reach threshold
        do
        {
            Ilamas_Start = Ilamas_Start + (Ilamas_Start / 3) - (Ilamas_Start / 4);
            n++;
        }
        while (Ilamas_Start < Ilamas_End);

    // TODO: Print number of years
    printf("Years: %d\n", n);
}
