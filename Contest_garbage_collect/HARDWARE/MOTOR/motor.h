#ifndef _MOTOR_H
#define _MOTOR_H

#include "sys.h"

void PUSH_Init(void);
void up_stop(void);
void up_forward(void);
void up_backward(void);
void low_stop(void);
void low_forward(void);
void low_backward(void);

#endif
