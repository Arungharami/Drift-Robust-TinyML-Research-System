#include "inference_c1_fused.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int n,char**v){if(n!=3)return 2;FILE*i=fopen(v[1],"r"),*o=fopen(v[2],"w");if(!i||!o)return 3;char line[131072];fprintf(o,"sample_id,prediction");for(int c=0;c<6;c++)fprintf(o,",score_%d",c);for(int c=0;c<6;c++)fprintf(o,",prob_%d",c);fputc(10,o);while(fgets(line,sizeof line,i)){char*save=0,*t=strtok_r(line,",\r\n",&save);if(!t)continue;char id[256];snprintf(id,sizeof id,"%s",t);float x[128],s[6],p[6];for(int k=0;k<128;k++){t=strtok_r(0,",\r\n",&save);if(!t)return 4;x[k]=strtof(t,0);}if(!c1_fused_infer(x,s,p))return 5;int y=0;for(int c=1;c<6;c++)if(s[c]>s[y])y=c;fprintf(o,"%s,%d",id,y+1);for(int c=0;c<6;c++)fprintf(o,",%.9g",s[c]);for(int c=0;c<6;c++)fprintf(o,",%.9g",p[c]);fputc(10,o);}return fclose(i)||fclose(o);}
