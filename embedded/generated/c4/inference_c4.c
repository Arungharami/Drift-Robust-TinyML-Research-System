#include "inference_c4.h"
#include "preprocessing_c4.h"
#include "model_c4.h"
#include <math.h>
int c4_infer(const float raw[128],float z[128],float s[6],float p[6]){float h1[64],h2[32];if(!c4_preprocess(raw,z))return -1;for(int j=0;j<64;j++){float v=c4_b1[j];for(int i=0;i<128;i++)v+=z[i]*c4_w1[i*64+j];h1[j]=v>0?v:0;}for(int j=0;j<32;j++){float v=c4_b2[j];for(int i=0;i<64;i++)v+=h1[i]*c4_w2[i*32+j];h2[j]=v>0?v:0;}for(int j=0;j<6;j++){float v=c4_b3[j];for(int i=0;i<32;i++)v+=h2[i]*c4_w3[i*6+j];s[j]=v;}float m=s[0];for(int j=1;j<6;j++)if(s[j]>m)m=s[j];float sum=0;for(int j=0;j<6;j++){p[j]=expf(s[j]-m);sum+=p[j];}for(int j=0;j<6;j++){p[j]/=sum;s[j]=p[j];}int best=0;for(int j=1;j<6;j++)if(p[j]>p[best])best=j;return best;}
