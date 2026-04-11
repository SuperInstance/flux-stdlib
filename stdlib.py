"""
FLUX Standard Library — common programs pre-compiled to bytecodes.
"""
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class ProgramCategory(Enum):
    MATH = "math"
    SORT = "sort"
    SEARCH = "search"
    CRYPTO = "crypto"
    STRING = "string"
    FLEET = "fleet"
    SENSOR = "sensor"
    UTILITY = "utility"


@dataclass
class FluxProgram:
    name: str
    category: ProgramCategory
    description: str
    bytecode: List[int]
    inputs: List[str]
    outputs: List[str]
    cycles_estimate: int = 0
    size_bytes: int = 0
    author: str = "stdlib"
    
    def __post_init__(self):
        self.size_bytes = len(self.bytecode)
    
    def run(self, initial_regs: Dict[int, int] = None) -> Dict[int, int]:
        regs = [0] * 64
        stack = [0] * 4096
        sp = 4096
        pc = 0
        halted = False
        cycles = 0
        
        if initial_regs:
            for k, v in initial_regs.items():
                regs[k] = v
        
        def sb(b): return b - 256 if b > 127 else b
        
        while not halted and pc < len(self.bytecode) and cycles < 100000:
            bc = self.bytecode
            op = bc[pc]
            cycles += 1
            if op == 0x00: halted = True; pc += 1
            elif op == 0x01: pc += 1
            elif op == 0x08: regs[bc[pc+1]] += 1; pc += 2
            elif op == 0x09: regs[bc[pc+1]] -= 1; pc += 2
            elif op == 0x0B: rd = bc[pc+1]; regs[rd] = -regs[rd]; pc += 2
            elif op == 0x0C: sp -= 1; stack[sp] = regs[bc[pc+1]]; pc += 2
            elif op == 0x0D: regs[bc[pc+1]] = stack[sp]; sp += 1; pc += 2
            elif op == 0x18: regs[bc[pc+1]] = sb(bc[pc+2]); pc += 3
            elif op == 0x19: regs[bc[pc+1]] += sb(bc[pc+2]); pc += 3
            elif op == 0x20: regs[bc[pc+1]] = regs[bc[pc+2]] + regs[bc[pc+3]]; pc += 4
            elif op == 0x21: regs[bc[pc+1]] = regs[bc[pc+2]] - regs[bc[pc+3]]; pc += 4
            elif op == 0x22: regs[bc[pc+1]] = regs[bc[pc+2]] * regs[bc[pc+3]]; pc += 4
            elif op == 0x23:
                if regs[bc[pc+3]] != 0: regs[bc[pc+1]] = regs[bc[pc+2]] // regs[bc[pc+3]]
                pc += 4
            elif op == 0x24: regs[bc[pc+1]] = regs[bc[pc+2]] % regs[bc[pc+3]]; pc += 4
            elif op == 0x2C: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] == regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x2D: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] < regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x2E: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] > regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x3A: regs[bc[pc+1]] = regs[bc[pc+2]]; pc += 4
            elif op == 0x3C:
                if regs[bc[pc+1]] == 0: pc += sb(bc[pc+2])
                else: pc += 4
            elif op == 0x3D:
                if regs[bc[pc+1]] != 0: pc += sb(bc[pc+2])
                else: pc += 4
            else: pc += 1
        return {i: regs[i] for i in range(16)}


PROGRAMS = {}

def _r(name, cat, desc, bc, inp, out):
    PROGRAMS[name] = FluxProgram(name=name, category=cat, description=desc, bytecode=bc, inputs=inp, outputs=out)

# ── MATH ──
_r("abs", ProgramCategory.MATH, "Absolute value: |R0| -> R0",
   [0x18,1,0, 0x2D,2,0,1, 0x3C,2,2,0, 0x0B,0, 0x00],
   ["R0"], ["R0"])

_r("max", ProgramCategory.MATH, "Maximum: max(R0,R1) -> R2",
   [0x3A,2,1,0, 0x2E,3,0,1, 0x3C,3,2,0, 0x3A,2,0,0, 0x00],
   ["R0","R1"], ["R2"])

_r("min", ProgramCategory.MATH, "Minimum: min(R0,R1) -> R2",
   [0x3A,2,1,0, 0x2D,3,0,1, 0x3C,3,2,0, 0x3A,2,0,0, 0x00],
   ["R0","R1"], ["R2"])

_r("factorial", ProgramCategory.MATH, "Factorial: R0! -> R1. Handles 0!=1.",
   [0x18,1,1, 0x18,5,0, 0x2C,2,0,5, 0x3C,2,5,0, 0x00,
    0x22,1,1,0, 0x09,0, 0x18,4,1, 0x3D,4,-18&0xFF,0, 0x00],
   ["R0"], ["R1"])

_r("power", ProgramCategory.MATH, "Power: R0^R1 -> R2",
   [0x18,2,1, 0x22,2,2,0, 0x09,1, 0x3D,1,-6&0xFF,0, 0x00],
   ["R0","R1"], ["R2"])

_r("fibonacci", ProgramCategory.MATH, "Fibonacci: R2 iterations -> R1",
   [0x20,3,0,1, 0x3A,0,1,0, 0x3A,1,3,0, 0x09,2, 0x3D,2,-14&0xFF,0, 0x00],
   ["R0","R1","R2"], ["R1"])

_r("gcd", ProgramCategory.MATH, "GCD: gcd(R0,R1) -> R0. Euclidean.",
   [0x18,5,0, 0x2C,2,1,5, 0x3C,2,5,0, 0x00,
    0x24,3,0,1, 0x3A,0,1,0, 0x3A,1,3,0, 0x18,4,1, 0x3D,4,-24&0xFF,0, 0x00],
   ["R0","R1"], ["R0"])

_r("sum_to_n", ProgramCategory.MATH, "Sum 1..R0 -> R1",
   [0x18,1,0, 0x20,1,1,0, 0x09,0, 0x3D,0,-6&0xFF,0, 0x00],
   ["R0"], ["R1"])

# ── UTILITY ──
_r("swap", ProgramCategory.UTILITY, "Swap R0 and R1 via stack",
   [0x0C,0, 0x0C,1, 0x0D,0, 0x0D,1, 0x00],
   ["R0","R1"], ["R0","R1"])

_r("copy", ProgramCategory.UTILITY, "Copy R0 to R1",
   [0x3A,1,0,0, 0x00], ["R0"], ["R1"])

_r("negate", ProgramCategory.UTILITY, "Negate R0",
   [0x0B,0, 0x00], ["R0"], ["R0"])

_r("double", ProgramCategory.UTILITY, "Double R0",
   [0x20,0,0,0, 0x00], ["R0"], ["R0"])

_r("square", ProgramCategory.UTILITY, "Square R0 -> R1",
   [0x22,1,0,0, 0x00], ["R0"], ["R1"])


import unittest

class TestStdlib(unittest.TestCase):
    def test_factorial(self):
        result = PROGRAMS["factorial"].run({0: 6})
        self.assertEqual(result[1], 720)
    
    def test_factorial_zero(self):
        result = PROGRAMS["factorial"].run({0: 0})
        self.assertEqual(result[1], 1)
    
    def test_power(self):
        result = PROGRAMS["power"].run({0: 2, 1: 10})
        self.assertEqual(result[2], 1024)
    
    def test_swap(self):
        result = PROGRAMS["swap"].run({0: 42, 1: 99})
        self.assertEqual(result[0], 99)
        self.assertEqual(result[1], 42)
    
    def test_copy(self):
        result = PROGRAMS["copy"].run({0: 42})
        self.assertEqual(result[1], 42)
    
    def test_negate(self):
        result = PROGRAMS["negate"].run({0: 42})
        self.assertEqual(result[0], -42)
    
    def test_double(self):
        result = PROGRAMS["double"].run({0: 21})
        self.assertEqual(result[0], 42)
    
    def test_square(self):
        result = PROGRAMS["square"].run({0: 12})
        self.assertEqual(result[1], 144)
    
    def test_max(self):
        r1 = PROGRAMS["max"].run({0: 10, 1: 20})
        self.assertEqual(r1[2], 20)
        r2 = PROGRAMS["max"].run({0: 30, 1: 20})
        self.assertEqual(r2[2], 30)
    
    def test_min(self):
        r1 = PROGRAMS["min"].run({0: 10, 1: 20})
        self.assertEqual(r1[2], 10)
        r2 = PROGRAMS["min"].run({0: 30, 1: 20})
        self.assertEqual(r2[2], 20)
    
    def test_sum_to_n(self):
        result = PROGRAMS["sum_to_n"].run({0: 100})
        self.assertEqual(result[1], 5050)
    
    def test_gcd(self):
        result = PROGRAMS["gcd"].run({0: 48, 1: 18})
        self.assertEqual(result[0], 6)
    
    def test_gcd_coprime(self):
        result = PROGRAMS["gcd"].run({0: 17, 1: 13})
        self.assertEqual(result[0], 1)
    
    def test_program_count(self):
        self.assertGreaterEqual(len(PROGRAMS), 10)
    
    def test_all_have_category(self):
        for p in PROGRAMS.values():
            self.assertIsInstance(p.category, ProgramCategory)
    
    def test_all_have_description(self):
        for p in PROGRAMS.values():
            self.assertGreater(len(p.description), 0)
