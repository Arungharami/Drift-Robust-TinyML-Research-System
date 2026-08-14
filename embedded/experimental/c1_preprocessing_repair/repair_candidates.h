#ifndef REPAIR_CANDIDATES_H
#define REPAIR_CANDIDATES_H
extern const char *repair_candidate_ids[5];
int repair_preprocess(int candidate,const float raw[128],float z[128]);
#endif
