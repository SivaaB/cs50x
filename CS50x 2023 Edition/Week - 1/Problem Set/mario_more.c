#include <cs50.h>
#include <stdio.h>

int height, row, column, space;

int main(void)
{
    do
    {
        height = get_int("Enter Height: ");
    }
    while (height < 1 || height > 8);

    for (row = 0 ; row < height ; row++)
    {
        for (space = 0; space < height - row - 1 ; space++)
        {
            printf(" ");
        }
        for (column = 0; column <= row; column++)
        {
            printf("#");
        }
        printf("  ");
        for (column = 0; column <= row; column++)
        {
            printf("#");
        }
        printf("\n");
    }
}