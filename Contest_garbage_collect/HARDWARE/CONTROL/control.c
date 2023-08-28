#include "control.h"

u8 flag_type=0x04;//��������ı���
u8 flag_load=0x00;//���ر�������δ������������ʱ���ڸ��Ӿ����ͶԲ��Ƿ����صĵ�һ��־λ
u8 flag_load_type=0x04;//��������Ͱ��ŵı���
u8 flag_finish=0x00;//��ɷ���ı���

/*������������ʱ���ڸ��Ӿ����͸����Ƿ�����,0��1��ͷ��6��β
2��00��3��01��4��02��5��03*/
u8 flag_full[7]={0x5D,0x30,0,0,0,0,0x2A};

u8 flag_sum[7]={0x2C,0x12,0,0,0,0x5B,0};//����ͨ�����飬�������ر��������������������ɷ������
int j=0;

int time=0;//����ѹ������ı���
int flag_react=1;

u8 no_response=0;//��ʱ��δ��Ӧ��־λ��Ĭ��00��δ��Ӧ01��

void keyasuo(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_2);
	flag_finish=0x00;//ˢ����ɱ�־
	flag_load=0x00;//ˢ�����ر�־
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
	up_forward();//�ϵ��Ƹ�ѹ������
	Get_Weight();//�õ�һ�γ�ֵ
	while((weight_shiji<20000)&flag_react)//����ѭ����ʽ��1����������80kg��2����ʱʱ�䳬��8s
	{
		Get_Weight();//������ֵ����20000g
		delay_ms(50);
		time++;
		if(time>=25)
			flag_react=0;
	}
	up_stop();
	yanshi(0.5);
	duoji_right();
	up_backward();//�ϵ��Ƹ˸�λ
	low_backward();//�µ��Ƹ����е�������
	
	yanshi(1);
	low_stop();
	
	yanshi(3);
	up_stop();
	
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)//��ȡ����IO�ڵ�ƽ���͵�ƽ������75%���ߵ�ƽ��δ����
		flag_load=0x01;
	flag_finish=0x01;//��־�����������
	flag_load_type=0x00;
	
	flag_sum[2]=flag_load;
	flag_sum[3]=flag_load_type;//��ѹ�������Բ����00����������
	flag_sum[4]=flag_finish;
	
	for(j=0;j<7;j++)
	{
		while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		USART_SendData(USART1,flag_sum[j]);
		USART_ClearFlag(USART1,USART_FLAG_TC);
		
//		/*�����޷�ͨ����������*/
//		while(USART_GetFlagStatus(USART1,USART_FLAG_TXE) != SET);
//		USART_SendData(USART1,flag_sum[j]);
//		USART_ClearFlag(USART1,USART_FLAG_TC);
//		while(USART_GetFlagStatus(USART1,USART_FLAG_TC) != SET);
		
//		while(USART_GetFlagStatus(USART2,USART_FLAG_TC) != SET);
//		USART_SendData(USART2,flag_sum[j]);
//		USART_ClearFlag(USART2,USART_FLAG_TC);
	}
	
	flag_type=0x04;//ˢ�����������־λ
	
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
	
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)//��ȡ����IO�ڵ�ƽ���͵�ƽ������75%���ߵ�ƽ��δ����
		flag_load=0x01;//��⵽Ϊ������δ��⵽Ϊ����
	flag_finish=0x01;//��־�����������
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
	
	flag_type=0x04;//ˢ�����������־λ
	
	GPIO_SetBits(GPIOC, GPIO_Pin_0);
}

void check_full(void)
{
	GPIO_ResetBits(GPIOC, GPIO_Pin_2);
	GPIO_ResetBits(GPIOC, GPIO_Pin_0);
	no_response=0;//��λ
	for(j=2;j<6;j++)//ѭ����λ
	  flag_full[j]=0x00;
	
	TIM_SetCompare1(TIM3, 8);//����2��
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[4]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 13);//����3��
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[5]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 18);//����0��
	yanshi(3);
	if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5)==0)
		flag_full[2]=0x01;
	yanshi(1);
	
	TIM_SetCompare1(TIM3, 23);//����1��
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
	GPIO_SetBits(GPIOC, GPIO_Pin_13);//�̵�
	GPIO_SetBits(GPIOC, GPIO_Pin_2);//���
	GPIO_SetBits(GPIOC, GPIO_Pin_0);//�Ƶ�
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

