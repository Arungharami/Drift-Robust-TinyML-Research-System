#ifndef PREPROCESSING_C4_H
#define PREPROCESSING_C4_H
#define C4_INPUTS 128
extern const float c4_mean[128];
extern const float c4_scale[128];
int c4_preprocess(const float raw[128], float z[128]);
#endif
