#include <stdio.h>
int main() (
double n1, n2;
char op;
printf("Enter expression (e.g. 5 + 5): "); scanf("%lf %c %lf", &n1, &op, &n2);
switch(op) (
case '+'; printf("%.21f", n1+n2); break
case '-': printf("%.2IP, n1-n2); break;
case "*": printf("%.21f", n1*n2); break case '/':
if(n2!=0) printf("%.21f", n1/n2); else printf("Div by Zero"); break;
default: printf(Error");
return  0;
}