#include "stm32f10x.h"
#include "sys.h" 
#include <stdio.h>

/*
PA0(TIM2CH1)�����������+
PA2(TX),PA3(RX)����usart2��λ������
PA6�������̶��
PA7�����ͷ��������
PA9(TX),PA10(RX)����usart1���շ������ݣ�����һ��Ҫ��֤���Ӿ��Ĳ��������õ���ȫ��ͬ
PB1���������������+��˳ʱ�룺����ʱ�룺��
PB2�����������ʹ��+���͵�ƽ������״̬������Ӧ�������壩
PB5�������⴫����
PB6,PB7����AD���ش�����
PB8,PB9�������Ƹ�
PB12,PB13�������Ƹ�
PC0�Ƶ�,PC2���,PC13�̵�

flag_sum[6]:0��1��ͷ��2����У��λ��00δ���أ�01���أ���
3��������Ͱ��ţ�00����������01����������02�ɻ���������03�к���������
4���У��λ��00δ��ɣ�01����ɣ���5��β��
*/

int main(void)
{	
	delay_init();
    uart1_init(9600);
	uart2_init(9600);
	LASER_EXTi_Init();//�������ʼ��
	NVIC_Config();
	
	duoji_Init();
	Weight_Init();//���ش�������ʼ��
	PUSH_Init();
	
	reset_all();
		
	while(1)
	{		
		if(flag_type==0x02)
			keyasuo();
		else if(flag_type==0x01|flag_type==0x03|flag_type==0x00)
			bukeyasuo();
		
		if(no_response==0x01)
			check_full();
	}		
}
