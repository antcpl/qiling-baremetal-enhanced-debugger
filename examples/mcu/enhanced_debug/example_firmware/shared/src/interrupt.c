#include <libopencm3/cm3/nvic.h>
#include <libopencm3/stm32/gpio.h>
#include "core/interrupt.h"
#include "core/uart.h"

uint8_t message[]={104,97,114,100,32,102,97,117,108,116,10};

void hard_fault_handler(void){
    while(1){
        for(uint32_t i=0; i<60000;i++){
            __asm__ volatile ("nop");
        }
        uart_write(message, 11);
    }
}