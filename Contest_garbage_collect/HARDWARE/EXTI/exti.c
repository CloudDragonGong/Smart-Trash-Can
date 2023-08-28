#include "exti.h"

/*工训赛激光测距传感器中断，PB5下降沿检测距离
  逆时针距离变近，顺时针距离变远*/
void LASER_EXTi_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	EXTI_InitTypeDef EXTI_InitStruct;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB|RCC_APB2Periph_AFIO, ENABLE);
	
	GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Mode= GPIO_Mode_IPU;//上拉输入
	GPIO_InitStruct.GPIO_Pin= GPIO_Pin_5;
	GPIO_InitStruct.GPIO_Speed= GPIO_Speed_2MHz;
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource5);//外部中断和GPIO映射起来
	
	EXTI_StructInit(&EXTI_InitStruct);
	EXTI_InitStruct.EXTI_Line= EXTI_Line5;
    EXTI_InitStruct.EXTI_LineCmd= ENABLE;
	EXTI_InitStruct.EXTI_Mode= EXTI_Mode_Interrupt;//中断触发
	EXTI_InitStruct.EXTI_Trigger= EXTI_Trigger_Falling;//产生一个下降沿
	EXTI_Init(&EXTI_InitStruct);
}

void EXTI9_5_IRQHandler(void)
{                           
	if(EXTI_GetITStatus(EXTI_Line5)!=0)//一级判定
	{}
	EXTI_ClearITPendingBit(EXTI_Line5);//清除中断标志位
}
