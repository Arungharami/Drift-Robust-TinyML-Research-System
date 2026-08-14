#include "inference_c1.h"
#include "preprocessing_c1.h"
#include "model_c1.h"
#include <math.h>
int c1_infer(const float raw[128],float z[128],float s[6],float p[6],float a[128]){if(!c1_preprocess(raw,z))return -1;int best=0;for(int c=0;c<6;c++){float v=c1_intercept[c];for(int i=0;i<128;i++)v+=c1_coef[c*128+i]*z[i];s[c]=v;if(v>s[best])best=c;}float m=s[0];for(int c=1;c<6;c++)if(s[c]>m)m=s[c];float sum=0;for(int c=0;c<6;c++){p[c]=expf(s[c]-m);sum+=p[c];}for(int c=0;c<6;c++)p[c]/=sum;best=0;for(int c=1;c<6;c++)if(p[c]>p[best])best=c;for(int i=0;i<128;i++)a[i]=c1_coef[best*128+i]*z[i];return best;}
