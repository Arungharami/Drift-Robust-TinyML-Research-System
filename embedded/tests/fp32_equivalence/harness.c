#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef MODEL_C1
#include "inference_c1.h"
#define PREFIX "c1"
#else
#include "inference_c4.h"
#define PREFIX "c4"
#endif

int main(int argc,char **argv){
  if(argc!=3){fprintf(stderr,"usage: harness input.csv output.csv\n");return 2;}
  FILE *in=fopen(argv[1],"r"),*out=fopen(argv[2],"w");if(!in||!out)return 3;
  char line[65536],id[128];
  fprintf(out,"sample_id");for(int i=0;i<128;i++)fprintf(out,",z_%03d",i);for(int c=0;c<6;c++)fprintf(out,",score_%d",c);for(int c=0;c<6;c++)fprintf(out,",prob_%d",c);fprintf(out,",prediction");
#ifdef MODEL_C1
  for(int i=0;i<128;i++)fprintf(out,",attribution_%03d",i);
#endif
  fprintf(out,"\n");
  while(fgets(line,sizeof(line),in)){
    char *token=strtok(line,",");if(!token)continue;strncpy(id,token,sizeof(id)-1);id[sizeof(id)-1]=0;
    float raw[128],z[128],scores[6],probs[6];int ok=1;
    for(int i=0;i<128;i++){token=strtok(NULL,",");if(!token){ok=0;break;}raw[i]=strtof(token,NULL);}if(!ok)return 4;
#ifdef MODEL_C1
    float attrs[128];int prediction=c1_infer(raw,z,scores,probs,attrs);
#else
    int prediction=c4_infer(raw,z,scores,probs);
#endif
    if(prediction<0)return 5;fprintf(out,"%s",id);for(int i=0;i<128;i++)fprintf(out,",%.9g",z[i]);for(int c=0;c<6;c++)fprintf(out,",%.9g",scores[c]);for(int c=0;c<6;c++)fprintf(out,",%.9g",probs[c]);fprintf(out,",%d",prediction+1);
#ifdef MODEL_C1
    for(int i=0;i<128;i++)fprintf(out,",%.9g",attrs[i]);
#endif
    fprintf(out,"\n");
  }
  fclose(in);fclose(out);return 0;
}
