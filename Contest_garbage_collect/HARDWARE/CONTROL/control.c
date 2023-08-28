#include "control.h"

u8 flag_type=0x04;//垃圾种类的变量
u8 flag_load=0x00;//满载变量，在未触发验满功能时用于给视觉发送对侧是否满载的单一标志位
u8 flag_load_type=0x04;//满载垃圾桶序号的变量
u8 flag_finish=0x00;//完成分类的变量

/*触发验满功能时用于给视觉发送各组是否满载,0、1包头；6包尾
2—00；3—01；4—02；5—03*/
u8 flag_full[7]={0x5D,0x30,0,0,0,0,0x2A};

u8 flag_sum[7]={0x2C,0x12,0,0,0,0x5B,0};//串口通信数组，发送满载变量、满载种类变量、完成分类变量
int j=0;

int time=0;//处理压缩定义的变量
int flag_react=1;

u8 no_response=0;//长时间未响应标志位（默认00，未响应01）

void keyasuo(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_2);
	flag_finish=0x00;//刷新完成标志
	flag_load=0x00;//刷新满载标志
	flag_load_type=0x04;
	flag_sum[2]=flag_load;
	flag_sum[3]=flag_load_type;
	flag_sum[4]=flag_finish;
	flag_react=1;
	time=0;
	
	dipan_turn(flag_type);
	low_forward();
	yanshi(0.9);
	duoji_left();
	low_stop();
	up_forward();//上电推杆压缩垃圾
	Get_Weight();//得到一次初值
	while((weight_shiji<20000)&flag_react)//跳出循环方式：1、重量超过80kg；2、计时时间超过8s
	{
		Get_Weight();//最后的数值定在20000g
		delay_ms(50);
		time++;
		if(time>=25)
			flag_react=0;
	}
	up_stop();
	yanshi(0.5);
	duoji_right();
	up_backward();//上电推杆复位
	low_backward();//下电推杆右行掉落垃圾
	
	yanshi(1);
	low_stop();
	
	yanshi(3);
	up_stop();
	
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)//读取激光IO口电平，低电平—超过75%；高电平—未超过
		flag_load=0x01;
	flag_finish=0x01;//标志所有任务完成
	flag_load_type=0x00;
	
	flag_sum[2]=flag_load;
	flag_sum[3]=flag_load_type;//可压缩垃圾对侧就是00其他垃圾算
	flag_sum[4]=flag_finish;
	
	for(j=0;j<7;j++)
	{
		while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		USART_SendData(USART1,flag_sum[j]);
		USART_ClearFlag(USART1,USART_FLAG_TC);
		
//		/*测试无法通过，待分析*/
//		while(USART_GetFlagStatus(USART1,USART_FLAG_TXE) != SET);
//		USART_SendData(USART1,flag_sum[j]);
//		USART_ClearFlag(USART1,USART_FLAG_TC);
//		while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		
//		while(USART_GetFlagStatus(USART2,USART_FLAG_TC) != SET);
//		USART_SendData(USART2,flag_sum[j]);
//		USART_ClearFlag(USART2,USART_FLAG_TC);
	}
	
	flag_type=0x04;//刷新垃圾种类标志位
	
	GPIO_SetBits(GPIOC, GPIO_Pin_2);
}

void bukeyasuo(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_0);
	flag_finish=0x00;
	flag_load=0x00;
	flag_load_type=0x04;
	flag_sum[2]=flag_load;
	flag_sum[3]=flag_load_type;
	flag_sum[4]=flag_finish;
	
	dipan_turn(flag_type);
//	if(flag_type==0x01)
//		yanshi(2);
//	else
	yanshi(1.3);
	duoji_left();
	yanshi(0.5);
	duoji_right();
	
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)//读取激光IO口电平，低电平—超过75%；高电平—未超过
		flag_load=0x01;//检测到为高亮，未检测到为暗亮
	flag_finish=0x01;//标志所有任务完成
	flag_load_type=number_duice(flag_type);
	
	flag_sum[2]=flag_load;
	flag_sum[3]=flag_load_type;
	flag_sum[4]=flag_finish;
	
	for(j=0;j<7;j++)
	{
	    while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		USART_SendData(USART1,flag_sum[j]);
		USART_ClearFlag(USART1,USART_FLAG_TC);
		
//		while(USART_GetFlagStatus(USART2,USART_FLAG_TC) != SET);
//		USART_SendData(USART2,flag_sum[j]);
//		USART_ClearFlag(USART2,USART_FLAG_TC);
	}
	
	flag_type=0x04;//刷新垃圾种类标志位
	
	GPIO_SetBits(GPIOC, GPIO_Pin_0);
}

void check_full(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_2);
	GPIO_ResetBits(GPIOC, GPIO_Pin_0);
	no_response=0;//复位
	for(j=2;j<6;j++)//循环复位
	  flag_full[j]=0x00;
	
	TIM_SetCompare1(TIM3, 8);//检验2号
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[4]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 13);//检验3号
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[5]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 18);//检验0号
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[2]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 23);//检验1号
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[3]=0x01;
	
	for(j=0;j<7;j++)
	{
		while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		USART_SendData(USART1,flag_full[j]);
		USART_ClearFlag(USART1,USART_FLAG_TC);
		
//		while(USART_GetFlagStatus(USART2,USART_FLAG_TC) != SET);
//		USART_SendData(USART2,flag_full[j]);
//		USART_ClearFlag(USART2,USART_FLAG_TC);
	}
	
	GPIO_SetBits(GPIOC, GPIO_Pin_2);
	GPIO_SetBits(GPIOC, GPIO_Pin_0);
}

void reset_all(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_13);
	dipan_turn(0);
	duoji_right();
	up_backward();
	low_backward();
    yanshi(2);
	low_stop();
	yanshi(1);
	up_stop();
	GPIO_SetBits(GPIOC, GPIO_Pin_13);//绿灯
	GPIO_SetBits(GPIOC, GPIO_Pin_2);//红灯
	GPIO_SetBits(GPIOC, GPIO_Pin_0);//黄灯
}

void yanshi(float ex_time)
{
	int i;
	i=ex_time*10+1;
	while(i--)
		delay_ms(100);
}

u8 number_duice(u8 type)
{
	u8 flag=0x04;
	
	if(type==0x00)flag=0x02;
	else if(type==0x01)flag=0x03;
	else if(type==0x03)flag=0x01;
	
	return flag;
}

