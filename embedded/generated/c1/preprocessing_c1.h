#ifndef PREPROCESSING_C1_H
#define PREPROCESSING_C1_H
#define C1_INPUTS 128
extern const float c1_mean[128];
extern const float c1_scale[128];
int c1_preprocess(const float raw[128], float z[128]);
#endif
