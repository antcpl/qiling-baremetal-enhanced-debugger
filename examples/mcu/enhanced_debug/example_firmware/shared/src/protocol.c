#include "common-defines.h"
#include "core/protocol.h"
#include "core/uart.h"
#include <libopencm3/stm32/gpio.h>

uint8_t magic[]={49,51,51,55,49,51,51,55};
uint8_t protocol_header[]={117,97,114,116};


//general notes : 
//The get_magic_value function could be a tricky example to deal with as no new basic bloc will be covered
//It could be interesting to nest the poll_in_rx function into a uart_read function in another POC to have a more HAL friendly code

uint8_t check(uint8_t* recv, uint8_t size, uint8_t* waited_val){
  for(uint8_t i=0; i<size; i++){
    if (recv[i]!=waited_val[i]){
      return 0;
    }
  }
  return 1; 
}

void reset(uint8_t*ptr, uint8_t size){
  for(uint8_t i=0;i<size;i++){
    ptr[i]=0U;
  }
}

void parse_len(uint8_t* message, uint32_t recv_size, uint32_t * calculated_len){
  uint8_t counter=recv_size-3;
  uint8_t i=2;
  uint32_t tmp=1;
  uint32_t size=0;
  while(counter>0){
    for(uint8_t pow=0;pow<(counter-1);pow++){
      tmp*=10;
    }
    size+=tmp*((*(message+i))-48);
    counter--;
    i++;
    tmp=1;
  }
  *calculated_len = size;
}


void protocol_manager(void){
  
  uint8_t read_bytes = poll_in_rx(8);
  uint8_t msg[8] = {0U};
  uint8_t header[4] = {0U};
  uint8_t len[2] = {0U};
  uint32_t calculated_len = 0;
  
  if (read_bytes<8){
    return;
  }

  uart_read(msg,read_bytes);

  if (check(msg, read_bytes, magic)){
    reset(msg,10);

    read_bytes = poll_in_rx(4); 
    uart_read(header,read_bytes);
    if (check(header, read_bytes, protocol_header)){
      read_bytes = poll_in_rx(2); 
      uart_read(len,read_bytes);
      parse_len(len, read_bytes, &calculated_len);
    }
    else{
      return; 
    }
  }
  else{
    return;
  }
}