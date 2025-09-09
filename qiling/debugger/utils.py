#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#



from qiling import Qiling

from .adds.mmio_tracker.tracker import MMIOTracker
from .adds.hook_handler.hook_handler import HookHandler
from .adds.memory_mapper.memory_mapper import MemoryMapper
from typing import Optional
import json, os
from qiling.const import QL_ARCH
from typing import TYPE_CHECKING, Callable, Dict, Mapping, Tuple, Type
from ..exception import QlErrorFileNotFound,QlErrorJsonDecode

from .adds.subroutine_tracker import (
    SubroutineTracker,
    SubroutineTrackerARM, 
    SubroutineTrackerCORTEX_M
)

def __int_nothrow(v: str, /) -> Optional[int]:
    try:
        return int(v, 0)
    except ValueError:
        return None

def __convert_list(addr_hook:list = None) -> Optional[dict]:
        
        hook_list = []

        for t in addr_hook: 
            hook_list.append((__int_nothrow(t[0]),(__int_nothrow(t[1]))))
        return hook_list

def retrieve_json_with_key(key:str = None):
    filename = "MMIO_Tracker_config.json"
    if os.path.exists(filename):
        with open(filename) as config : 
            global_config = json.loads(config.read())
            if key not in global_config:
                raise QlErrorJsonDecode(f'Key "{key}" missing in the MMIO_Tracker_config.json')
            return global_config[key]
    else: 
        raise QlErrorFileNotFound(f'MMIO_Tracker_config.json file not found')


def setup_mmio_tracker(gdb  = None, server = False, context_render=None)->MMIOTracker: 
    def __parse_mmio_map(raw_map:dict = None)->dict:
        converted_mmio_map = {}
        for key in raw_map:    
            converted_mmio_map[__int_nothrow(key)] = raw_map[key]
        return converted_mmio_map
    
    def __parse_providing_mmio_map(raw_map:dict = None)->dict:
        converted_mmio_map = {}
        converted_sub_provider_mmio_map ={}
        for key in raw_map:   
            for key2 in raw_map[key] :
                converted_sub_provider_mmio_map[__int_nothrow(key2)] = raw_map[key][key2]
            converted_mmio_map[__int_nothrow(key)] = converted_sub_provider_mmio_map
            converted_sub_provider_mmio_map = {}
        return converted_mmio_map

    converted_mmio_map=__parse_mmio_map(retrieve_json_with_key("mmio_map"))
    converted_provider_mmio_map=__parse_providing_mmio_map(retrieve_json_with_key("providing_mmio_map"))
    
    return MMIOTracker(converted_mmio_map, converted_provider_mmio_map, gdb, server, context_render)

def setup_subroutine_tracker(ql: Qiling, gdb=None) -> Optional[SubroutineTracker]:

    preds: Dict[QL_ARCH, Type[SubroutineTracker]] = {
        QL_ARCH.ARM:      SubroutineTrackerARM,
        QL_ARCH.CORTEX_M:      SubroutineTrackerCORTEX_M,
    }

    p = preds[ql.arch.type]

    subroutine_names = retrieve_json_with_key("subroutine_map")
    if subroutine_names == {}:
        subroutine_names = None

    return p(ql, subroutine_names, gdb)

def setup_hook_handler()->HookHandler: 

    unconverted_hook_list = retrieve_json_with_key("hook_list")
    if unconverted_hook_list == []:
        raise QlErrorJsonDecode(f'Hook_list empty in the MMIO_Tracker_config.json')

    hook_list = __convert_list(unconverted_hook_list)

    return HookHandler(hook_list)


def setup_memory_mapper(): 

    memory_mapping = __convert_list(retrieve_json_with_key("memory_mapping"))

    return MemoryMapper(memory_mapping)