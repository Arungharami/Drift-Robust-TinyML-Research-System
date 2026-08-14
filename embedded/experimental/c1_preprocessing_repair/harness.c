#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "repair_candidates.h"
#include "model_c1.h"

int main(int argc,char **argv){
  if(argc!=3)return 2;FILE *in=fopen(argv[1],"r"),*out=fopen(argv[2],"w");if(!in||!out)return 3;
  char line[65536],id[128];fprintf(out,"candidate_id,sample_id");for(int i=0;i<128;i++)fprintf(out,",z_%03d",i);for(int c=0;c<6;c++)fprintf(out,",score_%d",c);for(int c=0;c<6;c++)fprintf(out,",prob_%d",c);fprintf(out,",prediction");for(int i=0;i<128;i++)fprintf(out,",attribution_%03d",i);fprintf(out,"\n");
  while(fgets(line,sizeof(line),in)){char *t=strtok(line,",");if(!t)continue;strncpy(id,t,127);id[127]=0;float raw[128];for(int i=0;i<128;i++){t=strtok(NULL,",");if(!t)return 4;raw[i]=strtof(t,NULL);}for(int candidate=0;candidate<5;candidate++){float z[128],s[6],p[6],a[128];if(!repair_preprocess(candidate,raw,z))return 5;int best=0;for(int c=0;c<6;c++){float v=c1_intercept[c];for(int i=0;i<128;i++)v+=c1_coef[c*128+i]*z[i];s[c]=v;if(v>s[best])best=c;}float m=s[0];for(int c=1;c<6;c++)if(s[c]>m)m=s[c];float sum=0;for(int c=0;c<6;c++){p[c]=expf(s[c]-m);sum+=p[c];}for(int c=0;c<6;c++)p[c]/=sum;best=0;for(int c=1;c<6;c++)if(p[c]>p[best])best=c;for(int i=0;i<128;i++)a[i]=c1_coef[best*128+i]*z[i];fprintf(out,"%s,%s",repair_candidate_ids[candidate],id);for(int i=0;i<128;i++)fprintf(out,",%.9g",z[i]);for(int c=0;c<6;c++)fprintf(out,",%.9g",s[c]);for(int c=0;c<6;c++)fprintf(out,",%.9g",p[c]);fprintf(out,",%d",best+1);for(int i=0;i<128;i++)fprintf(out,",%.9g",a[i]);fprintf(out,"\n");}}
  fclose(in);fclose(out);return 0;
}
