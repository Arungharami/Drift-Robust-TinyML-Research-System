#include "inference_c1_fused.h"
#include "model_c1_fused.h"
#include <math.h>
int c1_fused_infer(const float x[128],float s[6],float p[6]){for(int i=0;i<128;i++)if(!isfinite(x[i]))return 0;for(int c=0;c<6;c++){float a=c1_fused_biases[c];for(int i=0;i<128;i++)a+=c1_fused_weights[c][i]*x[i];s[c]=a;}float m=s[0];for(int c=1;c<6;c++)if(s[c]>m)m=s[c];float z=0.0f;for(int c=0;c<6;c++){p[c]=expf(s[c]-m);z+=p[c];}for(int c=0;c<6;c++)p[c]/=z;return 1;}
