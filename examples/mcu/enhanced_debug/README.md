# Cortex M3 firmware examples 

These examples are here to show what could be achieved using the new developed features. Both examples are based on a firmware that has been developped for the STM32F103C8T6 chip (also known as the blue pill) with an ARM Cortex M3 core. As briefly mentionned, we created this tool to fuzz well choosen parts of baremetal binaries but this could be used not only to fuzz but to setup bruteforce or other Qiling based vulnerability researches. The methodology we propose is the following : 
1. Identify a part of the code that you may target for a vulnerability research. 
2. Identify the hardware peripherals linked to the targeted part of the code. 
3. Identify in the binary their initialisation processes. 
4. Emulate the code from the beginning to reach the target function and provide a faithful emulation of the aforementioned hardware peripherals
5. Perform a snapshot
6. Reuse this snapshot to perform the vulnerability hunting.

In the following examples, the [cortex_M3_reverse_example](./cortex_M3_reverse_example/) demonstrates how to perform the 5 first steps of the process and the [cortex_M3_bruteforce_example](./cortex_M3_bruteforce_example/) is an illustration of vulnerability hunting. 

## The firmware : [example_firmware](./example_firmware/)

Inspired by "The baremetal programming series" from **low byte productions** available on youtube and GitHub [The baremetal programming series](https://github.com/lowbyteproductions/bare-metal-series).

The firmware is composed of a [bootloader](./example_firmware/bootloader/) that does nothing apart locating the second part of the firmware and transfering execution to it. The bootloader is located in the [0x0800 0000; 0x0800 7FFF] memory range.  

The core of the [firmware](./example_firmware/app/) is located from 0x08008000 and above in memory. The firmware implements a small USART application. After all the peripherals initialisation, the main is performing a polling over the USART2 and try to retrieve 8 bytes. Received bytes are placed in a ring buffer. Once 8 bytes have been received, the application retrieve them from the ring buffer and compare them with a magic value. If the value is correct ("13371337"), then the application tries to retrieve 4 other bytes and perform another comparison ("USART").

You may want to recompile the firmware but the generated binary is already available in [cortex_M3_reverse_example](./cortex_M3_reverse_example/) and [cortex_M3_bruteforce_example](./cortex_M3_bruteforce_example/). However, you may follow the steps described in the [README](./example_firmware/README.md) to recompile it from scratch. 

## Reverse Example : [cortex_M3_reverse_example](./cortex_M3_reverse_example/)

The goal of this example is to show exactly how to perform reverse engineering and a faithful emulation of the baremetal firmware using the upgrades.  
The already provided reverse elements cover three aspects : 
- **The subroutine naming** : during the execution you will be able to cross-check the subroutine names with the functions names of the C firmware code. 
- **The hardware peripherals naming** : using the STM32F103C8T6 memory map, you will also be able to cross-check the accessed peripherals names with the ones defined in the map. 
- **The hardware peripherals provided values** : the firmware is accessing hardware peripherals during two different phases. The setup phase which is characterized by load/modify/store access patterns and that doesn't impact the execution flow. And the main phase where we want the execution to be faithful. 

During the main phase, the firmware logic is making polling on the USART. From the hardware peripherals side, this represents alternated access on the USART Status Register and the Data Register. 
- Status Regitser access is done in the subroutine located at ```0x08008716```. The subroutine is checking in a while loop if the RXNE bit is set or not. This is handled for you using the ```0x00000020``` value that you will observe in the pile during the execution. 
- Data Register access is done in the subroutine located at ```0x08008706```. In that case as well, the value have already been provided for you and you will see them in the pile. 
 
**Advice** : try to execute the binary with the memory map of the STM32F103C8T6 on the side. You will be able to cross-check all the accessed addresses with the MMIO names already provided in the configuration file. 

- **Test the example** : 
Execute this command line and connect to the 9999 tcp port using a gdb client or the tool of your choice. 
```bash 
python general_script.py
```
You'll just have to control the execution that will be driven by the already provided values. 

- **general_script.py** : 
Is the Qiling script used to emulate the binary. You will notice that the enhanced_debugger parameter is present in the gdbserver line. 
- **cortex_M3_profile.py** : a dictionary defining some memory regions of the cortex M3 and that are mapped thanks to the mcu loader defined in Qiling. 
- **cortexM.bin** : is the compiled firmware.
- **cortexM.bin.i64** : the IDA database corresponding to the binary that has some indications of the subroutine names. 
- **enhanced_debug.json** : the configuration that is storing all the values. 

## Bruteforce Example : [cortex_M3_bruteforce_example](./cortex_M3_bruteforce_example/)

This example is here to demonstrate the vulnerability hunting part that could be done using Qiling. The firmware itself is well suited to perform a bruteforce on the waited value. Indeed, the comparison is done is a loop as the strcmp maneer. As the processing is done byte per byte this represents only 255 values to try 8 times in a row. The exploit has been entirely design to provide the best performances. 

To test it just execute : 

```bash 
python bruteforce.py
```
The bruteforce script starts execution from the execution.bin file. This is a snapshot that has been created using the tool. Using emulation, we reached the poll_in_rx call in the protocol_manager function and start our bruteforce from here. 