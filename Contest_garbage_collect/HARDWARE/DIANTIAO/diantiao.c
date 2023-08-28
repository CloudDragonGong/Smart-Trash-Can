#include "diantiao.h"


/*PA1-TIM2_CH2-���pwm���Ƶ��������ˢ���*/
/*���������Ϻ�ֻ��Ҫ��1ms ~ 2ms��5% - 10%ռ�ձȣ�֮�䣬
�����������ɵ�����ˢ���ת��,1msΪֹͣ��2msΪ���ת�١�*/
void diantiao_Init(void)
{
		GPIO_InitTypeDef GPIO_InitStruct;
		TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
		TIM_OCInitTypeDef TIM_OCInitStruct;
		
		//1.ʹ��GPIOʱ�ӡ���ʱ��ʱ�ӡ�����ʱ��
		RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
		RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);

		//3.����GPIO
	    GPIO_StructInit(&GPIO_InitStruct);
		GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AF_PP;
		GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_1;
		GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
		GPIO_Init(GPIOA, &GPIO_InitStruct);
		
		//4.���ö�ʱ��
	    TIM_TimeBaseStructInit(&TIM_TimeBaseInitStruct);
		TIM_TimeBaseInitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
		TIM_TimeBaseInitStruct.TIM_CounterMode   = TIM_CounterMode_Up;
		TIM_TimeBaseInitStruct.TIM_Period        = 200-1;
		TIM_TimeBaseInitStruct.TIM_Prescaler     = 7200-1;
		TIM_TimeBaseInit(TIM2, &TIM_TimeBaseInitStruct);
		
		//5.����PWM
		TIM_OCStructInit(&TIM_OCInitStruct);
		TIM_OCInitStruct.TIM_OCMode      = TIM_OCMode_PWM1;
		TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
		TIM_OCInitStruct.TIM_OCPolarity  = TIM_OCPolarity_High;
		TIM_OC2Init(TIM2, &TIM_OCInitStruct);
		TIM_OC2PreloadConfig(TIM2, TIM_OCPreload_Enable);
		
		TIM_Cmd(TIM2, ENABLE);
		
}

void turn(int flag_turn)
{
	float pwm_out;
	
	flag_turn=flag_type;
	pwm_out=(1.0+(1.9-1.0)/4*flag_turn)/20*200;
	
	TIM_SetCompare2(TIM2, pwm_out);
}

