#include "stm32f10x.h"
#include "sys.h" 
#include <stdio.h>

/*
PA0(TIM2CH1)步进电机脉冲+
PA2(TX),PA3(RX)——usart2上位机调试
PA6——底盘舵机
PA7——释放垃圾舵机
PA9(TX),PA10(RX)——usart1接收发送数据！！！一定要保证和视觉的波特率设置的完全相同
PB1——步进电机方向+（顺时针：；逆时针：）
PB2——步进电机使能+（低电平，自由状态，不响应步进脉冲）
PB5——激光传感器
PB6,PB7——AD称重传感器
PB8,PB9——上推杆
PB12,PB13——下推杆
PC0黄灯,PC2红灯,PC13绿灯

flag_sum[6]:0、1包头；2满载校验位（00未满载，01满载）；
3满载垃圾桶编号（00其他垃圾；01厨余垃圾；02可回收垃圾；03有害垃圾）；
4完成校验位（00未完成；01已完成）；5包尾；
*/

int main(void)
{	
	delay_init();
    uart1_init(9600);
	uart2_init(9600);
	LASER_EXTi_Init();//激光测距初始化
	NVIC_Config();
	
	duoji_Init();
	Weight_Init();//称重传感器初始化
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
