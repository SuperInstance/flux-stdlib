"""Tests for the FluxProgram dataclass."""

import pytest
from stdlib import FluxProgram, ProgramCategory


class TestFluxProgramInit:
    """Tests for FluxProgram initialization and defaults."""

    def test_basic_creation(self):
        prog = FluxProgram(
            name="test",
            category=ProgramCategory.MATH,
            description="Test program",
            bytecode=[0x00],
            inputs=["R0"],
            outputs=["R0"],
        )
        assert prog.name == "test"
        assert prog.category == ProgramCategory.MATH
        assert prog.description == "Test program"
        assert prog.bytecode == [0x00]
        assert prog.inputs == ["R0"]
        assert prog.outputs == ["R0"]

    def test_default_cycles_estimate(self):
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        assert prog.cycles_estimate == 0

    def test_default_size_bytes(self):
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        assert prog.size_bytes == 1  # post_init computes from bytecode length

    def test_default_author(self):
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        assert prog.author == "stdlib"

    def test_size_bytes_from_bytecode(self):
        bc = [0x18, 1, 0, 0x00]
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=bc, inputs=[], outputs=[],
        )
        assert prog.size_bytes == len(bc)

    def test_empty_bytecode(self):
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[], inputs=[], outputs=[],
        )
        assert prog.size_bytes == 0

    def test_large_bytecode_size(self):
        bc = [0x00] * 1000
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=bc, inputs=[], outputs=[],
        )
        assert prog.size_bytes == 1000


class TestFluxProgramRun:
    """Tests for FluxProgram.run() method."""

    def test_halt_opcode(self):
        """Program with just HALT (0x00) should return all-zero registers."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        result = prog.run()
        assert all(v == 0 for v in result.values())

    def test_noop_opcode(self):
        """NOP (0x01) should not change registers."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x01, 0x01, 0x00], inputs=[], outputs=[],
        )
        result = prog.run()
        assert all(v == 0 for v in result.values())

    def test_initial_registers_passed(self):
        """initial_regs should set register values before execution."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        result = prog.run({0: 42, 5: 99})
        assert result[0] == 42
        assert result[5] == 99

    def test_initial_regs_none(self):
        """None as initial_regs should result in all-zero registers."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        result = prog.run(None)
        assert all(v == 0 for v in result.values())

    def test_increment_opcode(self):
        """INCR R0 (0x08, 0) should increment register 0."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x08, 0, 0x00], inputs=["R0"], outputs=["R0"],
        )
        result = prog.run({0: 10})
        assert result[0] == 11

    def test_decrement_opcode(self):
        """DECR R0 (0x09, 0) should decrement register 0."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x09, 0, 0x00], inputs=["R0"], outputs=["R0"],
        )
        result = prog.run({0: 10})
        assert result[0] == 9

    def test_negate_opcode(self):
        """NEG R0 (0x0B, 0) should negate register 0."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x0B, 0, 0x00], inputs=["R0"], outputs=["R0"],
        )
        result = prog.run({0: 42})
        assert result[0] == -42

    def test_negate_zero(self):
        """Negating zero should still be zero."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x0B, 0, 0x00], inputs=["R0"], outputs=["R0"],
        )
        result = prog.run({0: 0})
        assert result[0] == 0

    def test_add_opcode(self):
        """ADD R2, R0, R1 (0x20, 2, 0, 1) should set R2 = R0 + R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[0x20, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 30, 1: 12})
        assert result[2] == 42

    def test_sub_opcode(self):
        """SUB R2, R0, R1 (0x21, 2, 0, 1) should set R2 = R0 - R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[0x21, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 50, 1: 8})
        assert result[2] == 42

    def test_mul_opcode(self):
        """MUL R1, R0, R0 (0x22, 1, 0, 0) should set R1 = R0 * R0."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[0x22, 1, 0, 0, 0x00], inputs=["R0"], outputs=["R1"],
        )
        result = prog.run({0: 7})
        assert result[1] == 49

    def test_div_opcode(self):
        """DIV R1, R0, R1 (0x23, 1, 0, 1) should set R1 = R0 // R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[0x23, 1, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R1"],
        )
        result = prog.run({0: 20, 1: 3})
        assert result[1] == 6

    def test_mod_opcode(self):
        """MOD R1, R0, R1 (0x24, 1, 0, 1) should set R1 = R0 % R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.MATH, description="d",
            bytecode=[0x24, 1, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R1"],
        )
        result = prog.run({0: 20, 1: 3})
        assert result[1] == 2

    def test_eq_opcode_true(self):
        """EQ R2, R0, R1 (0x2C) should set R2 = 1 when R0 == R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2C, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 42, 1: 42})
        assert result[2] == 1

    def test_eq_opcode_false(self):
        """EQ R2, R0, R1 should set R2 = 0 when R0 != R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2C, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 42, 1: 7})
        assert result[2] == 0

    def test_lt_opcode_true(self):
        """LT R2, R0, R1 should set R2 = 1 when R0 < R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2D, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 5, 1: 10})
        assert result[2] == 1

    def test_lt_opcode_false(self):
        """LT R2, R0, R1 should set R2 = 0 when R0 >= R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2D, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 10, 1: 5})
        assert result[2] == 0

    def test_gt_opcode_true(self):
        """GT R2, R0, R1 should set R2 = 1 when R0 > R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2E, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 10, 1: 5})
        assert result[2] == 1

    def test_gt_opcode_false(self):
        """GT R2, R0, R1 should set R2 = 0 when R0 <= R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x2E, 2, 0, 1, 0x00], inputs=["R0", "R1"], outputs=["R2"],
        )
        result = prog.run({0: 5, 1: 10})
        assert result[2] == 0

    def test_mov_opcode(self):
        """MOV R1, R0, R0 (0x3A, 1, 0, 0) should copy R0 to R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x3A, 1, 0, 0, 0x00], inputs=["R0"], outputs=["R1"],
        )
        result = prog.run({0: 123})
        assert result[1] == 123

    def test_push_pop(self):
        """PUSH R0 then POP R1 should move value from R0 to R1."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x0C, 0, 0x0D, 1, 0x00], inputs=["R0"], outputs=["R1"],
        )
        result = prog.run({0: 55})
        assert result[1] == 55

    def test_load_immediate(self):
        """LOADI R0, 42 (0x18, 0, 42) should set R0 = 42."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x18, 0, 42, 0x00], inputs=[], outputs=["R0"],
        )
        result = prog.run()
        assert result[0] == 42

    def test_unknown_opcode_skipped(self):
        """Unknown opcodes should be skipped (pc += 1)."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0xFF, 0x00], inputs=[], outputs=[],
        )
        result = prog.run()
        assert all(v == 0 for v in result.values())

    def test_returns_first_16_registers(self):
        """Result should always have exactly keys 0..15."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        result = prog.run()
        assert set(result.keys()) == set(range(16))

    def test_registers_beyond_16_ignored_in_result(self):
        """Registers 16+ are not in the returned dict."""
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x00], inputs=[], outputs=[],
        )
        result = prog.run()
        assert 16 not in result
        assert 63 not in result

    def test_cycle_limit(self):
        """A tight infinite loop should still halt due to cycle limit (100000)."""
        # JNZ R0, -2 (jump back 2 bytes if R0 != 0) — infinite loop
        prog = FluxProgram(
            name="t", category=ProgramCategory.UTILITY, description="d",
            bytecode=[0x18, 0, 1, 0x3D, 0, 254], inputs=[], outputs=[],
        )
        result = prog.run()  # should not hang
        assert isinstance(result, dict)
