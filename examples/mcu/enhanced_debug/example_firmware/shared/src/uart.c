#include "uart.h"
#include "ring-buffer.h"
#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/usart.h>
#include <libopencm3/cm3/nvic.h>
#include <libopencm3/stm32/gpio.h>
#include "ring-buffer.h"


#define UART_PORT           (GPIOA)
#define BAUDRATE            (115200)
#define RING_BUFFER_SIZE    (1024)

static ring_buffer_t rb = {0U};
static uint8_t data_buffer[RING_BUFFER_SIZE] = {0U};

// static uint8_t data_buffer = 0U; 
// static bool data_available = false;

// two different cases either overrun occured or just a byte arrived 

// void USART2_isr(void){
//     const bool overrun_occured = usart_get_flag(USART2, USART_FLAG_ORE) == 1;
//     const bool received_data = usart_get_flag(USART2, USART_FLAG_RXNE) == 1;
  
//     if(overrun_occured||received_data){
//         if(ring_buffer_write(&rb, (uint8_t) usart_recv(USART2))){
//             //handle problem
//         }
  
//         // data_buffer = (uint8_t) usart_recv(USART2);
//         // data_available = true;
//     }
  
//   }

uint8_t poll_in_rx(const uint32_t counter){
    uint32_t rx_bytes=0; 
    while(rx_bytes<counter){
        uint16_t word = usart_recv_blocking(USART2);    
        if(ring_buffer_write(&rb, (uint8_t) word)){
            rx_bytes++;
        }
        else{
            return 0;
        }
    }
    return counter;
}

void uart_setup(void){

    ring_buffer_setup(&rb, data_buffer, RING_BUFFER_SIZE);

    //enable IRQ for USART2
    // nvic_enable_irq(NVIC_USART2_IRQ);
  
    //configure USART RX on PA3
    gpio_set_mode(GPIOA, GPIO_MODE_INPUT, GPIO_CNF_INPUT_FLOAT, GPIO_USART2_RX);
    //Configure USART TX on PA2
    gpio_set_mode(GPIOA, GPIO_MODE_OUTPUT_50_MHZ, GPIO_CNF_OUTPUT_ALTFN_PUSHPULL, GPIO_USART2_TX);

    //USART2 general configuration
    usart_set_baudrate(USART2, 115200);
    usart_set_databits(USART2, 8);
    usart_set_stopbits(USART2, USART_STOPBITS_1);
    usart_set_mode(USART2, USART_MODE_TX_RX);
    usart_set_parity(USART2, USART_PARITY_NONE);
    usart_set_flow_control(USART2, USART_FLOWCONTROL_NONE);
  
    // Enable USART2 RX Interruption in the "hard way"
    // USART_CR1(USART2) |= USART_CR1_RXNEIE;

    //to be tested tomorrow
    // usart_enable_rx_interrupt(USART2);

    //globally enable USART2
    usart_enable(USART2);

}

void uart_write_byte(uint8_t data){
    usart_send_blocking(USART2,(uint16_t)data);
}

void uart_write(uint8_t* data, const uint32_t length){
    for(uint32_t i=0; i<length;i++){
        uart_write_byte(data[i]);
    }
}

uint32_t uart_read(uint8_t* data, const uint32_t length){
    // if(length>0){
    //     *data = data_buffer;
    //     data_available = false;
    //     return 1;
    // }
    // return 0;

    if(length==0){
        return 0;
    }

    for(uint32_t bytes_read=0;bytes_read<length;bytes_read++){
        if(!ring_buffer_read(&rb, &data[bytes_read])){
            return bytes_read;
        }
    }
    return length;
}

uint8_t uart_read_byte(void){
    uint8_t byte=0;
    uart_read(&byte,1);
    return byte;
}   

bool uart_data_available(void){
    return !ring_buffer_empty(&rb);
}