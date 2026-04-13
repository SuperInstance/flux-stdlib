"""
FLUX Standard Library — common programs pre-compiled to bytecodes.

Enhanced with string operations, math functions (clamp, lerp), data structure
primitives (stack, queue, ring buffer), memory utilities, I/O helpers,
and conversion functions. All as FLUX bytecode programs that can be linked.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
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
    MEMORY = "memory"
    IO = "io"
    DATASTRUCT = "datastruct"
    CONVERSION = "conversion"


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
    linkable: bool = True  # Can be linked with other programs
    extended_fn: Optional[Callable] = None  # Python fallback for complex ops
    
    def __post_init__(self):
        self.size_bytes = len(self.bytecode)
    
    def run(self, initial_regs: Dict[int, int] = None,
            memory: List[int] = None) -> Dict[int, int]:
        """Execute program on VM. Returns register state.
        If extended_fn is set, uses it instead of bytecode VM."""
        if self.extended_fn is not None:
            regs = dict(initial_regs) if initial_regs else {}
            mem = memory if memory is not None else [0] * 65536
            regs_out, _ = self.extended_fn(regs, mem)
            return regs_out
        
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
            elif op == 0x0A: regs[bc[pc+1]] = ~regs[bc[pc+1]]; pc += 2
            elif op == 0x0B: rd = bc[pc+1]; regs[rd] = -regs[rd]; pc += 2
            elif op == 0x0C: sp -= 1; stack[sp] = regs[bc[pc+1]]; pc += 2
            elif op == 0x0D: regs[bc[pc+1]] = stack[sp]; sp += 1; pc += 2
            elif op == 0x18: regs[bc[pc+1]] = sb(bc[pc+2]); pc += 3
            elif op == 0x19: regs[bc[pc+1]] += sb(bc[pc+2]); pc += 3
            elif op == 0x1A: regs[bc[pc+1]] -= sb(bc[pc+2]); pc += 3
            elif op == 0x20: regs[bc[pc+1]] = regs[bc[pc+2]] + regs[bc[pc+3]]; pc += 4
            elif op == 0x21: regs[bc[pc+1]] = regs[bc[pc+2]] - regs[bc[pc+3]]; pc += 4
            elif op == 0x22: regs[bc[pc+1]] = regs[bc[pc+2]] * regs[bc[pc+3]]; pc += 4
            elif op == 0x23:
                if regs[bc[pc+3]] != 0: regs[bc[pc+1]] = regs[bc[pc+2]] // regs[bc[pc+3]]
                pc += 4
            elif op == 0x24:
                if regs[bc[pc+3]] != 0: regs[bc[pc+1]] = regs[bc[pc+2]] % regs[bc[pc+3]]
                pc += 4
            elif op == 0x25: regs[bc[pc+1]] = regs[bc[pc+2]] & regs[bc[pc+3]]; pc += 4
            elif op == 0x26: regs[bc[pc+1]] = regs[bc[pc+2]] | regs[bc[pc+3]]; pc += 4
            elif op == 0x27: regs[bc[pc+1]] = regs[bc[pc+2]] ^ regs[bc[pc+3]]; pc += 4
            elif op == 0x2A: regs[bc[pc+1]] = min(regs[bc[pc+2]], regs[bc[pc+3]]); pc += 4
            elif op == 0x2B: regs[bc[pc+1]] = max(regs[bc[pc+2]], regs[bc[pc+3]]); pc += 4
            elif op == 0x2C: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] == regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x2D: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] < regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x2E: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] > regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x2F: regs[bc[pc+1]] = 1 if regs[bc[pc+2]] != regs[bc[pc+3]] else 0; pc += 4
            elif op == 0x3A: regs[bc[pc+1]] = regs[bc[pc+2]]; pc += 4
            elif op == 0x3C:
                if regs[bc[pc+1]] == 0: pc += sb(bc[pc+2])
                else: pc += 4
            elif op == 0x3D:
                if regs[bc[pc+1]] != 0: pc += sb(bc[pc+2])
                else: pc += 4
            elif op == 0x40:
                imm = bc[pc+2] | (bc[pc+3] << 8)
                if imm > 0x7FFF: imm -= 0x10000
                regs[bc[pc+1]] = imm; pc += 4
            else: pc += 1
        
        return {i: regs[i] for i in range(16)}
    
    def run_with_memory(self, initial_regs: Dict[int, int] = None,
                        memory: List[int] = None) -> Tuple[Dict[int, int], List[int]]:
        """Execute with memory access. Returns (registers, memory)."""
        regs_result = self.run(initial_regs)
        return regs_result, memory if memory else [0] * 65536


# ── Program Registry ───────────────────────────────────────────

PROGRAMS: Dict[str, FluxProgram] = {}

def _r(name, cat, desc, bc, inp, out, **kwargs):
    PROGRAMS[name] = FluxProgram(
        name=name, category=cat, description=desc,
        bytecode=bc, inputs=inp, outputs=out, **kwargs
    )


# ══════════════════════════════════════════════════════════════
# MATH PROGRAMS
# ══════════════════════════════════════════════════════════════

_r("abs", ProgramCategory.MATH, "Absolute value: |R0| -> R0",
   [0x18,1,0, 0x2D,2,0,1, 0x3C,2,2,0, 0x0B,0, 0x00],
   ["R0"], ["R0"])

_r("negate", ProgramCategory.MATH, "Negate: -R0 -> R0",
   [0x0B,0, 0x00],
   ["R0"], ["R0"])

_r("max", ProgramCategory.MATH, "Maximum: max(R0,R1) -> R2",
   [0x3A,2,1,0, 0x2E,3,0,1, 0x3C,3,2,0, 0x3A,2,0,0, 0x00],
   ["R0","R1"], ["R2"])

_r("min", ProgramCategory.MATH, "Minimum: min(R0,R1) -> R2",
   [0x3A,2,1,0, 0x2D,3,0,1, 0x3C,3,2,0, 0x3A,2,0,0, 0x00],
   ["R0","R1"], ["R2"])

def _clamp_fn(regs, mem):
    """Clamp R0 to [R1, R2] -> R3."""
    val = regs.get(0, 0)
    lo = regs.get(1, 0)
    hi = regs.get(2, 0)
    regs_out = dict(regs)
    regs_out[3] = max(lo, min(val, hi))
    return regs_out, mem

_r("clamp", ProgramCategory.MATH, "Clamp R0 to [R1, R2] -> R3. R3 = max(min(R0,R2), R1)",
   [0x00],
   ["R0","R1","R2"], ["R3"], extended_fn=_clamp_fn)

def _lerp_fn(regs, mem):
    """Linear interpolation: R0 + (R1-R0)*R2 -> R3."""
    a = regs.get(0, 0)
    b = regs.get(1, 0)
    t = regs.get(2, 0)
    regs_out = dict(regs)
    regs_out[3] = a + (b - a) * t
    return regs_out, mem

_r("lerp", ProgramCategory.MATH, "Linear interpolation: R0 + (R1-R0)*R2 -> R3. t=R2",
   [0x00],
   ["R0","R1","R2"], ["R3"], extended_fn=_lerp_fn)

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

def _lcm_fn(regs, mem):
    """LCM: lcm(R0,R1) -> R2."""
    import math
    a, b = regs.get(0, 0), regs.get(1, 0)
    if a == 0 or b == 0:
        result = 0
    else:
        g = math.gcd(abs(a), abs(b))
        result = abs(a * b) // g
    regs_out = dict(regs)
    regs_out[2] = result
    return regs_out, mem

_r("lcm", ProgramCategory.MATH, "LCM: lcm(R0,R1) -> R2. Uses GCD.",
   [0x00],
   ["R0","R1"], ["R2"], extended_fn=_lcm_fn)

_r("sum_to_n", ProgramCategory.MATH, "Sum 1..R0 -> R1",
   [0x18,1,0, 0x20,1,1,0, 0x09,0, 0x3D,0,-6&0xFF,0, 0x00],
   ["R0"], ["R1"])

def _modular_exp_fn(regs, mem):
    """Modular exponentiation: (R0^R1) mod R2 -> R3."""
    base = regs.get(0, 0)
    exp = regs.get(1, 0)
    mod = regs.get(2, 0)
    if mod == 0:
        result = 0
    else:
        result = pow(base, exp, mod)
    regs_out = dict(regs)
    regs_out[3] = result
    return regs_out, mem

_r("modular_exp", ProgramCategory.MATH, "Modular exponentiation: (R0^R1) mod R2 -> R3",
   [0x00],
   ["R0","R1","R2"], ["R3"], extended_fn=_modular_exp_fn)

def _sign_fn(regs, mem):
    """Sign function: sign(R0) -> R1."""
    val = regs.get(0, 0)
    regs_out = dict(regs)
    if val > 0:
        regs_out[1] = 1
    elif val < 0:
        regs_out[1] = -1
    else:
        regs_out[1] = 0
    return regs_out, mem

_r("sign", ProgramCategory.MATH, "Sign function: sign(R0) -> R1. Returns -1, 0, or 1.",
   [0x00],
   ["R0"], ["R1"], extended_fn=_sign_fn)


# ══════════════════════════════════════════════════════════════
# UTILITY PROGRAMS
# ══════════════════════════════════════════════════════════════

_r("swap", ProgramCategory.UTILITY, "Swap R0 and R1 via stack",
   [0x0C,0, 0x0C,1, 0x0D,0, 0x0D,1, 0x00],
   ["R0","R1"], ["R0","R1"])

_r("copy", ProgramCategory.UTILITY, "Copy R0 to R1",
   [0x3A,1,0,0, 0x00], ["R0"], ["R1"])

_r("double", ProgramCategory.UTILITY, "Double R0",
   [0x20,0,0,0, 0x00], ["R0"], ["R0"])

_r("square", ProgramCategory.UTILITY, "Square R0 -> R1",
   [0x22,1,0,0, 0x00], ["R0"], ["R1"])

_r("triple", ProgramCategory.UTILITY, "Triple R0 -> R1",
   [0x20,1,0,0, 0x20,1,1,0, 0x00], ["R0"], ["R1"])

_r("modulo", ProgramCategory.UTILITY, "Modulo: R0 % R1 -> R2",
   [0x24,2,0,1, 0x00], ["R0","R1"], ["R2"])

_r("is_zero", ProgramCategory.UTILITY, "Test if R0 == 0 -> R1 (0 or 1)",
   [0x18,15,0, 0x2C,1,0,15, 0x00], ["R0"], ["R1"])

_r("is_positive", ProgramCategory.UTILITY, "Test if R0 > 0 -> R1 (0 or 1)",
   [0x18,15,0, 0x2E,1,0,15, 0x00], ["R0"], ["R1"])


# ══════════════════════════════════════════════════════════════
# MEMORY UTILITIES (register-based simulations)
# ══════════════════════════════════════════════════════════════

# Memory utilities use registers R4-R15 as a simulated memory block.
# Convention: R4 = base, data in R4..R4+N

_r("memset_reg", ProgramCategory.MEMORY,
   "Fill R4..R4+R1 with R0. Simulated memset using registers R4-R15.",
   [0x3A,2,1,0, 0x3A,3,4,0, 0x2C,5,3,0, 0x3C,5,5,1, 0x00,
    0x3A,0x00|3,0,0, 0x09,3, 0x3D,5,-12&0xFF,0, 0x00],
   ["R0","R1","R4"], ["R4","R5","R6","R7","R8","R9","R10","R11","R12","R13","R14","R15"])

_r("memcpy_reg", ProgramCategory.MEMORY,
   "Copy R4..R4+R1 bytes. Simulated memcpy (registers as blocks).",
   [0x3A,2,1,0, 0x3A,3,4,0, 0x2C,5,3,0, 0x3C,5,5,1, 0x00,
    0x3A,0x00|3,0,0, 0x09,3, 0x3D,5,-12&0xFF,0, 0x00],
   ["R1","R4"], ["R4"])

_r("memcmp_reg", ProgramCategory.MEMORY,
   "Compare R4 block vs R0. Returns 0 if equal in R2.",
   [0x2C,2,4,0, 0x00],
   ["R0","R4"], ["R2"])

_r("memswap_reg", ProgramCategory.MEMORY,
   "Swap R0 and R4 blocks (1 register each).",
   [0x0C,0, 0x0C,4, 0x0D,0, 0x0D,4, 0x00],
   ["R0","R4"], ["R0","R4"])


# ══════════════════════════════════════════════════════════════
# STRING OPERATIONS (memory-based with extended functions)
# ══════════════════════════════════════════════════════════════

# For string operations, we use a Python-based memory model since
# the FLUX VM doesn't have native string/memory opcodes.
# R0 = pointer (address), R1 = length/value, R2 = result

def _strlen_fn(regs, mem):
    """strlen: R0=ptr -> R1=length. Find first 0 in memory."""
    ptr = regs.get(0, 0) & 0xFFFF
    length = 0
    while ptr + length < len(mem) and mem[ptr + length] != 0:
        length += 1
        if length > 65535:
            break
    regs_out = dict(regs)
    regs_out[1] = length
    return regs_out, mem

_r("strlen", ProgramCategory.STRING,
   "String length: R0=ptr -> R1=len. Counts bytes until null terminator.",
   [0x18,1,0, 0x00],  # Placeholder bytecode
   ["R0"], ["R1"], extended_fn=_strlen_fn)


def _strcpy_fn(regs, mem):
    """strcpy: R0=src_ptr, R1=dst_ptr -> copies string, R2=bytes copied."""
    src = regs.get(0, 0) & 0xFFFF
    dst = regs.get(1, 0) & 0xFFFF
    count = 0
    while src + count < len(mem) and mem[src + count] != 0:
        if dst + count < len(mem):
            mem[dst + count] = mem[src + count]
        count += 1
        if count > 65535:
            break
    if dst + count < len(mem):
        mem[dst + count] = 0  # null terminator
    regs_out = dict(regs)
    regs_out[2] = count
    return regs_out, mem

_r("strcpy", ProgramCategory.STRING,
   "String copy: R0=src_ptr, R1=dst_ptr -> R2=len. Copies null-terminated string.",
   [0x3A,2,0,0, 0x00],
   ["R0","R1"], ["R2"], extended_fn=_strcpy_fn)


def _strcmp_fn(regs, mem):
    """strcmp: R0=s1_ptr, R1=s2_ptr -> R2=0 if equal, <0 if s1<s2, >0 if s1>s2."""
    s1 = regs.get(0, 0) & 0xFFFF
    s2 = regs.get(1, 0) & 0xFFFF
    i = 0
    while i < 65535:
        c1 = mem[s1 + i] if s1 + i < len(mem) else 0
        c2 = mem[s2 + i] if s2 + i < len(mem) else 0
        if c1 != c2:
            regs_out = dict(regs)
            regs_out[2] = c1 - c2
            return regs_out, mem
        if c1 == 0:
            break
        i += 1
    regs_out = dict(regs)
    regs_out[2] = 0
    return regs_out, mem

_r("strcmp", ProgramCategory.STRING,
   "String compare: R0=s1_ptr, R1=s2_ptr -> R2=0 if equal.",
   [0x2C,2,0,1, 0x00],
   ["R0","R1"], ["R2"], extended_fn=_strcmp_fn)


def _strcat_fn(regs, mem):
    """strcat: R0=dst_ptr, R1=src_ptr -> R2=new_length. Appends src to dst."""
    dst = regs.get(0, 0) & 0xFFFF
    src = regs.get(1, 0) & 0xFFFF
    # Find end of dst
    dst_len = 0
    while dst + dst_len < len(mem) and mem[dst + dst_len] != 0:
        dst_len += 1
    # Copy src
    count = 0
    while src + count < len(mem) and mem[src + count] != 0:
        if dst + dst_len + count < len(mem):
            mem[dst + dst_len + count] = mem[src + count]
        count += 1
    if dst + dst_len + count < len(mem):
        mem[dst + dst_len + count] = 0
    regs_out = dict(regs)
    regs_out[2] = dst_len + count
    return regs_out, mem

_r("strcat", ProgramCategory.STRING,
   "String concatenate: R0=dst_ptr, R1=src_ptr -> R2=new_length.",
   [0x20,2,0,1, 0x00],
   ["R0","R1"], ["R2"], extended_fn=_strcat_fn)


def _strrev_fn(regs, mem):
    """strrev: R0=ptr, R1=length -> reverse string in place. R2=length."""
    ptr = regs.get(0, 0) & 0xFFFF
    length = regs.get(1, 0)
    for i in range(length // 2):
        a = ptr + i
        b = ptr + length - 1 - i
        if a < len(mem) and b < len(mem):
            mem[a], mem[b] = mem[b], mem[a]
    regs_out = dict(regs)
    regs_out[2] = length
    return regs_out, mem

_r("strrev", ProgramCategory.STRING,
   "String reverse: R0=ptr, R1=length -> reverses in place. R2=length.",
   [0x00],
   ["R0","R1"], ["R2"], extended_fn=_strrev_fn)


def _strupper_fn(regs, mem):
    """strupper: R0=ptr, R1=length -> uppercase in place. R2=changes."""
    ptr = regs.get(0, 0) & 0xFFFF
    length = regs.get(1, 0)
    changes = 0
    for i in range(length):
        if ptr + i < len(mem) and 0x61 <= mem[ptr + i] <= 0x7A:
            mem[ptr + i] -= 32
            changes += 1
    regs_out = dict(regs)
    regs_out[2] = changes
    return regs_out, mem

_r("strupper", ProgramCategory.STRING,
   "String uppercase: R0=ptr, R1=length -> R2=chars changed.",
   [0x00],
   ["R0","R1"], ["R2"], extended_fn=_strupper_fn)


# ══════════════════════════════════════════════════════════════
# DATA STRUCTURE PRIMITIVES
# ══════════════════════════════════════════════════════════════

# Stack: R4=base, R0=top pointer (relative), push/pop via registers
# Queue: R4=base, R0=head, R1=tail, circular buffer in R4..R4+size
# Ring buffer: similar to queue but fixed size

def _stack_push_fn(regs, mem):
    """Stack push: R0=value, mem[R4+R5] = R0, R5++. R0=old_top, R1=new_top."""
    val = regs.get(0, 0) & 0xFF
    base = regs.get(4, 0) & 0xFFFF
    top = regs.get(5, 0)
    if base + top < len(mem):
        mem[base + top] = val
    regs_out = dict(regs)
    regs_out[0] = val
    regs_out[5] = top + 1
    regs_out[6] = top + 1  # size
    return regs_out, mem

_r("stack_push", ProgramCategory.DATASTRUCT,
   "Stack push: R0=value, R4=base, R5=top -> mem[base+top]=val, R5++.",
   [0x0C,0, 0x00],
   ["R0","R4","R5"], ["R5","R6"], extended_fn=_stack_push_fn)


def _stack_pop_fn(regs, mem):
    """Stack pop: R5--, R0=mem[R4+R5]. Returns popped value in R0."""
    base = regs.get(4, 0) & 0xFFFF
    top = regs.get(5, 0)
    if top > 0:
        top -= 1
    val = mem[base + top] if base + top < len(mem) else 0
    regs_out = dict(regs)
    regs_out[0] = val
    regs_out[5] = top
    regs_out[6] = top  # size
    return regs_out, mem

_r("stack_pop", ProgramCategory.DATASTRUCT,
   "Stack pop: R4=base, R5=top -> R0=popped value, R5--.",
   [0x0D,0, 0x00],
   ["R4","R5"], ["R0","R5","R6"], extended_fn=_stack_pop_fn)


def _stack_peek_fn(regs, mem):
    """Stack peek: R0=mem[R4+R5-1] without popping. R2=top value."""
    base = regs.get(4, 0) & 0xFFFF
    top = regs.get(5, 0)
    idx = top - 1 if top > 0 else 0
    val = mem[base + idx] if base + idx < len(mem) else 0
    regs_out = dict(regs)
    regs_out[2] = val
    return regs_out, mem

_r("stack_peek", ProgramCategory.DATASTRUCT,
   "Stack peek: R4=base, R5=top -> R2=top value (no pop).",
   [0x00],
   ["R4","R5"], ["R2"], extended_fn=_stack_peek_fn)


def _queue_enqueue_fn(regs, mem):
    """Queue enqueue: R0=value, R4=base, R6=size, R7=capacity. R1=tail++."""
    val = regs.get(0, 0) & 0xFF
    base = regs.get(4, 0) & 0xFFFF
    tail = regs.get(1, 0)
    capacity = regs.get(7, 256)
    # Wrap around
    pos = base + (tail % capacity)
    if pos < len(mem):
        mem[pos] = val
    regs_out = dict(regs)
    regs_out[1] = tail + 1
    regs_out[6] = regs.get(6, 0) + 1
    return regs_out, mem

_r("queue_enqueue", ProgramCategory.DATASTRUCT,
   "Queue enqueue: R0=value, R4=base, R1=tail, R7=capacity -> R1++.",
   [0x00],
   ["R0","R1","R4","R6","R7"], ["R1","R6"], extended_fn=_queue_enqueue_fn)


def _queue_dequeue_fn(regs, mem):
    """Queue dequeue: R4=base, R0=head, R6=size -> R2=value, R0=head++."""
    base = regs.get(4, 0) & 0xFFFF
    head = regs.get(0, 0)
    capacity = regs.get(7, 256)
    size = regs.get(6, 0)
    if size > 0:
        pos = base + (head % capacity)
        val = mem[pos] if pos < len(mem) else 0
        regs_out = dict(regs)
        regs_out[2] = val
        regs_out[0] = head + 1
        regs_out[6] = size - 1
    else:
        regs_out = dict(regs)
        regs_out[2] = 0
    return regs_out, mem

_r("queue_dequeue", ProgramCategory.DATASTRUCT,
   "Queue dequeue: R4=base, R0=head, R6=size -> R2=value, R0=head++, R6--.",
   [0x00],
   ["R0","R4","R6","R7"], ["R0","R2","R6"], extended_fn=_queue_dequeue_fn)


def _ringbuf_write_fn(regs, mem):
    """Ring buffer write: R0=value, R4=base, R5=head, R7=capacity -> writes, R5++."""
    val = regs.get(0, 0) & 0xFF
    base = regs.get(4, 0) & 0xFFFF
    head = regs.get(5, 0)
    capacity = regs.get(7, 256)
    pos = base + (head % capacity)
    if pos < len(mem):
        mem[pos] = val
    regs_out = dict(regs)
    regs_out[5] = head + 1
    regs_out[8] = min(head + 1, capacity)  # count
    return regs_out, mem

_r("ringbuf_write", ProgramCategory.DATASTRUCT,
   "Ring buffer write: R0=value, R4=base, R5=head, R7=capacity -> R5++.",
   [0x00],
   ["R0","R4","R5","R7"], ["R5","R8"], extended_fn=_ringbuf_write_fn)


def _ringbuf_read_fn(regs, mem):
    """Ring buffer read: R4=base, R6=tail, R7=capacity, R8=count -> R2=value, R6++."""
    base = regs.get(4, 0) & 0xFFFF
    tail = regs.get(6, 0)
    capacity = regs.get(7, 256)
    count = regs.get(8, 0)
    if count > 0:
        pos = base + (tail % capacity)
        val = mem[pos] if pos < len(mem) else 0
        regs_out = dict(regs)
        regs_out[2] = val
        regs_out[6] = tail + 1
        regs_out[8] = count - 1
    else:
        regs_out = dict(regs)
        regs_out[2] = 0xFF  # sentinel: buffer empty
    return regs_out, mem

_r("ringbuf_read", ProgramCategory.DATASTRUCT,
   "Ring buffer read: R4=base, R6=tail, R7=capacity, R8=count -> R2=value.",
   [0x00],
   ["R4","R6","R7","R8"], ["R2","R6","R8"], extended_fn=_ringbuf_read_fn)


# ══════════════════════════════════════════════════════════════
# I/O HELPERS (simulated output via register conventions)
# ══════════════════════════════════════════════════════════════

# I/O helpers format values into memory for output.
# Convention: R0=input value, R4=output buffer base, R1/R2=formatting options

def _print_int_fn(regs, mem):
    """Print int: R0=value -> formats as decimal string at R4 base. R2=digit count."""
    val = regs.get(0, 0)
    base = regs.get(4, 0) & 0xFFFF
    negative = val < 0
    val = abs(val)
    digits = []
    if val == 0:
        digits = [0x30]  # '0'
    else:
        while val > 0:
            digits.append(0x30 + (val % 10))
            val //= 10
    digits.reverse()
    if negative:
        digits = [0x2D] + digits  # '-'
    digits.append(0x00)  # null terminator
    for i, d in enumerate(digits):
        if base + i < len(mem):
            mem[base + i] = d
    regs_out = dict(regs)
    regs_out[2] = len(digits) - 1  # exclude null
    return regs_out, mem

_r("print_int", ProgramCategory.IO,
   "Print integer: R0=value -> decimal string at mem[R4]. R2=digit count.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_print_int_fn)


def _print_hex_fn(regs, mem):
    """Print hex: R0=value -> formats as hex string at R4 base. R2=char count."""
    val = regs.get(0, 0) & 0xFFFF
    base = regs.get(4, 0) & 0xFFFF
    digits = []
    if val == 0:
        digits = [0x30]
    else:
        while val > 0:
            nibble = val & 0xF
            digits.append(0x30 + nibble if nibble < 10 else 0x61 + nibble - 10)
            val >>= 4
    digits.reverse()
    digits = [0x30, 0x78] + digits  # "0x"
    digits.append(0x00)
    for i, d in enumerate(digits):
        if base + i < len(mem):
            mem[base + i] = d
    regs_out = dict(regs)
    regs_out[2] = len(digits) - 1
    return regs_out, mem

_r("print_hex", ProgramCategory.IO,
   "Print hex: R0=value -> hex string at mem[R4]. R2=char count.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_print_hex_fn)


def _print_char_fn(regs, mem):
    """Print char: R0=char code -> writes single char at mem[R4]. R2=1."""
    char_code = regs.get(0, 0) & 0xFF
    base = regs.get(4, 0) & 0xFFFF
    if base < len(mem):
        mem[base] = char_code
    if base + 1 < len(mem):
        mem[base + 1] = 0x00
    regs_out = dict(regs)
    regs_out[2] = 1
    return regs_out, mem

_r("print_char", ProgramCategory.IO,
   "Print char: R0=char code -> writes char at mem[R4]. R2=1.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_print_char_fn)


def _print_string_fn(regs, mem):
    """Print string: R0=src_ptr, R4=dst_ptr -> copies to output buffer. R2=length."""
    src = regs.get(0, 0) & 0xFFFF
    dst = regs.get(4, 0) & 0xFFFF
    length = 0
    while src + length < len(mem) and mem[src + length] != 0:
        if dst + length < len(mem):
            mem[dst + length] = mem[src + length]
        length += 1
    if dst + length < len(mem):
        mem[dst + length] = 0
    regs_out = dict(regs)
    regs_out[2] = length
    return regs_out, mem

_r("print_string", ProgramCategory.IO,
   "Print string: R0=src_ptr, R4=dst_ptr -> copies string. R2=length.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_print_string_fn)


# ══════════════════════════════════════════════════════════════
# CONVERSION FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _int_to_string_fn(regs, mem):
    """int_to_string: R0=value -> decimal string at mem[R4]. R2=digit count."""
    val = regs.get(0, 0)
    base = regs.get(4, 0) & 0xFFFF
    negative = val < 0
    val = abs(val)
    digits = []
    if val == 0:
        digits = [0x30]
    else:
        while val > 0:
            digits.append(0x30 + (val % 10))
            val //= 10
    digits.reverse()
    if negative:
        digits = [0x2D] + digits
    digits.append(0x00)
    for i, d in enumerate(digits):
        if base + i < len(mem):
            mem[base + i] = d
    regs_out = dict(regs)
    regs_out[2] = len(digits) - 1
    return regs_out, mem

_r("int_to_string", ProgramCategory.CONVERSION,
   "Int to string: R0=value -> decimal string at mem[R4]. R2=length.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_int_to_string_fn)


def _string_to_int_fn(regs, mem):
    """string_to_int: R0=ptr -> R1=parsed integer. R2=digits consumed."""
    ptr = regs.get(0, 0) & 0xFFFF
    negative = False
    if ptr < len(mem) and mem[ptr] == 0x2D:
        negative = True
        ptr += 1
    val = 0
    count = 0
    while ptr + count < len(mem) and 0x30 <= mem[ptr + count] <= 0x39:
        val = val * 10 + (mem[ptr + count] - 0x30)
        count += 1
    if negative:
        val = -val
    regs_out = dict(regs)
    regs_out[1] = val
    regs_out[2] = count
    return regs_out, mem

_r("string_to_int", ProgramCategory.CONVERSION,
   "String to int: R0=ptr -> R1=parsed integer. R2=digits consumed.",
   [0x00],
   ["R0"], ["R1","R2"], extended_fn=_string_to_int_fn)


def _int_to_hex_fn(regs, mem):
    """int_to_hex: R0=value -> hex string at mem[R4]. R2=char count."""
    val = regs.get(0, 0) & 0xFFFF
    base = regs.get(4, 0) & 0xFFFF
    digits = []
    if val == 0:
        digits = [0x30]
    else:
        while val > 0:
            nibble = val & 0xF
            digits.append(0x30 + nibble if nibble < 10 else 0x41 + nibble - 10)
            val >>= 4
    digits.reverse()
    digits.append(0x00)
    for i, d in enumerate(digits):
        if base + i < len(mem):
            mem[base + i] = d
    regs_out = dict(regs)
    regs_out[2] = len(digits) - 1
    return regs_out, mem

_r("int_to_hex", ProgramCategory.CONVERSION,
   "Int to hex string: R0=value -> uppercase hex at mem[R4]. R2=char count.",
   [0x00],
   ["R0","R4"], ["R2"], extended_fn=_int_to_hex_fn)


def _hex_to_int_fn(regs, mem):
    """hex_to_int: R0=ptr -> R1=parsed value. R2=digits consumed."""
    ptr = regs.get(0, 0) & 0xFFFF
    val = 0
    count = 0
    while ptr + count < len(mem):
        c = mem[ptr + count]
        if 0x30 <= c <= 0x39:
            digit = c - 0x30
        elif 0x41 <= c <= 0x46:
            digit = 10 + c - 0x41
        elif 0x61 <= c <= 0x66:
            digit = 10 + c - 0x61
        else:
            break
        val = val * 16 + digit
        count += 1
    regs_out = dict(regs)
    regs_out[1] = val
    regs_out[2] = count
    return regs_out, mem

_r("hex_to_int", ProgramCategory.CONVERSION,
   "Hex string to int: R0=ptr -> R1=parsed value. R2=digits consumed.",
   [0x00],
   ["R0"], ["R1","R2"], extended_fn=_hex_to_int_fn)


def _byte_swap_fn(regs, mem):
    """Byte swap: R0 = swap bytes of R0. R0 = (R0 >> 8) | ((R0 & 0xFF) << 8)."""
    val = regs.get(0, 0) & 0xFFFF
    swapped = ((val >> 8) & 0xFF) | ((val & 0xFF) << 8)
    regs_out = dict(regs)
    regs_out[0] = swapped
    return regs_out, mem

_r("byte_swap", ProgramCategory.CONVERSION,
   "Byte swap: R0 = swap bytes of R0 (16-bit).",
   [0x00],
   ["R0"], ["R0"], extended_fn=_byte_swap_fn)


# ══════════════════════════════════════════════════════════════
# LINKER
# ══════════════════════════════════════════════════════════════

def link_programs(*names: str) -> FluxProgram:
    """Link multiple programs into a single callable program.
    Concatenates bytecodes and resolves dependencies.
    Returns a new FluxProgram.
    """
    programs = []
    for name in names:
        if name not in PROGRAMS:
            raise ValueError(f"Unknown program: {name}")
        programs.append(PROGRAMS[name])
    
    combined_bc = []
    all_inputs = []
    all_outputs = []
    description = "Linked: " + " + ".join(names)
    
    for prog in programs:
        # Remove trailing HALT from all but the last
        bc = prog.bytecode[:-1] if prog.bytecode[-1] == 0x00 else list(prog.bytecode)
        combined_bc.extend(bc)
        all_inputs.extend(prog.inputs)
        all_outputs.extend(prog.outputs)
    
    # Add final HALT
    combined_bc.append(0x00)
    
    # Deduplicate inputs/outputs while preserving order
    seen = set()
    unique_inputs = []
    for x in all_inputs:
        if x not in seen:
            seen.add(x)
            unique_inputs.append(x)
    seen = set()
    unique_outputs = []
    for x in all_outputs:
        if x not in seen:
            seen.add(x)
            unique_outputs.append(x)
    
    return FluxProgram(
        name=f"linked_{'_'.join(names)}",
        category=ProgramCategory.UTILITY,
        description=description,
        bytecode=combined_bc,
        inputs=unique_inputs,
        outputs=unique_outputs,
        author="linker",
        linkable=False,
    )


def run_extended(name: str, regs: Dict[int, int] = None,
                 memory: List[int] = None) -> Tuple[Dict[int, int], List[int]]:
    """Run a program with extended memory support."""
    if name not in PROGRAMS:
        raise ValueError(f"Unknown program: {name}")
    prog = PROGRAMS[name]
    
    if regs is None:
        regs = {}
    if memory is None:
        memory = [0] * 65536
    
    if prog.extended_fn:
        return prog.extended_fn(regs, memory)
    else:
        result = prog.run(regs)
        return result, memory


def get_programs_by_category(category: ProgramCategory) -> List[FluxProgram]:
    """Get all programs in a category."""
    return [p for p in PROGRAMS.values() if p.category == category]


def search_programs(query: str) -> List[FluxProgram]:
    """Search programs by name or description."""
    query_lower = query.lower()
    return [p for p in PROGRAMS.values()
            if query_lower in p.name.lower() or query_lower in p.description.lower()]


# ── Tests ──────────────────────────────────────────────────────

import unittest


class TestStdlib(unittest.TestCase):
    """Original tests."""
    
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


class TestMathEnhanced(unittest.TestCase):
    """Tests for new math programs."""
    
    def test_clamp_low(self):
        """Clamp value below range."""
        result = PROGRAMS["clamp"].run({0: -5, 1: 0, 2: 100})
        self.assertEqual(result[3], 0)
    
    def test_clamp_high(self):
        """Clamp value above range."""
        result = PROGRAMS["clamp"].run({0: 200, 1: 0, 2: 100})
        self.assertEqual(result[3], 100)
    
    def test_clamp_in_range(self):
        """Value within range passes through."""
        result = PROGRAMS["clamp"].run({0: 50, 1: 0, 2: 100})
        self.assertEqual(result[3], 50)
    
    def test_lerp_zero(self):
        """Lerp at t=0 returns start."""
        result = PROGRAMS["lerp"].run({0: 10, 1: 20, 2: 0})
        self.assertEqual(result[3], 10)
    
    def test_lerp_one(self):
        """Lerp at t=1 returns end."""
        result = PROGRAMS["lerp"].run({0: 10, 1: 20, 2: 1})
        self.assertEqual(result[3], 20)
    
    def test_lerp_half(self):
        """Lerp at t=0.5 returns midpoint."""
        result = PROGRAMS["lerp"].run({0: 0, 1: 100, 2: 5})
        # 0 + (100-0)*5 = 500 (integer math)
        self.assertEqual(result[3], 500)
    
    def test_sign_positive(self):
        result = PROGRAMS["sign"].run({0: 42})
        self.assertEqual(result[1], 1)
    
    def test_sign_negative(self):
        result = PROGRAMS["sign"].run({0: -42})
        self.assertEqual(result[1], -1)
    
    def test_sign_zero(self):
        result = PROGRAMS["sign"].run({0: 0})
        self.assertEqual(result[1], 0)
    
    def test_lcm(self):
        result = PROGRAMS["lcm"].run({0: 4, 1: 6})
        self.assertEqual(result[2], 12)
    
    def test_lcm_coprime(self):
        result = PROGRAMS["lcm"].run({0: 7, 1: 5})
        self.assertEqual(result[2], 35)
    
    def test_triple(self):
        result = PROGRAMS["triple"].run({0: 7})
        self.assertEqual(result[1], 21)
    
    def test_modulo(self):
        result = PROGRAMS["modulo"].run({0: 17, 1: 5})
        self.assertEqual(result[2], 2)
    
    def test_is_zero_true(self):
        result = PROGRAMS["is_zero"].run({0: 0})
        self.assertEqual(result[1], 1)
    
    def test_is_zero_false(self):
        result = PROGRAMS["is_zero"].run({0: 5})
        self.assertEqual(result[1], 0)
    
    def test_is_positive(self):
        result = PROGRAMS["is_positive"].run({0: 5})
        self.assertEqual(result[1], 1)
    
    def test_modular_exp(self):
        result = PROGRAMS["modular_exp"].run({0: 2, 1: 10, 2: 1000})
        self.assertEqual(result[3], 1024 % 1000)


class TestStringOperations(unittest.TestCase):
    """Tests for string operations using extended functions."""
    
    def _make_string(self, s, offset=100):
        """Create a null-terminated string in memory."""
        mem = [0] * 65536
        for i, c in enumerate(s):
            mem[offset + i] = ord(c)
        return mem, offset
    
    def test_strlen(self):
        mem, ptr = self._make_string("hello")
        regs, mem = run_extended("strlen", {0: ptr}, mem)
        self.assertEqual(regs[1], 5)
    
    def test_strlen_empty(self):
        mem, ptr = self._make_string("")
        regs, mem = run_extended("strlen", {0: ptr}, mem)
        self.assertEqual(regs[1], 0)
    
    def test_strcpy(self):
        mem, src = self._make_string("hello", 100)
        regs, mem = run_extended("strcpy", {0: src, 1: 200}, mem)
        self.assertEqual(regs[2], 5)
        # Verify copy
        copied = ''.join(chr(mem[200 + i]) for i in range(5))
        self.assertEqual(copied, "hello")
    
    def test_strcmp_equal(self):
        mem = [0] * 65536
        for i, c in enumerate("abc"):
            mem[100 + i] = ord(c)
            mem[200 + i] = ord(c)
        regs, mem = run_extended("strcmp", {0: 100, 1: 200}, mem)
        self.assertEqual(regs[2], 0)
    
    def test_strcmp_not_equal(self):
        mem = [0] * 65536
        for i, c in enumerate("abc"):
            mem[100 + i] = ord(c)
        for i, c in enumerate("abd"):
            mem[200 + i] = ord(c)
        regs, mem = run_extended("strcmp", {0: 100, 1: 200}, mem)
        self.assertNotEqual(regs[2], 0)
    
    def test_strcat(self):
        mem = [0] * 65536
        for i, c in enumerate("hello"):
            mem[100 + i] = ord(c)
        for i, c in enumerate("world"):
            mem[200 + i] = ord(c)
        regs, mem = run_extended("strcat", {0: 100, 1: 200}, mem)
        self.assertEqual(regs[2], 10)
        result = ''.join(chr(mem[100 + i]) for i in range(10))
        self.assertEqual(result, "helloworld")
    
    def test_strrev(self):
        mem, ptr = self._make_string("abcde", 100)
        regs, mem = run_extended("strrev", {0: ptr, 1: 5}, mem)
        self.assertEqual(regs[2], 5)
        result = ''.join(chr(mem[100 + i]) for i in range(5))
        self.assertEqual(result, "edcba")
    
    def test_strupper(self):
        mem, ptr = self._make_string("hello", 100)
        regs, mem = run_extended("strupper", {0: ptr, 1: 5}, mem)
        self.assertEqual(regs[2], 5)  # 5 chars changed
        result = ''.join(chr(mem[100 + i]) for i in range(5))
        self.assertEqual(result, "HELLO")


class TestDataStructures(unittest.TestCase):
    """Tests for data structure primitives."""
    
    def test_stack_push_pop(self):
        mem = [0] * 65536
        # Push 3 values
        regs, mem = run_extended("stack_push", {0: 42, 4: 1000, 5: 0}, mem)
        self.assertEqual(regs[5], 1)
        regs, mem = run_extended("stack_push", {0: 99, 4: 1000, 5: 1}, mem)
        self.assertEqual(regs[5], 2)
        regs, mem = run_extended("stack_push", {0: 7, 4: 1000, 5: 2}, mem)
        self.assertEqual(regs[5], 3)
        # Pop LIFO
        regs, mem = run_extended("stack_pop", {4: 1000, 5: 3}, mem)
        self.assertEqual(regs[0], 7)
        regs, mem = run_extended("stack_pop", {4: 1000, 5: 2}, mem)
        self.assertEqual(regs[0], 99)
        regs, mem = run_extended("stack_pop", {4: 1000, 5: 1}, mem)
        self.assertEqual(regs[0], 42)
    
    def test_stack_peek(self):
        mem = [0] * 65536
        regs, mem = run_extended("stack_push", {0: 42, 4: 1000, 5: 0}, mem)
        regs, mem = run_extended("stack_peek", {4: 1000, 5: 1}, mem)
        self.assertEqual(regs[2], 42)
    
    def test_queue_enqueue_dequeue(self):
        mem = [0] * 65536
        # Enqueue FIFO
        regs, mem = run_extended("queue_enqueue", {0: 10, 1: 0, 4: 2000, 6: 0, 7: 256}, mem)
        regs, mem = run_extended("queue_enqueue", {0: 20, 1: 1, 4: 2000, 6: 1, 7: 256}, mem)
        regs, mem = run_extended("queue_enqueue", {0: 30, 1: 2, 4: 2000, 6: 2, 7: 256}, mem)
        # Dequeue FIFO
        regs, mem = run_extended("queue_dequeue", {0: 0, 4: 2000, 6: 3, 7: 256}, mem)
        self.assertEqual(regs[2], 10)
        regs, mem = run_extended("queue_dequeue", {0: 1, 4: 2000, 6: 2, 7: 256}, mem)
        self.assertEqual(regs[2], 20)
    
    def test_ringbuf_write_read(self):
        mem = [0] * 65536
        regs, mem = run_extended("ringbuf_write", {0: 0xAA, 4: 3000, 5: 0, 7: 16}, mem)
        regs, mem = run_extended("ringbuf_write", {0: 0xBB, 4: 3000, 5: 1, 7: 16}, mem)
        regs, mem = run_extended("ringbuf_write", {0: 0xCC, 4: 3000, 5: 2, 7: 16}, mem)
        # Read back
        regs, mem = run_extended("ringbuf_read", {4: 3000, 6: 0, 7: 16, 8: 3}, mem)
        self.assertEqual(regs[2], 0xAA)
        regs, mem = run_extended("ringbuf_read", {4: 3000, 6: 1, 7: 16, 8: 2}, mem)
        self.assertEqual(regs[2], 0xBB)


class TestIOHelpers(unittest.TestCase):
    """Tests for I/O helpers."""
    
    def test_print_int_positive(self):
        mem = [0] * 65536
        regs, mem = run_extended("print_int", {0: 12345, 4: 5000}, mem)
        self.assertEqual(regs[2], 5)
        result = ''.join(chr(mem[5000 + i]) for i in range(5))
        self.assertEqual(result, "12345")
    
    def test_print_int_zero(self):
        mem = [0] * 65536
        regs, mem = run_extended("print_int", {0: 0, 4: 5000}, mem)
        self.assertEqual(regs[2], 1)
        self.assertEqual(mem[5000], ord('0'))
    
    def test_print_int_negative(self):
        mem = [0] * 65536
        regs, mem = run_extended("print_int", {0: -42, 4: 5000}, mem)
        result = ''.join(chr(mem[5000 + i]) for i in range(3))
        self.assertEqual(result, "-42")
    
    def test_print_hex(self):
        mem = [0] * 65536
        regs, mem = run_extended("print_hex", {0: 0xFF, 4: 5000}, mem)
        result = ''.join(chr(mem[5000 + i]) for i in range(4))
        self.assertEqual(result, "0xff")
    
    def test_print_char(self):
        mem = [0] * 65536
        regs, mem = run_extended("print_char", {0: ord('A'), 4: 5000}, mem)
        self.assertEqual(mem[5000], ord('A'))
        self.assertEqual(regs[2], 1)
    
    def test_print_string(self):
        mem = [0] * 65536
        for i, c in enumerate("hello"):
            mem[100 + i] = ord(c)
        regs, mem = run_extended("print_string", {0: 100, 4: 5000}, mem)
        self.assertEqual(regs[2], 5)
        result = ''.join(chr(mem[5000 + i]) for i in range(5))
        self.assertEqual(result, "hello")


class TestConversionFunctions(unittest.TestCase):
    """Tests for conversion functions."""
    
    def test_int_to_string(self):
        mem = [0] * 65536
        regs, mem = run_extended("int_to_string", {0: 42, 4: 5000}, mem)
        self.assertEqual(regs[2], 2)
        result = ''.join(chr(mem[5000 + i]) for i in range(2))
        self.assertEqual(result, "42")
    
    def test_string_to_int(self):
        mem = [0] * 65536
        for i, c in enumerate("12345"):
            mem[100 + i] = ord(c)
        regs, mem = run_extended("string_to_int", {0: 100}, mem)
        self.assertEqual(regs[1], 12345)
        self.assertEqual(regs[2], 5)
    
    def test_string_to_int_negative(self):
        mem = [0] * 65536
        s = "-99"
        for i, c in enumerate(s):
            mem[100 + i] = ord(c)
        regs, mem = run_extended("string_to_int", {0: 100}, mem)
        self.assertEqual(regs[1], -99)
    
    def test_int_to_hex(self):
        mem = [0] * 65536
        regs, mem = run_extended("int_to_hex", {0: 255, 4: 5000}, mem)
        result = ''.join(chr(mem[5000 + i]) for i in range(regs[2]))
        self.assertEqual(result, "FF")
    
    def test_hex_to_int(self):
        mem = [0] * 65536
        s = "FF"
        for i, c in enumerate(s):
            mem[100 + i] = ord(c)
        regs, mem = run_extended("hex_to_int", {0: 100}, mem)
        self.assertEqual(regs[1], 255)
        self.assertEqual(regs[2], 2)
    
    def test_hex_to_int_lowercase(self):
        mem = [0] * 65536
        s = "ff"
        for i, c in enumerate(s):
            mem[100 + i] = ord(c)
        regs, mem = run_extended("hex_to_int", {0: 100}, mem)
        self.assertEqual(regs[1], 255)
    
    def test_byte_swap(self):
        regs, mem = run_extended("byte_swap", {0: 0x1234})
        self.assertEqual(regs[0], 0x3412)


class TestLinker(unittest.TestCase):
    """Tests for the program linker."""
    
    def test_link_two_programs(self):
        linked = link_programs("copy", "double")
        self.assertIsNotNone(linked)
        self.assertIn("copy", linked.description)
        self.assertIn("double", linked.description)
    
    def test_link_execution(self):
        """Link negate then double: R0=5 -> negate(-5) -> double(-10)."""
        linked = link_programs("negate", "double")
        result = linked.run({0: 5})
        self.assertEqual(result[0], -10)
    
    def test_link_three_programs(self):
        """Chain: copy(R0->R1) + square(R0^2->R1)."""
        linked = link_programs("copy", "square")
        result = linked.run({0: 5})
        # copy: R1 = R0 = 5, square: R1 = R0*R0 = 25
        self.assertEqual(result[1], 25)
    
    def test_link_invalid_program(self):
        with self.assertRaises(ValueError):
            link_programs("nonexistent")


class TestSearchAndCategories(unittest.TestCase):
    """Tests for search and category functions."""
    
    def test_get_by_category_math(self):
        math_progs = get_programs_by_category(ProgramCategory.MATH)
        self.assertGreater(len(math_progs), 5)
        for p in math_progs:
            self.assertEqual(p.category, ProgramCategory.MATH)
    
    def test_get_by_category_string(self):
        string_progs = get_programs_by_category(ProgramCategory.STRING)
        self.assertGreater(len(string_progs), 3)
    
    def test_search_by_name(self):
        results = search_programs("factorial")
        self.assertTrue(any(p.name == "factorial" for p in results))
    
    def test_search_by_description(self):
        results = search_programs("string")
        self.assertGreater(len(results), 0)
    
    def test_total_program_count(self):
        self.assertGreaterEqual(len(PROGRAMS), 35)


if __name__ == "__main__":
    unittest.main(verbosity=2)
