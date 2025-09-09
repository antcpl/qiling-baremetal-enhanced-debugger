

import importlib.util
import os


class MemoryMapper:

      #TODO : update the pagination problem, this implementation works but in some cases, it can be wrong

      def __init__(self, map):
            self.map = map

      #note : if the list is empty, the memory mapper still maps everything !
      def check_validity(self, addr, size) -> bool: 
            for t in self.map: 
                  if (addr>=t[0] and addr<t[1]) or (addr+size>=t[0] and addr+size<t[1]): 
                        return False 
            return True

      def fix(self, ql, access, addr, size, value):
            if self.check_validity(addr, size):
                  if size <1024: 
                        ql.mem.map(addr//1024*1024, 1024,info="ram")
                  else :
                        ql.mem.map(addr//1024*1024, size,info="ram")
                  return 
            else : 
                  print("[!] Impossible to map this ")
