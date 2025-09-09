from qiling.core import Qiling
from qiling.const import *
from qiling.arch.models import ARM_CPU_MODEL
from cortex_M3_profile import cortexm3


ql = Qiling(["./cortexM.bin", 0x0], archtype=QL_ARCH.CORTEX_M, ostype=QL_OS.MCU, verbose=QL_VERBOSE.DISABLED, cputype=ARM_CPU_MODEL.ARM_CORTEX_M3, env=cortexm3)

ql.debugger= "gdb:127.0.0.1:9999:enhanced_debugger"

ql.run()

