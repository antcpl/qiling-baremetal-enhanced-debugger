#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

from abc import abstractmethod
from typing import ClassVar, NamedTuple, Optional
from ...qdb.context import Context

class SubroutineTracker(Context):
    """Branch predictor base class.
    """
    

    stop: ClassVar[str]
    """Instruction mnemonic that can be used to determine program's end.
    """

    def has_ended(self) -> bool:
        """Determine whether the program has ended by inspecting the currnet instruction.
        """

        insn = self.disasm_lite(self.cur_addr)

        if not insn:
            return False

        # (address, size, mnemonic, op_str)
        return insn[2] == self.stop

    

    @abstractmethod
    def track(self) -> None:
        """Predict whether a certian branch will be taken or not based on current context.
        """


    # def read_reg(self, reg_name):
    #     """
    #     read specific register value
    #     """

    #     return self.ql.arch.regs.read(reg_name)

    # @abstractmethod
    # def track(self) -> None:
    #     """
    #     Try to predict certian branch will be taken or not based on current context
    #     """
    
