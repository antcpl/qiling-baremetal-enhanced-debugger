#ifndef INC_SYSTEM_H
#define INC_SYSTEM_H

#include "common-defines.h"

// be careful, as precised in the libopencm3 documentation, if the frequency is too low the handler set_frequency doesn"t work
#define CPU_FREQ        (72000000)
// be careful, as precised in the libopencm3 documentation, if the frequency is too low the handler set_frequency doesn"t work
#define SYSTICK_FREQ    (1000000)

#endif // INC_SYSTEM_H