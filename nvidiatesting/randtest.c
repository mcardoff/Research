#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

double rand_double(double min, double max) {
  double range = (max - min); 
  double div = RAND_MAX / range;
  return min + (rand() / div);
  /* return ((double)rand() * (high - low)) / (double)RAND_MAX + low; */

}

int main() {
  double randomNum;
  srand(time(NULL)%1729+getpid());
  for(int i = 0; i < 20; i++){
    randomNum = rand_double(-1,1);
    printf("%f\n",randomNum);
  }
  return 0;
}
