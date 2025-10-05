

import importlib.util
import os


class MemoryMapper:

      def __init__(self, mapPath:str=None):
            self.mapPath = mapPath 
            self._map = None

      @property
      def map(self):
            return self._map

      def setMap(self):
            if not self.mapPath.endswith(".py"):
                  raise ValueError("Must be a .py file")

            spec = importlib.util.spec_from_file_location("dynamic_module", self.mapPath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                  if attr_name.startswith("__"):  
                        continue
                  attr = getattr(module, attr_name)
                  if isinstance(attr, dict):
                        self._map = attr
                        return

            raise ValueError("No dictionary found in the module")


      def fix(self, ql, access, addr, size, value):
            print(hex(addr))
            print(size)
            if size <1024: 
                  ql.mem.map(addr//1024*1024, 1024,info="ram")
            else :
                  ql.mem.map(addr//1024*1024, size,info="ram")
            return 


      def mapTheMap(self, ql):
            if self._map is not None: 
                  for start in self._map:
                        # for the moment we round the address, to the nearest page size do we want to be more precise ?
                        try :
                              size = self._map[start]["size"] 
                              if self._map[start]["size"]<1024: 
                                    size = 1024
                              # I think I've added the ram info for the snapshot
                              print(hex(start//1024*1024))
                              print(hex(size//1024*1024))
                              ql.mem.map(start//1024*1024,size//1024*1024,info="ram")
                        except MemoryError as e :
                              raise
            else: 
                  raise AttributeError("Map unitialized")

