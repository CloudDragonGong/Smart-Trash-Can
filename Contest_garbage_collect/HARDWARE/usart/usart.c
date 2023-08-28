#include "usart.h"	  
  
#if 1
#pragma import(__use_no_semihosting)             
//标准库需要的支持函数                 
struct __FILE 
{ 
	int handle; 

}; 

FILE __stdout;       
//定义_sys_exit()以避免使用半主机模式    
_sys_exit(int x) 
{ 
	x = x; 
} 
//重定义fputc函数 
int fputc(int ch, FILE *f)
{      
	while((USART2->SR&0X40)==0);//循环发送,直到发送完毕   
    USART2->DR = (u8) ch;      
	return ch;
}
#endif
 
#if EN_USART1_RX   //如果使能了接收
//串口2中断服务程序
//注意,读取USARTx->SR能避免莫名其妙的错误   	
u8 USART_RX_BUF[USART_REC_LEN];     //接收缓冲,最大USART_REC_LEN个字节.
//接收状态
//bit15，	接收完成标志
//bit14，	接收到0x0d
//bit13~0，	接收到的有效字节数目
u16 USART_RX_STA=0;       //接收状态标记	  
  
void uart1_init(u32 bound)
{
    //GPIO端口设置
    GPIO_InitTypeDef GPIO_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	 
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1|RCC_APB2Periph_GPIOA, ENABLE);	//使能USART1，GPIOA时钟
  
	//USART1_TX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;	//复用推挽输出
    GPIO_Init(GPIOA, &GPIO_InitStructure);
   
    //USART1_RX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;//浮空输入
    GPIO_Init(GPIOA, &GPIO_InitStructure);
  
   //USART 初始化设置

	USART_InitStructure.USART_BaudRate = bound;//串口波特率
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;//字长为8位数据格式
	USART_InitStructure.USART_StopBits = USART_StopBits_1;//一个停止位
	USART_InitStructure.USART_Parity = USART_Parity_No;//无奇偶校验位
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;//无硬件数据流控制
	USART_InitStructure.USART_Mode =  USART_Mode_Rx|USART_Mode_Tx;	//收发模式
    USART_Init(USART1, &USART_InitStructure); //初始化串口1
  
    USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);//开启串口接受中断
    USART_Cmd(USART1, ENABLE);                    //使能串口1 

}

void uart2_init(u32 bound)
{
    //GPIO端口设置
    GPIO_InitTypeDef GPIO_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	 
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2,ENABLE);
	//USART2_TX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;	//复用推挽输出
    GPIO_Init(GPIOA, &GPIO_InitStructure);
   
    //USART2_RX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;//浮空输入
    GPIO_Init(GPIOA, &GPIO_InitStructure);
  
   //USART 初始化设置

	USART_InitStructure.USART_BaudRate = bound;//串口波特率
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;//字长为8位数据格式
	USART_InitStructure.USART_StopBits = USART_StopBits_1;//一个停止位
	USART_InitStructure.USART_Parity = USART_Parity_No;//无奇偶校验位
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;//无硬件数据流控制
	USART_InitStructure.USART_Mode = USART_Mode_Rx|USART_Mode_Tx;	//收发模式
    USART_Init(USART2, &USART_InitStructure);
	
    USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);//开启串口接受中断
    USART_Cmd(USART2, ENABLE);

}

void USART1_IRQHandler(void)                	//串口1中断服务程序
{
	 u8 com_data; 
	
	 static u16 Rebuf_1[4]={0};
	 static u8 i=0;
	 static u8 RxState_1=0;
	 u8 count_1;
	 
	 static u16 Rebuf_2[4]={0};
	 static u8 m=0;
	 static u8 RxState_2=0;
	 u8 count_2;
	 
	if(USART_GetITStatus(USART1,USART_IT_RXNE)!=RESET)
	{
		USART_ClearITPendingBit(USART1,USART_IT_RXNE);//清除中断标志
		com_data=USART_ReceiveData(USART1);
		
		if(RxState_1==0&&com_data==0x2C)
		{
			RxState_1=1;
			Rebuf_1[i++]=com_data;
		}
		else if(RxState_1==1&&com_data==0x12)
		{
			RxState_1=2;
			Rebuf_1[i++]=com_data;
		}

		else if(RxState_1==2)
		{
			Rebuf_1[i++]=com_data;

			if(i>=3||com_data==0x5B)       //RxBuffer1接受满了，或者接收数据结束
			{
				flag_type=Rebuf_1[2];
				
				USART_ITConfig(USART1,USART_IT_RXNE,DISABLE);//关闭DTSABLE中断
				
				i=0;
				RxState_1=0;
				for(count_1=0;count_1<4;count_1++)
				{
					Rebuf_1[count_1]=0x00;      //将存放数据数组清零，重新开始计数
				}
				
				USART_ITConfig(USART1,USART_IT_RXNE,ENABLE);			

			}
		}
		else   //接收异常
		{
			RxState_1=0;
			i=0;
			for(count_1=0;count_1<4;count_1++)
			{
				Rebuf_1[count_1]=0x00;      //将存放数据数组清零
			}
		}
/******************************************************/		
		if(RxState_2==0&&com_data==0x5D)
		{
			RxState_2=1;
			Rebuf_2[m++]=com_data;
		}
		else if(RxState_2==1&&com_data==0x30)
		{
			RxState_2=2;
			Rebuf_2[m++]=com_data;
		}

		else if(RxState_2==2)
		{
			Rebuf_2[m++]=com_data;

			if(m>=3||com_data==0x2A)       //Rebuf接受满了，或者接收数据结束
			{
				no_response=Rebuf_2[2];
				
				USART_ITConfig(USART1,USART_IT_RXNE,DISABLE);//关闭DTSABLE中断
				
				m=0;
				RxState_2=0;
				for(count_2=0;count_2<4;count_2++)
				{
					Rebuf_2[count_2]=0x00;      //将存放数据数组清零，重新开始计数
				}
				
				USART_ITConfig(USART1,USART_IT_RXNE,ENABLE);			

			}
		}
		else   //接收异常
		{
			RxState_2=0;
			m=0;
			for(count_2=0;count_2<4;count_2++)
			{
				Rebuf_2[count_2]=0x00;      //将存放数据数组清零
			}
		}
	}
}
	
void USART2_IRQHandler(void)            //蓝牙调试
{
	u8 Res;
	if(USART_GetITStatus(USART2, USART_IT_RXNE) != RESET)  //接收中断(接收到的数据必须是0x0d 0x0a结尾)
	{
		Res =USART_ReceiveData(USART2);	//读取接收到的数据
//		if(Res==0x01)flag_type=0x01;
//		else if(Res==0x02)flag_type=0x02;
//		else if(Res==0x03)flag_type=0x03;
//		else if(Res==0x00)flag_type=0x00;
//		else if(Res==0x05)no_response=0x01;
     } 
		USART_ClearITPendingBit(USART2,USART_IT_RXNE);        //清除USART1的接收中断标志位
}

#endif	
