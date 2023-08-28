#include "usart.h"	  
  
#if 1
#pragma import(__use_no_semihosting)             
//��׼����Ҫ��֧�ֺ���                 
struct __FILE 
{ 
	int handle; 

}; 

FILE __stdout;       
//����_sys_exit()�Ա���ʹ�ð�����ģʽ    
_sys_exit(int x) 
{ 
	x = x; 
} 
//�ض���fputc���� 
int fputc(int ch, FILE *f)
{      
	while((USART2->SR&0X40)==0);//ѭ������,ֱ���������   
    USART2->DR = (u8) ch;      
	return ch;
}
#endif
 
#if EN_USART1_RX   //���ʹ���˽���
//����2�жϷ������
//ע��,��ȡUSARTx->SR�ܱ���Ī������Ĵ���   	
u8 USART_RX_BUF[USART_REC_LEN];     //���ջ���,���USART_REC_LEN���ֽ�.
//����״̬
//bit15��	������ɱ�־
//bit14��	���յ�0x0d
//bit13~0��	���յ�����Ч�ֽ���Ŀ
u16 USART_RX_STA=0;       //����״̬���	  
  
void uart1_init(u32 bound)
{
    //GPIO�˿�����
    GPIO_InitTypeDef GPIO_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	 
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1|RCC_APB2Periph_GPIOA, ENABLE);	//ʹ��USART1��GPIOAʱ��
  
	//USART1_TX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;	//�����������
    GPIO_Init(GPIOA, &GPIO_InitStructure);
   
    //USART1_RX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;//��������
    GPIO_Init(GPIOA, &GPIO_InitStructure);
  
   //USART ��ʼ������

	USART_InitStructure.USART_BaudRate = bound;//���ڲ�����
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;//�ֳ�Ϊ8λ���ݸ�ʽ
	USART_InitStructure.USART_StopBits = USART_StopBits_1;//һ��ֹͣλ
	USART_InitStructure.USART_Parity = USART_Parity_No;//����żУ��λ
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;//��Ӳ������������
	USART_InitStructure.USART_Mode =  USART_Mode_Rx|USART_Mode_Tx;	//�շ�ģʽ
    USART_Init(USART1, &USART_InitStructure); //��ʼ������1
  
    USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);//�������ڽ����ж�
    USART_Cmd(USART1, ENABLE);                    //ʹ�ܴ���1 

}

void uart2_init(u32 bound)
{
    //GPIO�˿�����
    GPIO_InitTypeDef GPIO_InitStructure;
	USART_InitTypeDef USART_InitStructure;
	 
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2,ENABLE);
	//USART2_TX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;	//�����������
    GPIO_Init(GPIOA, &GPIO_InitStructure);
   
    //USART2_RX
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;//��������
    GPIO_Init(GPIOA, &GPIO_InitStructure);
  
   //USART ��ʼ������

	USART_InitStructure.USART_BaudRate = bound;//���ڲ�����
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;//�ֳ�Ϊ8λ���ݸ�ʽ
	USART_InitStructure.USART_StopBits = USART_StopBits_1;//һ��ֹͣλ
	USART_InitStructure.USART_Parity = USART_Parity_No;//����żУ��λ
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;//��Ӳ������������
	USART_InitStructure.USART_Mode = USART_Mode_Rx|USART_Mode_Tx;	//�շ�ģʽ
    USART_Init(USART2, &USART_InitStructure);
	
    USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);//�������ڽ����ж�
    USART_Cmd(USART2, ENABLE);

}

void USART1_IRQHandler(void)                	//����1�жϷ������
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
		USART_ClearITPendingBit(USART1,USART_IT_RXNE);//����жϱ�־
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

			if(i>=3||com_data==0x5B)       //RxBuffer1�������ˣ����߽������ݽ���
			{
				flag_type=Rebuf_1[2];
				
				USART_ITConfig(USART1,USART_IT_RXNE,DISABLE);//�ر�DTSABLE�ж�
				
				i=0;
				RxState_1=0;
				for(count_1=0;count_1<4;count_1++)
				{
					Rebuf_1[count_1]=0x00;      //����������������㣬���¿�ʼ����
				}
				
				USART_ITConfig(USART1,USART_IT_RXNE,ENABLE);			

			}
		}
		else   //�����쳣
		{
			RxState_1=0;
			i=0;
			for(count_1=0;count_1<4;count_1++)
			{
				Rebuf_1[count_1]=0x00;      //�����������������
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

			if(m>=3||com_data==0x2A)       //Rebuf�������ˣ����߽������ݽ���
			{
				no_response=Rebuf_2[2];
				
				USART_ITConfig(USART1,USART_IT_RXNE,DISABLE);//�ر�DTSABLE�ж�
				
				m=0;
				RxState_2=0;
				for(count_2=0;count_2<4;count_2++)
				{
					Rebuf_2[count_2]=0x00;      //����������������㣬���¿�ʼ����
				}
				
				USART_ITConfig(USART1,USART_IT_RXNE,ENABLE);			

			}
		}
		else   //�����쳣
		{
			RxState_2=0;
			m=0;
			for(count_2=0;count_2<4;count_2++)
			{
				Rebuf_2[count_2]=0x00;      //�����������������
			}
		}
	}
}
	
void USART2_IRQHandler(void)            //��������
{
	u8 Res;
	if(USART_GetITStatus(USART2, USART_IT_RXNE) != RESET)  //�����ж�(���յ������ݱ�����0x0d 0x0a��β)
	{
		Res =USART_ReceiveData(USART2);	//��ȡ���յ�������
//		if(Res==0x01)flag_type=0x01;
//		else if(Res==0x02)flag_type=0x02;
//		else if(Res==0x03)flag_type=0x03;
//		else if(Res==0x00)flag_type=0x00;
//		else if(Res==0x05)no_response=0x01;
     } 
		USART_ClearITPendingBit(USART2,USART_IT_RXNE);        //���USART1�Ľ����жϱ�־λ
}

#endif	
