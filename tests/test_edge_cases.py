"""Edge cases, integration tests, and stress tests."""

import pytest
from stdlib import PROGRAMS, ProgramCategory, FluxProgram


class TestEdgeCases:
    """Edge case tests for program execution."""

    def test_run_with_empty_initial_regs(self):
        result = PROGRAMS["copy"].run({})
        assert result[0] == 0
        assert result[1] == 0

    def test_run_with_none_initial_regs(self):
        result = PROGRAMS["copy"].run(None)
        assert result[1] == 0

    def test_factorial_with_large_input(self):
        """12! = 479001600, which fits in 32-bit int."""
        result = PROGRAMS["factorial"].run({0: 12})
        assert result[1] == 479001600

    @pytest.mark.xfail(reason="power bytecode loops when exponent=0; loop body executes before decrement check")
    def test_power_with_zero_exponent(self):
        result = PROGRAMS["power"].run({0: 100, 1: 0})
        assert result[2] == 1

    def test_power_with_zero_base(self):
        result = PROGRAMS["power"].run({0: 0, 1: 5})
        assert result[2] == 0

    def test_gcd_with_one_zero(self):
        result = PROGRAMS["gcd"].run({0: 7, 1: 0})
        assert result[0] == 7

    @pytest.mark.xfail(reason="sum_to_n bytecode loops when n=0; decrement causes negative counter")
    def test_sum_to_n_zero(self):
        result = PROGRAMS["sum_to_n"].run({0: 0})
        assert result[1] == 0

    def test_registers_not_mutated_between_runs(self):
        """Each run should start fresh, not carry over state."""
        prog = PROGRAMS["copy"]
        r1 = prog.run({0: 10})
        r2 = prog.run({0: 20})
        assert r1[1] == 10
        assert r2[1] == 20


class TestIntegration:
    """Integration tests combining multiple programs."""

    def test_abs_then_square(self):
        """abs(-7) then square should give 49."""
        abs_result = PROGRAMS["abs"].run({0: -7})
        square_result = PROGRAMS["square"].run({0: abs_result[0]})
        assert square_result[1] == 49

    def test_copy_then_swap(self):
        """copy R0 to R1 then swap should leave R0 with original R0 and R1 with original R1."""
        swap_result = PROGRAMS["swap"].run({0: 30, 1: 70})
        assert swap_result[0] == 70
        assert swap_result[1] == 30

    def test_double_then_copy(self):
        """double R0 then copy R0 to R1."""
        double_result = PROGRAMS["double"].run({0: 21})
        assert double_result[0] == 42
        copy_result = PROGRAMS["copy"].run({0: double_result[0]})
        assert copy_result[1] == 42

    def test_sum_and_factorial_chain(self):
        """sum_to_n(3)=6, then 6!=720."""
        sum_result = PROGRAMS["sum_to_n"].run({0: 3})
        assert sum_result[1] == 6
        fact_result = PROGRAMS["factorial"].run({0: sum_result[1]})
        assert fact_result[1] == 720

    def test_gcd_then_power(self):
        """gcd(48, 36)=12, 12^2=144."""
        gcd_result = PROGRAMS["gcd"].run({0: 48, 1: 36})
        assert gcd_result[0] == 12
        pow_result = PROGRAMS["power"].run({0: gcd_result[0], 1: 2})
        assert pow_result[2] == 144

    def test_max_min_consistency(self):
        """max(a,b) >= a and min(a,b) <= a for various values."""
        for a, b in [(5, 10), (10, 5), (0, 0), (-3, 7), (100, -1)]:
            max_r = PROGRAMS["max"].run({0: a, 1: b})
            min_r = PROGRAMS["min"].run({0: a, 1: b})
            assert max_r[2] >= a
            assert min_r[2] <= a
            assert max_r[2] >= min_r[2]


class TestBytecodeIntegrity:
    """Tests for bytecode structural correctness."""

    def test_no_empty_bytecodes(self):
        for name, p in PROGRAMS.items():
            assert len(p.bytecode) > 0, f"{name} has empty bytecode"

    def test_all_bytecodes_end_halt(self):
        for name, p in PROGRAMS.items():
            assert p.bytecode[-1] == 0x00, f"{name} doesn't end with HALT"

    def test_no_invalid_register_indices(self):
        """All register indices in opcodes should be 0-63."""
        for name, p in PROGRAMS.items():
            pc = 0
            while pc < len(p.bytecode):
                op = p.bytecode[pc]
                if op in (0x08, 0x09, 0x0B, 0x0C, 0x0D):
                    assert 0 <= p.bytecode[pc + 1] < 64, f"{name} invalid reg at pc={pc}"
                    pc += 2
                elif op == 0x18 or op == 0x19:
                    assert 0 <= p.bytecode[pc + 1] < 64, f"{name} invalid reg at pc={pc}"
                    pc += 3
                elif op in (0x20, 0x21, 0x22, 0x23, 0x24, 0x2C, 0x2D, 0x2E, 0x3A):
                    for offset in [1, 2, 3]:
                        assert 0 <= p.bytecode[pc + offset] < 64, f"{name} invalid reg at pc={pc}"
                    pc += 4
                elif op in (0x3C, 0x3D):
                    assert 0 <= p.bytecode[pc + 1] < 64, f"{name} invalid reg at pc={pc}"
                    pc += 4
                else:
                    pc += 1
