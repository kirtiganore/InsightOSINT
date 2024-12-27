#include<stdio.h>
int main()
{
    int age;
    printf("Enter the age: ");
    scanf("%d", &age);


    if(age<=18)
    {
        printf("you can't drive");
    }
    else if(age>70)
    {
        printf("you can't drive");
    }
    else
    {
        printf("you can drive");
    }
    return 0;
}