#ifndef XAI_C1_FUSED_H
#define XAI_C1_FUSED_H
void c1_fused_explain(const float raw[128],int class_index,float contribution[128]);
float c1_fused_explanation_score(int class_index,const float contribution[128]);
#endif
