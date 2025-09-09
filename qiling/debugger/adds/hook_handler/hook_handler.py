
from qiling import Qiling
from ..mmio_tracker.tracker import MMIOTracker

class HookHandler(): 

    def __init__(self, hook_list: list):
        self.hook_list=hook_list
        self.hook_read = []
        self.hook_write = []

    def hook_setter(self, ql:Qiling, mmio_tracker:MMIOTracker):
        for t in self.hook_list: 
            self.hook_read.append(ql.hook_mem_read(mmio_tracker.mmio_access_handler,begin=t[0],end=t[1],  user_data=("mmio",)))
            self.hook_write.append(ql.hook_mem_write(mmio_tracker.mmio_access_handler,begin=t[0],end=t[1], user_data=("mmio",)))

    def hook_unsetter(self, ql:Qiling): 
        for h in self.hook_read:
            ql.hook_del(h)
        for h in self.hook_write:
            ql.hook_del(h)

    