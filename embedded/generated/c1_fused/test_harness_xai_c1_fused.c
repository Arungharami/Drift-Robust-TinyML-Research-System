#include "xai_c1_fused.h"
#include "inference_c1_fused.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int n,char**v){if(n!=3)return 2;FILE*i=fopen(v[1],"r"),*o=fopen(v[2],"w");if(!i||!o)return 3;char l[131072];fprintf(o,"sample_id,explained_class,explanation_score,inference_score");for(int k=0;k<128;k++)fprintf(o,",contribution_%03d",k);fputc(10,o);while(fgets(l,sizeof l,i)){char*s=0,*t=strtok_r(l,",\r\n",&s),id[256];if(!t)continue;snprintf(id,sizeof id,"%s",t);t=strtok_r(0,",\r\n",&s);int c=atoi(t)-1;float x[128],a[128],sc[6],p[6];for(int k=0;k<128;k++){t=strtok_r(0,",\r\n",&s);x[k]=strtof(t,0);}c1_fused_explain(x,c,a);c1_fused_infer(x,sc,p);fprintf(o,"%s,%d,%.9g,%.9g",id,c+1,c1_fused_explanation_score(c,a),sc[c]);for(int k=0;k<128;k++)fprintf(o,",%.9g",a[k]);fputc(10,o);}return fclose(i)||fclose(o);}
