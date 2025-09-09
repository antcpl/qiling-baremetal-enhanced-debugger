#ifndef INC_COMMON_DEFINES_H
#define INC_COMMON_DEFINES_H

#include <stdint.h>
#include <stdbool.h>


#define LED_PORT        (GPIOC)
#define LED_PIN         (GPIO13)

// be careful, as precised in the libopencm3 documentation, if the frequency is too low the handler set_frequency doesn"t work
#define CPU_FREQ        (72000000)
// be careful, as precised in the libopencm3 documentation, if the frequency is too low the handler set_frequency doesn"t work
#define SYSTICK_FREQ    (10000)


#endif // INC_COMMON_DEFINES_H
