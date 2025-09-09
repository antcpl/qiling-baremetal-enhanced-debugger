
import json
from qiling import Qiling



from capstone import CsInsn
from unicorn.unicorn_const import *
from typing import Mapping
import copy

from ..mmio_render import Render
# from ...gdb.utils import QlGdbUtils


class MMIOTracker(Render): 
    def __init__(self, mmio_map: dict, providing_map: dict, gdb = None, server = False, context_render=None):
        Render.__init__(self)
    
        self._mmio_map = mmio_map
        self._providing_map = providing_map
        self.output_providing_map = {}
        self.track_list = []
        self.current_pile = None
        self.disable_mmio_stop = False
        self.context_render = context_render
        self.seen = False
        #piled_value is only used to indicate that the last treatment implicated a pile and that we potentially need to
        #overwrite it either in the formatting, either in the output_providing
        self.piled_value = False
        self.gdb = gdb
        self.current_track = False
    
    def get_map(self)->dict:
        return self._mmio_map
        
    
    def get_providing_map(self)->dict:
        if self._providing_map: 
            return self._providing_map
        else : 
            return {}

    def __pile_formatter(self,unformatted_pile: list)-> list:
        formatted_pile = []
        for x in unformatted_pile : 
            formatted_pile.append(hex(x))
        return formatted_pile


    def __overwrite_value(self, provided_val : int) ->None:
        """
        Only for rendering, called from do_provide and replace the last pile value in the current formatted track list 
        for it to be updated 
        """
        if self.piled_value: 
            self.track_list[-1]["pile"][0] = hex(provided_val)

    def __check_seen_value(self, addr:int, size:int)->bool:
        # print(addr in self.output_providing_map) 
        # print(size in self.output_providing_map[addr])

        # print(self.output_providing_map)
        test = self.output_providing_map.get(addr,False) 
        # print(test)
        if test != False: 
            if size in test : 
                return True 
        
        return False

    def __add_line_to_dump(self, dic: dict, provided_val , provided_addr=None, provided_size=None)->None:
        addr = provided_addr if provided_addr is not None else self.track_list[-1]["addr"]
        size = provided_size if provided_size is not None else self.track_list[-1]["size"]
        # print("{0:08x}".format(addr))
        # print(size)
        if addr in dic: 
            if size in dic[addr]: 
                if self.piled_value: 
                    # print("replace the last value")
                    dic[addr][size][-1] = provided_val
                else:
                    # print("added the last value to the output dump")
                    dic[addr][size].append(provided_val)
            else:
                # print("new size added to dump")
                dic[addr][size] = [provided_val]
        else:
            # print("new address added to dump")
            dic[addr] = {size:[provided_val]}
            # print(dic)


    def __key_to_hex_converter(self, dic: dict = None): 
        formatted_dict = {}
        for k in dic:
            if isinstance(k, int):
                formatted_dict[hex(k)] = dic[k]
            else: 
                formatted_dict[k] = dic[k]
        return formatted_dict


    def __name_retriever(self)-> None: 
        self.track_list[-1]["name"]="Unspecified device"
        map = self.get_map()
        for mmio_addr in map: 
            if mmio_addr <= self.track_list[-1]["addr"] < mmio_addr+ map[mmio_addr]["size"]:
                self.track_list[-1]["name"]=map[mmio_addr]["name"]
                return
            

    def __pile_retriever(self)-> None: 
        provider_map = self.get_providing_map()
        if self.track_list[-1]["access"]==16: 
            for start_addr in provider_map:
                for size in provider_map[start_addr]:
                    if self.track_list[-1]["addr"] == start_addr and size == self.track_list[-1]["size"]:
                        # here we need a copy for the rendering to be coherent 
                        self.track_list[-1]["pile"] = self.__pile_formatter(provider_map[start_addr][size].copy())
                        # current pile is here to have a dynamic consuming, meaning when consuming a value, this is also executed on the providing_map dictionary 
                        self.current_pile = provider_map[start_addr][size]
                        return 



    def __access_information_collector(self)->None: 
        """
        Retrieve information to the corresponding access 
        """
        self.__name_retriever()
        self.__pile_retriever()


    def __dump_dict(self,dic: dict=None, key:str = None, opt_dic : dict=None)->None: 
        save = self.piled_value
        if opt_dic is not None: 
            tmp=opt_dic
            self.piled_value=False
            for addr in tmp: 
                for size in tmp[addr]: 
                    for val in tmp[addr][size]: 
                        self.__add_line_to_dump(dic, val, addr,size)
        final_dump = {}
        formatted_dump = self.__key_to_hex_converter(dic)
        for k in formatted_dump:  
            final_dump[k] = self.__key_to_hex_converter(formatted_dump[k])

        # output_str = json.dumps(final_dump)
        
        with open("enhanced_debug.json", "r") as fd : 
            tmp = json.loads(fd.read())
            tmp[key] = final_dump
            
        with open("enhanced_debug.json", "w") as fd :
            fd.write(json.dumps(tmp))
        self.piled_value=save


    def dump(self)->None:
        """
        Format the output_providing_map into a dumpable format and write the formatted values into a file 
        output_providing_map -> json -> file
        """
        self.__dump_dict(self.output_providing_map,"providing_mmio_map",opt_dic=self.get_providing_map())
        self.__dump_dict(self.get_map(),'mmio_map')

    
    @Render.divider_printer("[ MMIO ]")
    def context_mmio(self) -> None:
        """
        Helper to gather information for the access and call the renderer
        """
        self.render_mmio_access()
            

    def mmio_access_handler(self, ql, access, addr, size, value, user_data):
        """
           General manager, called from callback 
           Gather information on the access, dispatch the work and consume values in case of provided pile
        """
        # print("hello")
        # print("self.disable_mmio_stop "+str(self.disable_mmio_stop))
        # print("self.seen "+str(self.seen))
        if not self.seen : 
            self.current_pile=None 
            self.piled_value=False
            self.current_track = True 
            self.seen = True
            #track_list management
            len(self.track_list)>3 and self.track_list.pop(0)
            self.track_list.append({"access": access,"addr":addr,"size":size,"value":value, "curr_value":None, "state": 'o'})
            # print("helloooooooooo")
            if ql.mem.is_mapped(addr, size):
                self.track_list[-1]["curr_value"]=ql.mem.read(addr,size)

            if not self.disable_mmio_stop: 
                # stop the emulation 
                # print("ql.stop call")
                ql.stop()

                if self.context_render : 
                    self.context_render()
                if self.gdb:
                    #be careful to take the correct pc, because it could change if thumb mode or not
                    # this is not the correct way to do this, ideally we would like to be able to send the breakpoint message directly
                    self.gdb.last_bp = getattr(ql.arch, 'effective_pc', ql.arch.regs.arch_pc)
                    # print("{0:08x}".format(self.gdb.last_bp))

                self.__access_information_collector()

                self.context_mmio()
            else:
                self.seen=False
                self.__access_information_collector()


            #if there exists a pile that means, that this value has been provided in the file
            # this check has tricked me, the elif is executed even if we are dealing with a write and we don't want that, I modified the condition for it to be executed only when the access 
            # is a read  
            # print(self.current_pile)
            # print("seen value is "+str(self.__check_seen_value(addr,size)))
            # print("access is "+str(self.track_list[-1]["access"]))
            # print("address is {0:08x}".format(addr))
            if self.current_pile is not None:
                try : 
                    # print("I popped the value")
                    last_element = self.current_pile.pop(0)
                    ql.mem.write(addr,last_element.to_bytes(size, 'little'))    
                except IndexError: 
                    # if the addr and size have already been accessed
                    last_element = ql.mem.read_ptr(addr, size)
                # print("hellooo")
                self.__add_line_to_dump(self.output_providing_map,last_element)
                self.piled_value=True
            # otherwise, it's an access to that a provided has been given by an interactive way 
            elif self.__check_seen_value(addr,size) and self.track_list[-1]["access"]==16: 
                # print("jellpo")
                last_element = ql.mem.read_ptr(addr, size)
                self.__add_line_to_dump(self.output_providing_map,last_element)
                self.piled_value=True
            else:
                self.__add_line_to_dump(self.output_providing_map,0)
                # print("else")
        else: 
            self.seen = False
            # print("seen value is "+str(self.__check_seen_value(addr,size)))
            # print("access is "+str(self.track_list[-1]["access"]))
            # print("address is {0:08x}".format(addr))
            

    #These are both commands that are required for the gdbserver usage but not for Qdb
    def do_provide(self, ql, line : str, context=None): 
        """
        Case description : 
        1. coming from mmio_handler => 'o'
        2. coming from a precedent do_provide (ie the user want to overwrite an already do_provide value) => "a" 
            -> We check if the corresponding acces is a read type
            -> Try to convert the provided address 
            -> We check if the address and size are mapped  
            -> Write the provided value into the memory 
            -> add the value to the output providing dump, __add_line_to_dump is using the piled_value variable
            -> 
    
            
        1. a pile is present, non empty, we need to overwrite the value in the render and change the value in the dump
        2. an empty pile is present, we need to write the value in the memory and add it to the dump 
        3. No pile is present, 
        """
    
        if self.track_list[-1].get("access")==16:
            addr = self.track_list[-1].get("addr")
            size = self.track_list[-1].get("size")
            try :
                int_val = int(line,16)
            except ValueError: 
                print("[+] ERROR impossible to convert the provided address")
                self.context_mmio()                     
            if ((int_val.bit_length() + 7) // 8) > size:
                print(f"[!] ERROR Value provided too large for the mmio access size")
                self.context_mmio()                    
            else:
                if ql.mem.is_mapped(addr, size): 
                    ql.mem.write(addr, int_val.to_bytes(size, 'little'))   
                    self.__add_line_to_dump(self.output_providing_map,int_val)

                    # just for the render
                    try : 
                        pile = self.track_list[-1].get("pile")
                        if pile !=[]: 
                            self.__overwrite_value(int_val)
                    except KeyError: 
                        pass
                
                    # to update the curr_value rendered 
                    self.track_list[-1]["curr_value"] = ql.mem.read(self.track_list[-1]["addr"],self.track_list[-1]["size"])
                    if context is not None: 
                        context()
                    self.context_mmio()
                else : 
                    print(f"[!] ERROR Memory not mapped")

        elif self.track_list[-1].get("access")==17:
            print(f"[!] ERROR This is a write")
            self.context_mmio()

    def add_name(self, line : str, context=None)->None:
        mmio_map = self.get_map()

        if self.track_list[-1]["addr"] in mmio_map and self.track_list[-1]["size"] == mmio_map[self.track_list[-1]["addr"]]["size"]: 
            mmio_map[self.track_list[-1]["addr"]]["name"] = line
        elif self.track_list[-1]["addr"] not in mmio_map: 
            mmio_map[self.track_list[-1]["addr"]] = {"size": self.track_list[-1]["size"], "name":line}
        
        self.track_list[-1]["name"]=line
        if context is not None: 
            context()


    def restore(self): 
        providing_map = self.get_providing_map() 
        for addr in providing_map: 
            for size in providing_map[addr]: 
                while providing_map[addr][size]: 
                    self.__add_line_to_dump(self.output_providing_map, providing_map[addr][size].pop(0), int(addr), int(size))
        