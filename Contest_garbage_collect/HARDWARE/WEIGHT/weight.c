#include "weight.h"

/*���ش�����ģ�飬PB7��DAT��PB6��CLK����ADת����*/
uint32_t weight_shiji=0;
uint32_t weight_qupi=0;

uint32_t Read_Weight(void);
void Get_Weight(void);
	
void Weight_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStructure;
	
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
	
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_7;//PB7��DAT
	GPIO_Init(GPIOB, &GPIO_InitStructure);
	
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6;//PB6��CLK
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOB, &GPIO_InitStructure);
	
	weight_qupi=Read_Weight();
}

uint32_t Read_Weight(void)
{
	uint8_t i;
	uint32_t value = 0;
	
	/**
	�����ֲ�д��������������ܽ� DOUT Ϊ�ߵ�ƽʱ������A/D ת������δ׼����������ݣ���ʱ����ʱ
	�������ź� PD_SCK ӦΪ�͵�ƽ������������������״̬��
	**/
	GPIO_SetBits(GPIOB, GPIO_Pin_7); //��ʼ״̬DT����Ϊ�ߵ�ƽ
	GPIO_ResetBits(GPIOB, GPIO_Pin_6); //��ʼ״̬SCK����Ϊ�͵�ƽ
	
	/**
	�ȴ�DT���ű�Ϊ�ߵ�ƽ
	**/
	while(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_7));
	delay_us(1);
	
	/**
	�� DOUT �Ӹߵ�ƽ��͵�ƽ��PD_SCK Ӧ���� 25 �� 27 �����ȵ�ʱ������
	25��ʱ������ ---> ͨ��A ����128
	26��ʱ������ ---> ͨ��B ����32
	27��ʱ������ ---> ͨ��A ����64
	**/
	for(i=0; i<24; i++) //24λ������ݴ����λ�����λ��λ������
	{
//		//����һ��
//		GPIO_SetBits(GPIOB, GPIO_Pin_6); //ʱ�Ӹߵ�ƽ
//		value = value << 1; //���DTλΪ������һλ
//		delay_us(1);
//		GPIO_ResetBits(GPIOB, GPIO_Pin_6); //ʱ�ӵ͵�ƽ
//		if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_7))
//			value++; //���DTλΪ�ߣ�ֵ+1
//		delay_us(1);
		

		//��������
		GPIO_SetBits(GPIOB, GPIO_Pin_6);
		delay_us(1);
		GPIO_ResetBits(GPIOB, GPIO_Pin_6);
		if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_7) == 0)
		{
			value = value << 1;
			value |= 0x00;
		}
		if(GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_7) == 1)
		{
			value = value << 1;
			value |= 0x01;
		}
		delay_us(1);
	}
	
	//�� 25�� 27 ��ʱ����������ѡ����һ�� A/D ת��������ͨ��������
	GPIO_SetBits(GPIOB, GPIO_Pin_6); 
	value = value^0x800000; 
	delay_us(1); 
	GPIO_ResetBits(GPIOB, GPIO_Pin_6); 
	delay_us(1);  
	return value; 	
}

void Get_Weight(void)
{
    weight_shiji = Read_Weight();
	if(weight_qupi>weight_shiji)
	{
		weight_shiji=weight_qupi-weight_shiji;
		weight_shiji=2.34*weight_shiji/100;//2.34������ϵ������ȷ������׼ȷ�������������ص���
		printf("%dg",weight_shiji);
	}
	else if(weight_qupi<=weight_shiji)
	{
		weight_shiji=weight_shiji-weight_qupi;
		weight_shiji=2.34*weight_shiji/100;
		printf("%dg",weight_shiji);
	}
//	return weight_shiji;
}

//uint32_t get_max_weight(uint32_t now_weight)
//{
//	int max_weight=0;
//	
//	if(now_weight>=max_weight)
//		max_weight=now_weight;
//	
//	return max_weight;
//}
