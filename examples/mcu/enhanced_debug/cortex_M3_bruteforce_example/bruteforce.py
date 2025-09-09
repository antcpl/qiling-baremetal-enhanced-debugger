from qiling.core import Qiling
from qiling.const import *
from qiling.arch.models import ARM_CPU_MODEL
from cortex_M3_profile import cortexm3
from multiprocessing import Queue
from memory_mapper import MemoryMapper

#Hook to provide the RXNE bit 
def provide_RXNE_bit(ql:Qiling): 
    print("[+] Provided the RXNE bit")
    ql.mem.write(0x40004400, b"\x20\x00\x00\x00")

#Hook to provide the USART byte value 
def provide_USART_DR_byte(ql:Qiling,user_data): 
    global current_val
    print("[+] Providing the DR byte with current_val = {0} and pc = {1:08x}".format(current_val, ql.arch.regs.arch_pc))
    ql.mem.write(0x40004404, user_data[current_val])
    current_val+=1

#Hook to track all the executed blocs in a defined range address
def block_callback(ql, address, size, user_data):
    basic_blocks = user_data[0]
    addr_range = user_data[1]
    if addr_range[0]<= address <= addr_range[1]:
        value = basic_blocks.get(address)
        if value is not None: 
            basic_blocks[address]+=1
        else: 
            basic_blocks[address]=1

def stop(ql:Qiling):
    ql.stop()

#Compare reference_dict with the current one
def post_processing(reference:dict, current_run:dict):
    return sum(reference.values())<sum(current_run.values())
 
            
def crack(size_input:int,win_address:int, loose_address:int,restore_file:str,dry_run:bool,range_addr:list, reference_dict:dict=None):
    
    ########################### Qiling general setup ########################### 
    basic_blocks = {}
    ql = Qiling(["./cortexM.bin", 0x0], archtype=QL_ARCH.CORTEX_M, ostype=QL_OS.MCU, verbose=QL_VERBOSE.DISABLED, cputype=ARM_CPU_MODEL.ARM_CORTEX_M3, env=cortexm3)
    mapper = MemoryMapper([])
    ql.hook_mem_unmapped(mapper.fix)
    ql.hook_address(stop,win_address)
    ql.hook_address(provide_RXNE_bit,0x08008716)
    ############################################################################

    global current_val
    current_val=0
   
    values = [b"\x00" * 1 for _ in range(size_input)]
    
    if dry_run: 
        #dry_run is here to intialise a reference dictionary for blocs counting
        hk1 = ql.hook_address(provide_USART_DR_byte,0x08008706,user_data=values)
        ql.hook_block(block_callback, user_data=[basic_blocks,range_addr])
        ql.restore(snapshot="./execution.bin")
        print(values)

        ql.run(begin=0x08008509, end=loose_address|1)

        if ql.arch.regs.arch_pc==win_address: 
            print("[+] The magic value is {0}".format(values))
            return
        return basic_blocks
    else:
        for byte_number in range(8):
            print("[+] byte_number = {0}".format(byte_number)) 
            for byte_value in range(1,255):
                print("[+] byte_value = {0}".format(byte_value))
                values[byte_number]=byte_value.to_bytes()
                # set the parameter for this run 
                hk1 = ql.hook_address(provide_USART_DR_byte,0x08008706,user_data=values)
                hk2 = ql.hook_block(block_callback, user_data=[basic_blocks,range_addr])


                ql.restore(snapshot="./execution.bin")
                print(values)

                ql.run(begin=0x08008509, end=loose_address|1)

                if ql.arch.regs.arch_pc==win_address: 
                    print("[+] The magic value is {0}".format(values))
                    return
                #Reset the parameters for the next run 
                ql.hook_del(hk1)
                ql.hook_del(hk2)
                current_val=0
                #Comparison between the reference_dict and the one from this run to detect new executed blocs
                if post_processing(reference_dict, basic_blocks):
                    reference_dict=basic_blocks
                    basic_blocks={}
                    print("[+] Go on for the next byte")
                    break    
                basic_blocks={}


if __name__ == "__main__":
    #user provided parameters : 
    size_input = 8
    win_address = 0x0800854e
    loose_address = 0x080085b0
    restore_file = "./execution.bin"
    range_addr = [0x08008400, 0x0800843c]

    reference_dict = crack(size_input, win_address, loose_address, restore_file, True, range_addr)
    
    print(reference_dict)
    
    crack(size_input, win_address, loose_address, restore_file, False, range_addr,reference_dict)

