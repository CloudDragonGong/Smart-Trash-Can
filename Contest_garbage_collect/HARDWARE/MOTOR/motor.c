#include "motor.h"

/*GPIO初始化函数，控制电推杆升降*/
void PUSH_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB|RCC_APB2Periph_GPIOC, ENABLE);
	
	GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Pin=GPIO_Pin_8 |GPIO_Pin_9|GPIO_Pin_12|GPIO_Pin_13;//默认低电平
	GPIO_InitStruct.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_InitStruct.GPIO_Mode=GPIO_Mode_Out_PP;//推挽输出
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	GPIO_InitStruct.GPIO_Pin=GPIO_Pin_13|GPIO_Pin_2|GPIO_Pin_0;//默认低电平
	GPIO_InitStruct.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_InitStruct.GPIO_Mode=GPIO_Mode_Out_PP;//推挽输出
	GPIO_Init(GPIOC, &GPIO_InitStruct);
	
	GPIO_ResetBits(GPIOC, GPIO_Pin_13);
	GPIO_ResetBits(GPIOC, GPIO_Pin_2);
	GPIO_ResetBits(GPIOC, GPIO_Pin_0);
}

void up_stop(void)
{
	GPIO_ResetBits(GPIOB, GPIO_Pin_8);//0.44A的电流
	GPIO_ResetBits(GPIOB, GPIO_Pin_9);
}

void up_forward(void)
{
	GPIO_SetBits(GPIOB, GPIO_Pin_8);//0.44A的电流
	GPIO_ResetBits(GPIOB, GPIO_Pin_9);
}

void up_backward(void)
{
	GPIO_ResetBits(GPIOB, GPIO_Pin_8);//0.44A的电流
	GPIO_SetBits(GPIOB, GPIO_Pin_9);
}

void low_stop(void)
{
	GPIO_ResetBits(GPIOB, GPIO_Pin_12);//0.44A的电流
	GPIO_ResetBits(GPIOB, GPIO_Pin_13);
}


void low_forward(void)
{
	GPIO_SetBits(GPIOB, GPIO_Pin_12);//0.44A的电流
	GPIO_ResetBits(GPIOB, GPIO_Pin_13);
}

void low_backward(void)
{
	GPIO_ResetBits(GPIOB, GPIO_Pin_12);//0.44A的电流
	GPIO_SetBits(GPIOB, GPIO_Pin_13);
}
