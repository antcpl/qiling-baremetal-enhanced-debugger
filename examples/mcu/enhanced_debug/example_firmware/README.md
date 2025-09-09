# example_firmware compilation 

First, you will need to install the ```arm-none-eabi``` toolchain that is necessary to compile C code for baremetal ARM cortex M chips. Once done, you can go further with these commands : 

**To install libopencm3** which is offering all the Hardware Abstraction Layer for the development. 
```bash 
cd example_firmware 
git clone https://github.com/libopencm3/libopencm3.git
cd libopencm3 
make TARGETS='stm32/f1'
```

**Then compile the bootloader**
```bash 
cd bootloader 
make 
```

**Finally compile the whole firmware**
```bash 
cd ../app
make 
```
