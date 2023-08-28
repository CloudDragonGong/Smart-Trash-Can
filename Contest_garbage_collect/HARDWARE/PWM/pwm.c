#include "pwm.h"

/*舵机pwm控制，PA6—TIM3通道1，PA7—TIM3通道2*/

void duoji_Init(void)
{
		GPIO_InitTypeDef GPIO_InitStruct;
		TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
		TIM_OCInitTypeDef TIM_OCInitStruct;
		
		//1.使能GPIO时钟、定时器时钟、复用时钟
		RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
		RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE);

		//3.配置GPIO
	    GPIO_StructInit(&GPIO_InitStruct);
		GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AF_PP;
		GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_7;
		GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
		GPIO_Init(GPIOA, &GPIO_InitStruct);
	
		GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AF_PP;
		GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_6;
		GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
		GPIO_Init(GPIOA, &GPIO_InitStruct);
		
		//4.配置定时器
	    TIM_TimeBaseStructInit(&TIM_TimeBaseInitStruct);
		TIM_TimeBaseInitStruct.TIM_ClockDivision = TIM_CKD_DIV1;
		TIM_TimeBaseInitStruct.TIM_CounterMode   = TIM_CounterMode_Up;
		TIM_TimeBaseInitStruct.TIM_Period        = 200-1;
		TIM_TimeBaseInitStruct.TIM_Prescaler     = 7200-1;
		TIM_TimeBaseInit(TIM3, &TIM_TimeBaseInitStruct);
		
		//5.配置PWM
		TIM_OCStructInit(&TIM_OCInitStruct);
		TIM_OCInitStruct.TIM_OCMode      = TIM_OCMode_PWM1;
		TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
		TIM_OCInitStruct.TIM_OCPolarity  = TIM_OCPolarity_High;
		TIM_OC2Init(TIM3, &TIM_OCInitStruct);
		TIM_OC2PreloadConfig(TIM3, TIM_OCPreload_Enable);
		
		TIM_OCStructInit(&TIM_OCInitStruct);
		TIM_OCInitStruct.TIM_OCMode      = TIM_OCMode_PWM1;
		TIM_OCInitStruct.TIM_OutputState = TIM_OutputState_Enable;
		TIM_OCInitStruct.TIM_OCPolarity  = TIM_OCPolarity_High;
		TIM_OC1Init(TIM3, &TIM_OCInitStruct);
		TIM_OC1PreloadConfig(TIM3, TIM_OCPreload_Enable);
		
		TIM_Cmd(TIM3, ENABLE);
		
}

void duoji_right(void)
{
	TIM_SetCompare2(TIM3, 1.3/20*200);//1.3-1.42-1.8
}

void duoji_left(void)
{
	TIM_SetCompare2(TIM3, 1.7/20*200);//1.3-1.42-1.8
}

void dipan_turn(u16 flag_turn)
{
	int pwm_out;
	
	pwm_out = 8+flag_turn*5;
	TIM_SetCompare1(TIM3, pwm_out);//8(0)、13(1)、18(2)、23(3)
}
