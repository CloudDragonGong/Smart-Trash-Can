#include "exti.h"

/*��ѵ�������ഫ�����жϣ�PB5�½��ؼ�����
  ��ʱ���������˳ʱ������Զ*/
void LASER_EXTi_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	EXTI_InitTypeDef EXTI_InitStruct;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB|RCC_APB2Periph_AFIO, ENABLE);
	
	GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Mode= GPIO_Mode_IPU;//��������
	GPIO_InitStruct.GPIO_Pin= GPIO_Pin_5;
	GPIO_InitStruct.GPIO_Speed= GPIO_Speed_2MHz;
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	GPIO_EXTILineConfig(GPIO_PortSourceGPIOB, GPIO_PinSource5);//�ⲿ�жϺ�GPIOӳ������
	
	EXTI_StructInit(&EXTI_InitStruct);
	EXTI_InitStruct.EXTI_Line= EXTI_Line5;
    EXTI_InitStruct.EXTI_LineCmd= ENABLE;
	EXTI_InitStruct.EXTI_Mode= EXTI_Mode_Interrupt;//�жϴ���
	EXTI_InitStruct.EXTI_Trigger= EXTI_Trigger_Falling;//����һ���½���
	EXTI_Init(&EXTI_InitStruct);
}

void EXTI9_5_IRQHandler(void)
{                           
	if(EXTI_GetITStatus(EXTI_Line5)!=0)//һ���ж�
	{}
	EXTI_ClearITPendingBit(EXTI_Line5);//����жϱ�־λ
}
