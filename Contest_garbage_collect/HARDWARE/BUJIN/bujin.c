#include "bujin.h"


void Bujin_motor_init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);//使能GPIOE时钟
	
	GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Pin = GPIO_Pin_1|GPIO_Pin_2; //DRIVER_DIR DRIVER_OE对应引脚
	GPIO_InitStruct.GPIO_Speed=GPIO_Speed_50MHz;
	GPIO_InitStruct.GPIO_Mode=GPIO_Mode_Out_PP;//推挽输出
	GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	GPIO_SetBits(GPIOB,GPIO_Pin_1);//PB1输出高，默认一个方向
	GPIO_SetBits(GPIOB,GPIO_Pin_2);//PB2输出高，不脱机，响应步进电机脉冲
}

void Bujin_pul_init(u16 arr,u16 psc)
{		 					 
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStruct;
	TIM_OCInitTypeDef TIM_OCInitStruct;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2,ENABLE);
	
	//配置GPIO
    GPIO_StructInit(&GPIO_InitStruct);
	GPIO_InitStruct.GPIO_Mode  = GPIO_Mode_AF_PP;
	GPIO_InitStruct.GPIO_Pin   = GPIO_Pin_0;
	GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	//4.配置定时器
	TIM_TimeBaseStructInit(&TIM_TimeBaseInitStruct);
	TIM_TimeBaseInitStruct.TIM_ClockDivision = 0;
	TIM_TimeBaseInitStruct.TIM_CounterMode   = TIM_CounterMode_Up;
	TIM_TimeBaseInitStruct.TIM_Period        = arr;//TIM2->ARR的值越大对应的脉冲频率越小，速度就降低，反之则会速度越快。
	TIM_TimeBaseInitStruct.TIM_Prescaler     = psc;
	TIM_TimeBaseInit(TIM2, &TIM_TimeBaseInitStruct);
	
	//配置PWM
	TIM_OCStructInit(&TIM_OCInitStruct);
	TIM_OCInitStruct.TIM_OCMode=TIM_OCMode_PWM1;                //PWM1模式
	TIM_OCInitStruct.TIM_OCPolarity=TIM_OCPolarity_High;        //设置PWM输出极性high
	TIM_OCInitStruct.TIM_OutputState=TIM_OutputState_Enable;    //PWM比较输出使能
	TIM_OCInitStruct.TIM_Pulse=0;                                //初始化脉宽为0
	TIM_OC1Init(TIM2, &TIM_OCInitStruct);                       //初始化通道一
	
	TIM_OC1PreloadConfig(TIM2, TIM_OCPreload_Enable);
	TIM_ARRPreloadConfig(TIM2, ENABLE); //使能TIMX在ARR上的预装载值
	
	TIM_Cmd(TIM2, ENABLE);  //使能TIM2										  
}


