#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

cortexm3 = {
    "SRAM BB": {
        "base": 0x22000000,
        "struct": "CortexMBitband",
        "type": "core",
        "kwargs":  {
            "base": 0x20000000,
            "size": 0x100000,
        }
    },
    "PERIP BB": {
        "base": 0x42000000,
        "struct": "CortexMBitband",
        "type": "core",
        "kwargs":  {
            "base": 0x40000000,
            "size": 0x100000,
        }
    },
    "SYSTICK": {
        "base": 0xe000e010,
        "struct": "CortexM3SysTick",
        "type": "core"
    },
    "NVIC": {
        "base": 0xe000e100,
        "struct": "CortexM3Nvic",
        "type": "core"
    },
    "SCB": {
        "base": 0xe000ed00,
        "struct": "CortexM3Scb",
        "type": "core"
    },
    "FLASH": {
        "base": 0x8000000,
        "size": 0x20000,
        "type": "memory"
    },
    "SYSTEM": {
        "base": 0x1ffff000,
        "size": 0x1000,
        "type": "memory"
    },
    "SRAM": {
        "base": 0x20000000,
        "size": 0x5000,
        "type": "memory"
    },
    "REMAP": {
        "base": 0x0,
        "struct": "MemoryRemap",
        "type": "core",
        "kwargs":  {
            "base": 0x8000000,
            "size": 0x80000,
        }
    },
    "REMAP REGION": {
        "base": 0x0,
        "size": 0x80000,
        "type": "mmio",
    }
}