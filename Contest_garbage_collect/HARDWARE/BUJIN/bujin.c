#include "bujin.h"


void Bujin_motor_init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);//ʹ��GPIOEʱ��
	
	GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_1|GPIO_Pin_2; //DRIVER_DIR DRIVER_OE��Ӧ����
	GPIO_InitStruct.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_InitStruct.GPIO_Mode=GPIO_Mode_Out_PP;//�������
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	GPIO_SetBits(GPIOB,GPIO_Pin_1);//PB1����ߣ�Ĭ��һ������
	GPIO_SetBits(GPIOB,GPIO_Pin_2);//PB2����ߣ����ѻ�����Ӧ�����������
}

void Bujin_pul_init(u16 arr,u16 psc)
{		 					 
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
	TIM_OCInitTypeDef TIM_OCInitStruct;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2,ENABLE);
	
	//����GPIO
    GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AF_PP;
	GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_0;
	GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	//4.���ö�ʱ��
	TIM_TimeBaseStructInit(&TIM_TimeBaseInitStruct);
	TIM_TimeBaseInitStruct.TIM_ClockDivision = 0;
	TIM_TimeBaseInitStruct.TIM_CounterMode   = TIM_CounterMode_Up;
	TIM_TimeBaseInitStruct.TIM_Period        = arr;//TIM2->ARR��ֵԽ���Ӧ������Ƶ��ԽС���ٶȾͽ��ͣ���֮����ٶ�Խ�졣
	TIM_TimeBaseInitStruct.TIM_Prescaler     = psc;
	TIM_TimeBaseInit(TIM2, &TIM_TimeBaseInitStruct);
	
	//����PWM
	TIM_OCStructInit(&TIM_OCInitStruct);
	TIM_OCInitStruct.TIM_OCMode=TIM_OCMode_PWM1;                //PWM1ģʽ
	TIM_OCInitStruct.TIM_OCPolarity=TIM_OCPolarity_High;        //����PWM�������high
	TIM_OCInitStruct.TIM_OutputState=TIM_OutputState_Enable;    //PWM�Ƚ����ʹ��
	TIM_OCInitStruct.TIM_Pulse=0;                                //��ʼ������Ϊ0
	TIM_OC1Init(TIM2, &TIM_OCInitStruct);                       //��ʼ��ͨ��һ
	
	TIM_OC1PreloadConfig(TIM2, TIM_OCPreload_Enable);
	TIM_ARRPreloadConfig(TIM2, ENABLE); //ʹ��TIMX��ARR�ϵ�Ԥװ��ֵ
	
	TIM_Cmd(TIM2, ENABLE);  //ʹ��TIM2										  
}


