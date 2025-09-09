#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#



from .subroutine_tracker import *
from ...qdb.arch import ArchARM, ArchCORTEX_M
from capstone.arm_const import *
import os,json
from ..mmio_render import Render
from typing import Optional
from unicorn import UC_ERR_READ_UNMAPPED
from capstone import CsInsn
from dataclasses import dataclass

class SubroutineTrackerARM(SubroutineTracker, ArchARM, Render):
    """
    predictor for ARM
    """

    def __init__(self, ql, subroutine_names:dict=None, gdb=None):
        # SubroutineTracker.__init__(ql)    
        ArchARM.__init__(self)
        Render.__init__(self)
        self.ql = ql 
        self.subroutine_tracking_list = []
        self.subroutine_provided_dic = subroutine_names
        self.stop_feature = True
        self.stopped = False
        self.gdb = gdb 
        self.INST_SIZE = 4
        self.THUMB_INST_SIZE = 2
        self.CODE_END = "udf"


    def add_name(self, name): 
        self.subroutine_provided_dic[self.subroutine_tracking_list[-1]]=name 

    def track(self, address):
        line = self.disasm(address, True)     #inherited from context
        match line.mnemonic:
            case "bl":
                self.subroutine_tracking_list.append(line.op_str[1:])
                self.stopped = True
            case "blx":
                self.subroutine_tracking_list.append(hex(self.read_reg(line.operands[0].value.reg)-8&~1))
                self.stopped = True
            case "bx":
                if line.op_str == "lr":
                    self.subroutine_tracking_list.pop()
                else: 
                    if line.op_str =='ip':
                        self.subroutine_tracking_list.append(hex(self.read_reg('r12')))
                    else:
                        self.subroutine_tracking_list.append(hex(self.read_reg(line.op_str)))
                    self.stopped = True
            case "pop": 
                for op in line.operands:
                    if op.value.reg == ARM_REG_PC:
                        self.subroutine_tracking_list.pop()
            case "mov":
                #this case is a weird one, can't assume if we need to add an element to the pile or not
                if line.operands[0].value.reg == ARM_REG_PC: 
                    if line.operands[1].type == ARM_OP_REG:
                        self.subroutine_tracking_list.append(hex(self.read_reg(line.operands[1].value.reg)))
            # case "b":
            #     self.subroutine_tracking_list.append(line.op_str[1:])
            case "ldr": 
                if line.operands[0].value.reg == ARM_REG_PC:  
                    """
                    All of this come from capstone arm.py file 
                    In this case, we have to deal with potential load like this : ldr pc, [pc, #0x100]
                    We extract operands from line in a list : 
                    We treat the operand type : ARM_OP_REG = 1 ; ARM_OP_MEM = 3
                    [pc, #0x100] => type 3 then in this op.type object we retrieve the future loaded value 
                    op.value.mem.base => in this case it's 11 = ARM_REG_PC
                    op.value.mem.disp => immediate in int value   
                    """
                    if line.operands[1].type == ARM_OP_MEM:
                        addr = self.read_reg(line.operands[1].value.mem.base) +8 + line.operands[1].value.mem.disp
                        jump_addr = self.ql.mem.read_ptr(addr, 4)
                        self.subroutine_tracking_list.append(hex(jump_addr))
            case _: 
                return  
            
        # if we detected a subroutine jump and the subroutine_tracker stop feature is not disabled
        if self.stopped and self.stop_feature : 
            # Set the breakpoint for it to be recognised as a breakpoint by the gdbserver 
            if self.gdb is not None : 
                self.gdb.current_track = True
                self.gdb.last_bp = getattr(self.ql.arch, 'effective_pc', self.ql.arch.regs.arch_pc)

            self.ql.stop()
            self.context_subroutines()


    def restore(self): 
        with open("enhanced_debug.json", "r") as fd:
            self.subroutine_tracking_list = json.load(fd)["providing_mmio_map"]

    def dump_pile(self): 
        if len(self.subroutine_tracking_list)!=0:
            with open("enhanced_debug.json", "r") as fd:
                dic = json.loads(fd.read())
                dic["subroutine_pile"] = self.subroutine_tracking_list
            with open("enhanced_debug.json", "w") as fd: 
                fd.write(json.dumps(dic))

    def dump_naming(self): 
        if self.subroutine_provided_dic:
            with open("enhanced_debug.json", "r+") as fd:
                dic = json.loads(fd.read())
                dic["subroutine_map"] = self.subroutine_provided_dic
            with open("enhanced_debug.json", "w") as fd: 
                fd.write(json.dumps(dic))

    def add_name(self, name, addr=None): 
        address = self.subroutine_tracking_list[-1] if addr is None else addr
        #here the modification case is handled 
        self.subroutine_provided_dic[address]=name 


    @Render.divider_printer("[ SUBROUTINES ]")
    def context_subroutines(self) -> None:
        self.render_subroutines()
        if self.stopped and self.stop_feature:
            try:
                width, _ = os.get_terminal_size()
            except OSError:
                width = 130
            print("─" * width)


class SubroutineTrackerCORTEX_M(SubroutineTrackerARM, ArchCORTEX_M, Render):
    """
    test
    """
