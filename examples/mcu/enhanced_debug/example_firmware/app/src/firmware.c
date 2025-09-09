#include <libopencm3/stm32/rcc.h>
#include <libopencm3/stm32/gpio.h>
#include <libopencm3/cm3/systick.h>
//contains the structure of the interrupt vector table
#include <libopencm3/cm3/vector.h>
// vector.c file contains the linker attributes functions to place the vector table at the right place in the memory 
// by default the vector.c file contains also the handler definitions for different interrupt vector entries
// by default they are weak and points towards the null_handler


// // to get the definition of the vector table offset 
#include <libopencm3/cm3/scb.h>

#include <libopencm3/stm32/usart.h>
#include <libopencm3/stm32/memorymap.h>

// flash program with openocd
// openocd -f stlink_bluepill.cfg -c "program main.elf verify reset exit"

// debug program with openocd 
// openocd -f stlink_bluepill.cfg


// #include "core/system.h"
#include "core/uart.h"
#include "core/protocol.h"
#include "common-defines.h"


#define UART_PORT       (GPIOA)
#define RX_PIN          (GPIO10)
#define TX_PIN          (GPIO9)


#define BOOTLOADER_SIZE     (0x8000U)

// Here we switch the vector table from the bootloader vector table to the firmware vector table 
static void vector_setup(void){
  SCB_VTOR = BOOTLOADER_SIZE;
}


static void clock_setup(void){

  //this is for the LED toggling
  rcc_periph_clock_enable(RCC_GPIOC);
  gpio_set_mode(LED_PORT,GPIO_MODE_OUTPUT_50_MHZ,GPIO_CNF_OUTPUT_PUSHPULL, LED_PIN);

  //this is for UART 
  rcc_periph_clock_enable(RCC_GPIOA);
  rcc_periph_clock_enable(RCC_USART2);
  //Don't forget the AFIO even if we use the default Alternate function
  rcc_periph_clock_enable(RCC_AFIO);

}

int main(void){
  vector_setup();
  clock_setup();
  uart_setup();

  while(1){
    protocol_manager();
  }
  
  return 0;
}
