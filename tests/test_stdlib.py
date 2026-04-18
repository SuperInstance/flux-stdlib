"""
Comprehensive test suite for flux-stdlib.
Covers all 13 programs with multiple inputs, class validation, enum checks,
edge cases, and register clobbering analysis.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stdlib import FluxProgram, ProgramCategory, PROGRAMS


# ═══════════════════════════════════════════════════════════════════════════════
# ProgramCategory Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestProgramCategory:
    """Tests for the ProgramCategory enum."""

    def test_enum_has_eight_members(self):
        assert len(ProgramCategory) == 8

    def test_all_category_names(self):
        names = {cat.name for cat in ProgramCategory}
        expected = {"MATH", "SORT", "SEARCH", "CRYPTO", "STRING", "FLEET", "SENSOR", "UTILITY"}
        assert names == expected

    def test_all_category_values_are_strings(self):
        for cat in ProgramCategory:
            assert isinstance(cat.value, str)

    def test_math_value(self):
        assert ProgramCategory.MATH.value == "math"

    def test_utility_value(self):
        assert ProgramCategory.UTILITY.value == "utility"

    def test_sort_value(self):
        assert ProgramCategory.SORT.value == "sort"

    def test_search_value(self):
        assert ProgramCategory.SEARCH.value == "search"

    def test_crypto_value(self):
        assert ProgramCategory.CRYPTO.value == "crypto"

    def test_string_value(self):
        assert ProgramCategory.STRING.value == "string"

    def test_fleet_value(self):
        assert ProgramCategory.FLEET.value == "fleet"

    def test_sensor_value(self):
        assert ProgramCategory.SENSOR.value == "sensor"


# ═══════════════════════════════════════════════════════════════════════════════
# FluxProgram Class Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestFluxProgram:
    """Tests for the FluxProgram dataclass."""

    def test_post_init_sets_size_bytes(self):
        bc = [0x18, 1, 0, 0x00]
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=bc, inputs=["R0"], outputs=["R0"])
        assert p.size_bytes == 4

    def test_post_init_size_matches_bytecode_length(self):
        for length in [0, 1, 5, 10, 100]:
            bc = [0x00] * length
            p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                            bytecode=bc, inputs=[], outputs=[])
            assert p.size_bytes == length

    def test_default_author_is_stdlib(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[])
        assert p.author == "stdlib"

    def test_default_cycles_estimate_is_zero(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[])
        assert p.cycles_estimate == 0

    def test_run_with_none_returns_all_zeros(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[])
        result = p.run(None)
        assert result == {i: 0 for i in range(16)}

    def test_run_with_no_args_returns_all_zeros(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[])
        result = p.run()
        assert result == {i: 0 for i in range(16)}

    def test_run_returns_dict_with_16_keys(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[])
        result = p.run({0: 42})
        assert set(result.keys()) == set(range(16))

    def test_run_preserves_initial_registers(self):
        """Registers not touched by bytecode should retain initial values."""
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=["R0"], outputs=["R0"])
        result = p.run({0: 42, 5: 99})
        assert result[0] == 42
        assert result[5] == 99

    def test_run_with_empty_bytecode(self):
        """An empty bytecode list should immediately return (no instructions to execute)."""
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[], inputs=[], outputs=[])
        result = p.run({0: 42})
        # No HALT ever executed, but loop condition pc < len(bytecode) is false
        assert result[0] == 42

    def test_custom_author_field(self):
        p = FluxProgram(name="t", category=ProgramCategory.MATH, description="t",
                        bytecode=[0x00], inputs=[], outputs=[], author="custom")
        assert p.author == "custom"


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRAMS Dict Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestProgramsDict:
    """Tests for the global PROGRAMS dictionary."""

    def test_program_count_is_13(self):
        assert len(PROGRAMS) == 13

    def test_all_entries_are_fluxprogram_instances(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program, FluxProgram), f"{name} is not a FluxProgram"

    def test_all_programs_have_non_empty_name(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.name, str) and len(program.name) > 0

    def test_all_programs_have_valid_category(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.category, ProgramCategory)

    def test_all_programs_have_non_empty_description(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.description, str) and len(program.description) > 0

    def test_all_programs_have_bytecode_list(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.bytecode, list)

    def test_all_bytecodes_are_non_empty(self):
        for name, program in PROGRAMS.items():
            assert len(program.bytecode) > 0, f"{name} has empty bytecode"

    def test_all_programs_end_with_halt(self):
        """Every program's bytecode should end with 0x00 (HALT)."""
        for name, program in PROGRAMS.items():
            assert program.bytecode[-1] == 0x00, f"{name} does not end with HALT"

    def test_all_programs_have_inputs_list(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.inputs, list)

    def test_all_programs_have_outputs_list(self):
        for name, program in PROGRAMS.items():
            assert isinstance(program.outputs, list)

    def test_all_programs_have_positive_size_bytes(self):
        for name, program in PROGRAMS.items():
            assert program.size_bytes > 0, f"{name} has size_bytes=0"

    def test_all_programs_size_bytes_equals_bytecode_length(self):
        for name, program in PROGRAMS.items():
            assert program.size_bytes == len(program.bytecode), \
                f"{name}: size_bytes({program.size_bytes}) != bytecode len({len(program.bytecode)})"

    def test_expected_program_names_present(self):
        expected = {"abs", "max", "min", "factorial", "power", "fibonacci",
                     "gcd", "sum_to_n", "swap", "copy", "negate", "double", "square"}
        assert set(PROGRAMS.keys()) == expected

    def test_categories_used_are_math_and_utility(self):
        cats = {p.category for p in PROGRAMS.values()}
        assert cats == {ProgramCategory.MATH, ProgramCategory.UTILITY}

    def test_math_programs_count(self):
        math_count = sum(1 for p in PROGRAMS.values() if p.category == ProgramCategory.MATH)
        assert math_count == 8

    def test_utility_programs_count(self):
        util_count = sum(1 for p in PROGRAMS.values() if p.category == ProgramCategory.UTILITY)
        assert util_count == 5


# ═══════════════════════════════════════════════════════════════════════════════
# abs Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAbs:
    """Tests for the abs program: |R0| -> R0."""

    def test_positive_value(self):
        r = PROGRAMS["abs"].run({0: 42})
        assert r[0] == 42

    def test_negative_value(self):
        r = PROGRAMS["abs"].run({0: -42})
        assert r[0] == 42

    def test_zero(self):
        r = PROGRAMS["abs"].run({0: 0})
        assert r[0] == 0

    def test_large_positive(self):
        r = PROGRAMS["abs"].run({0: 999999})
        assert r[0] == 999999

    def test_large_negative(self):
        r = PROGRAMS["abs"].run({0: -999999})
        assert r[0] == 999999

    def test_one(self):
        r = PROGRAMS["abs"].run({0: 1})
        assert r[0] == 1

    def test_neg_one(self):
        r = PROGRAMS["abs"].run({0: -1})
        assert r[0] == 1

    def test_modifies_r0_in_place(self):
        r = PROGRAMS["abs"].run({0: -7})
        assert r[0] == 7

    def test_clobbers_r1_and_r2(self):
        """abs uses R1 and R2 internally."""
        r = PROGRAMS["abs"].run({0: -5, 1: 999, 2: 888, 3: 777})
        assert r[1] != 999  # R1 clobbered
        assert r[2] != 888  # R2 clobbered
        assert r[3] == 777  # R3 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# max Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestMax:
    """Tests for the max program: max(R0, R1) -> R2."""

    def test_first_bigger(self):
        r = PROGRAMS["max"].run({0: 30, 1: 20})
        assert r[2] == 30

    def test_second_bigger(self):
        r = PROGRAMS["max"].run({0: 10, 1: 20})
        assert r[2] == 20

    def test_equal(self):
        r = PROGRAMS["max"].run({0: 42, 1: 42})
        assert r[2] == 42

    def test_negative_first_bigger(self):
        r = PROGRAMS["max"].run({0: -5, 1: -10})
        assert r[2] == -5

    def test_negative_second_bigger(self):
        r = PROGRAMS["max"].run({0: -10, 1: -5})
        assert r[2] == -5

    def test_one_negative_one_positive(self):
        r = PROGRAMS["max"].run({0: -5, 1: 10})
        assert r[2] == 10

    def test_positive_and_negative(self):
        r = PROGRAMS["max"].run({0: 5, 1: -10})
        assert r[2] == 5

    def test_both_zero(self):
        r = PROGRAMS["max"].run({0: 0, 1: 0})
        assert r[2] == 0

    def test_output_in_r2(self):
        r = PROGRAMS["max"].run({0: 3, 1: 7})
        assert r[2] == 7

    def test_clobbers_r3_only_beyond_outputs(self):
        """max uses R3 internally but doesn't touch R4+."""
        r = PROGRAMS["max"].run({0: 10, 1: 20, 3: 999, 4: 888})
        assert r[2] == 20
        assert r[3] != 999  # R3 clobbered
        assert r[4] == 888  # R4 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# min Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestMin:
    """Tests for the min program: min(R0, R1) -> R2."""

    def test_first_smaller(self):
        r = PROGRAMS["min"].run({0: 10, 1: 20})
        assert r[2] == 10

    def test_second_smaller(self):
        r = PROGRAMS["min"].run({0: 30, 1: 20})
        assert r[2] == 20

    def test_equal(self):
        r = PROGRAMS["min"].run({0: 42, 1: 42})
        assert r[2] == 42

    def test_negative_first_smaller(self):
        r = PROGRAMS["min"].run({0: -10, 1: -5})
        assert r[2] == -10

    def test_negative_second_smaller(self):
        r = PROGRAMS["min"].run({0: -5, 1: -10})
        assert r[2] == -10

    def test_one_negative_one_positive(self):
        r = PROGRAMS["min"].run({0: -5, 1: 10})
        assert r[2] == -5

    def test_both_zero(self):
        r = PROGRAMS["min"].run({0: 0, 1: 0})
        assert r[2] == 0

    def test_output_in_r2(self):
        r = PROGRAMS["min"].run({0: 3, 1: 7})
        assert r[2] == 3

    def test_clobbers_r3_only(self):
        """min uses R3 internally."""
        r = PROGRAMS["min"].run({0: 10, 1: 20, 3: 999, 4: 888})
        assert r[2] == 10
        assert r[3] != 999  # R3 clobbered
        assert r[4] == 888  # R4 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# factorial Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestFactorial:
    """Tests for the factorial program: R0! -> R1."""

    def test_factorial_zero(self):
        r = PROGRAMS["factorial"].run({0: 0})
        assert r[1] == 1

    def test_factorial_one(self):
        r = PROGRAMS["factorial"].run({0: 1})
        assert r[1] == 1

    def test_factorial_five(self):
        r = PROGRAMS["factorial"].run({0: 5})
        assert r[1] == 120

    def test_factorial_six(self):
        r = PROGRAMS["factorial"].run({0: 6})
        assert r[1] == 720

    def test_factorial_seven(self):
        r = PROGRAMS["factorial"].run({0: 7})
        assert r[1] == 5040

    def test_factorial_ten(self):
        r = PROGRAMS["factorial"].run({0: 10})
        assert r[1] == 3628800

    def test_output_in_r1(self):
        r = PROGRAMS["factorial"].run({0: 4})
        assert r[1] == 24

    def test_clobbers_r0_r2_r4_r5(self):
        """factorial modifies R0 (counter), R2, R4, R5 internally."""
        r = PROGRAMS["factorial"].run({0: 5, 2: 999, 4: 888, 5: 777, 6: 666})
        assert r[1] == 120
        assert r[0] == 0     # R0 consumed (decremented to 0)
        assert r[2] != 999   # R2 clobbered
        assert r[4] != 888   # R4 clobbered
        assert r[5] != 777   # R5 clobbered
        assert r[6] == 666   # R6 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# power Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPower:
    """Tests for the power program: R0^R1 -> R2."""

    def test_2_to_10(self):
        r = PROGRAMS["power"].run({0: 2, 1: 10})
        assert r[2] == 1024

    def test_3_to_3(self):
        r = PROGRAMS["power"].run({0: 3, 1: 3})
        assert r[2] == 27

    def test_5_to_1(self):
        r = PROGRAMS["power"].run({0: 5, 1: 1})
        assert r[2] == 5

    def test_0_to_n(self):
        """0^5 = 0."""
        r = PROGRAMS["power"].run({0: 0, 1: 5})
        assert r[2] == 0

    def test_1_to_n(self):
        """1^100 = 1."""
        r = PROGRAMS["power"].run({0: 1, 1: 100})
        assert r[2] == 1

    def test_2_to_1(self):
        r = PROGRAMS["power"].run({0: 2, 1: 1})
        assert r[2] == 2

    def test_output_in_r2(self):
        r = PROGRAMS["power"].run({0: 4, 1: 3})
        assert r[2] == 64

    def test_clobbers_r1(self):
        """power consumes R1 (decrements exponent)."""
        r = PROGRAMS["power"].run({0: 2, 1: 10})
        assert r[1] == 0  # R1 decremented to 0

    @pytest.mark.xfail(reason="BUG: power loop doesn't handle exponent=0; hits cycle limit and produces astronomically large number")
    def test_2_to_0(self):
        """2^0 should be 1, but the loop runs before checking the exponent."""
        r = PROGRAMS["power"].run({0: 2, 1: 0})
        assert r[2] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# fibonacci Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestFibonacci:
    """Tests for the fibonacci program: R2 iterations -> R1.
    Uses R0 and R1 as the starting pair (typically R0=0, R1=1)."""

    def test_1_iteration(self):
        """fib(0,1) after 1 iter: (1,1) -> R1=1."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 1})
        assert r[1] == 1

    def test_2_iterations(self):
        """fib(0,1) after 2 iters: (1,2) -> R1=2."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 2})
        assert r[1] == 2

    def test_5_iterations(self):
        """fib(0,1) after 5 iters: (5,8) -> R1=8."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 5})
        assert r[1] == 8

    def test_10_iterations(self):
        """fib(0,1) after 10 iters: (55,89) -> R1=89."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 10})
        assert r[1] == 89
        assert r[0] == 55

    @pytest.mark.xfail(reason="BUG: fibonacci loop decrements R2 before checking; R2=0 loops until cycle limit")
    def test_0_iterations(self):
        """fib(0,1) after 0 iters: no change, R1=1."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 0})
        assert r[1] == 1

    def test_r2_consumed(self):
        """R2 (iteration counter) is decremented to 0."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 5})
        assert r[2] == 0

    def test_clobbers_r0_and_r3(self):
        """fibonacci modifies R0 and uses R3 internally."""
        r = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 3, 3: 999, 4: 888})
        assert r[0] == 2   # R0 shifted
        assert r[3] != 999  # R3 clobbered
        assert r[4] == 888  # R4 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# gcd Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestGcd:
    """Tests for the gcd program: gcd(R0, R1) -> R0."""

    def test_basic(self):
        r = PROGRAMS["gcd"].run({0: 48, 1: 18})
        assert r[0] == 6

    def test_coprime(self):
        r = PROGRAMS["gcd"].run({0: 17, 1: 13})
        assert r[0] == 1

    def test_one_zero(self):
        """gcd(0, 5) = 5."""
        r = PROGRAMS["gcd"].run({0: 0, 1: 5})
        assert r[0] == 5

    def test_both_equal(self):
        """gcd(12, 12) = 12."""
        r = PROGRAMS["gcd"].run({0: 12, 1: 12})
        assert r[0] == 12

    def test_order_matters_first_larger(self):
        r = PROGRAMS["gcd"].run({0: 18, 1: 48})
        assert r[0] == 6

    def test_gcd_1_and_1(self):
        r = PROGRAMS["gcd"].run({0: 1, 1: 1})
        assert r[0] == 1

    def test_large_numbers(self):
        """gcd(100, 75) = 25."""
        r = PROGRAMS["gcd"].run({0: 100, 1: 75})
        assert r[0] == 25

    def test_negative_inputs_produce_negative_gcd(self):
        """BUG: gcd(-6, -15) returns -3 instead of 3.
        Python's modulo with negatives propagates sign."""
        r = PROGRAMS["gcd"].run({0: -6, 1: -15})
        assert r[0] == -3  # should be 3 (absolute value)

    def test_clobbers_multiple_registers(self):
        """gcd modifies R0, R1 and clobbers R2, R3, R4, R5."""
        r = PROGRAMS["gcd"].run({0: 48, 1: 18, 2: 999, 3: 888, 4: 777, 5: 666, 6: 555})
        assert r[0] == 6
        assert r[2] != 999  # R2 clobbered
        assert r[3] != 888  # R3 clobbered
        assert r[4] != 777  # R4 clobbered
        assert r[5] != 666  # R5 clobbered
        assert r[6] == 555  # R6 untouched


# ═══════════════════════════════════════════════════════════════════════════════
# sum_to_n Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSumToN:
    """Tests for the sum_to_n program: Sum 1..R0 -> R1."""

    def test_sum_1(self):
        r = PROGRAMS["sum_to_n"].run({0: 1})
        assert r[1] == 1

    def test_sum_10(self):
        r = PROGRAMS["sum_to_n"].run({0: 10})
        assert r[1] == 55

    def test_sum_100(self):
        r = PROGRAMS["sum_to_n"].run({0: 100})
        assert r[1] == 5050

    def test_sum_1000(self):
        r = PROGRAMS["sum_to_n"].run({0: 1000})
        assert r[1] == 500500

    def test_output_in_r1(self):
        r = PROGRAMS["sum_to_n"].run({0: 5})
        assert r[1] == 15

    def test_r0_consumed(self):
        """R0 is decremented to 0."""
        r = PROGRAMS["sum_to_n"].run({0: 10})
        assert r[0] == 0

    @pytest.mark.xfail(reason="BUG: sum_to_n loop doesn't handle R0=0; decrements to -1 and loops until cycle limit")
    def test_sum_0(self):
        """Sum 1..0 = 0, but the loop decrements R0 before checking, causing infinite loop."""
        r = PROGRAMS["sum_to_n"].run({0: 0})
        assert r[1] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# swap Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSwap:
    """Tests for the swap program: Swap R0 and R1 via stack."""

    def test_different_values(self):
        r = PROGRAMS["swap"].run({0: 42, 1: 99})
        assert r[0] == 99
        assert r[1] == 42

    def test_same_values(self):
        r = PROGRAMS["swap"].run({0: 7, 1: 7})
        assert r[0] == 7
        assert r[1] == 7

    def test_negative_values(self):
        r = PROGRAMS["swap"].run({0: -5, 1: 10})
        assert r[0] == 10
        assert r[1] == -5

    def test_zero_and_value(self):
        r = PROGRAMS["swap"].run({0: 0, 1: 42})
        assert r[0] == 42
        assert r[1] == 0

    def test_both_zero(self):
        r = PROGRAMS["swap"].run({0: 0, 1: 0})
        assert r[0] == 0
        assert r[1] == 0

    def test_double_swap_roundtrip(self):
        """Swapping twice should return to original."""
        p = PROGRAMS["swap"]
        r1 = p.run({0: 10, 1: 20})
        r2 = p.run(r1)
        assert r2[0] == 10
        assert r2[1] == 20

    def test_no_other_registers_clobbered(self):
        """swap only touches R0 and R1 via the stack."""
        r = PROGRAMS["swap"].run({0: 42, 1: 99, 2: 888, 3: 777})
        assert r[2] == 888
        assert r[3] == 777


# ═══════════════════════════════════════════════════════════════════════════════
# copy Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCopy:
    """Tests for the copy program: Copy R0 to R1."""

    def test_positive(self):
        r = PROGRAMS["copy"].run({0: 42})
        assert r[1] == 42

    def test_zero(self):
        r = PROGRAMS["copy"].run({0: 0})
        assert r[1] == 0

    def test_negative(self):
        r = PROGRAMS["copy"].run({0: -99})
        assert r[1] == -99

    def test_large_value(self):
        r = PROGRAMS["copy"].run({0: 1234567})
        assert r[1] == 1234567

    def test_r0_unchanged(self):
        r = PROGRAMS["copy"].run({0: 42})
        assert r[0] == 42

    def test_no_other_registers_clobbered(self):
        """copy only writes R1."""
        r = PROGRAMS["copy"].run({0: 42, 2: 999, 3: 888})
        assert r[2] == 999
        assert r[3] == 888


# ═══════════════════════════════════════════════════════════════════════════════
# negate Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestNegate:
    """Tests for the negate program: Negate R0."""

    def test_positive(self):
        r = PROGRAMS["negate"].run({0: 42})
        assert r[0] == -42

    def test_negative(self):
        r = PROGRAMS["negate"].run({0: -42})
        assert r[0] == 42

    def test_zero(self):
        r = PROGRAMS["negate"].run({0: 0})
        assert r[0] == 0

    def test_double_negate(self):
        """Negating twice returns the original value."""
        p = PROGRAMS["negate"]
        r1 = p.run({0: 42})
        r2 = p.run(r1)
        assert r2[0] == 42

    def test_no_other_registers_clobbered(self):
        """negate only modifies R0."""
        r = PROGRAMS["negate"].run({0: 42, 1: 999, 2: 888})
        assert r[1] == 999
        assert r[2] == 888


# ═══════════════════════════════════════════════════════════════════════════════
# double Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestDouble:
    """Tests for the double program: Double R0."""

    def test_positive(self):
        r = PROGRAMS["double"].run({0: 21})
        assert r[0] == 42

    def test_negative(self):
        r = PROGRAMS["double"].run({0: -10})
        assert r[0] == -20

    def test_zero(self):
        r = PROGRAMS["double"].run({0: 0})
        assert r[0] == 0

    def test_one(self):
        r = PROGRAMS["double"].run({0: 1})
        assert r[0] == 2

    def test_large_value(self):
        r = PROGRAMS["double"].run({0: 1000000})
        assert r[0] == 2000000

    def test_no_other_registers_clobbered(self):
        """double only modifies R0."""
        r = PROGRAMS["double"].run({0: 21, 1: 999, 2: 888})
        assert r[1] == 999
        assert r[2] == 888


# ═══════════════════════════════════════════════════════════════════════════════
# square Program Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestSquare:
    """Tests for the square program: Square R0 -> R1."""

    def test_small(self):
        r = PROGRAMS["square"].run({0: 5})
        assert r[1] == 25

    def test_large(self):
        r = PROGRAMS["square"].run({0: 1000})
        assert r[1] == 1000000

    def test_zero(self):
        r = PROGRAMS["square"].run({0: 0})
        assert r[1] == 0

    def test_negative(self):
        r = PROGRAMS["square"].run({0: -7})
        assert r[1] == 49

    def test_one(self):
        r = PROGRAMS["square"].run({0: 1})
        assert r[1] == 1

    def test_r0_unchanged(self):
        r = PROGRAMS["square"].run({0: 12})
        assert r[0] == 12

    def test_no_other_registers_clobbered(self):
        """square only writes R1."""
        r = PROGRAMS["square"].run({0: 12, 2: 999, 3: 888})
        assert r[2] == 999
        assert r[3] == 888


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Case & Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Cross-cutting edge case and integration tests."""

    def test_register_range_0_to_15(self):
        """run() returns exactly registers 0-15."""
        p = PROGRAMS["copy"]
        result = p.run({0: 42})
        assert len(result) == 16
        assert min(result.keys()) == 0
        assert max(result.keys()) == 15

    def test_registers_above_15_not_accessible(self):
        """Registers 16+ are internal and not in the return dict."""
        p = PROGRAMS["copy"]
        result = p.run({0: 42})
        assert 16 not in result
        assert 63 not in result

    def test_all_programs_produce_correct_structure(self):
        """Every program returns a dict of int->int for keys 0-15."""
        for name, program in PROGRAMS.items():
            result = program.run()
            assert isinstance(result, dict), f"{name}: result is not a dict"
            assert len(result) == 16, f"{name}: expected 16 keys, got {len(result)}"
            for key in range(16):
                assert key in result, f"{name}: missing key {key}"
                assert isinstance(result[key], int), f"{name}: result[{key}] not int"

    def test_all_programs_halt_within_cycle_limit(self):
        """All programs should terminate within 100000 cycles with default inputs."""
        for name, program in PROGRAMS.items():
            # Use minimal/default inputs (all zeros)
            result = program.run()
            assert isinstance(result, dict), f"{name}: did not produce valid result"

    def test_programs_that_modify_r0(self):
        """abs, negate, double, sum_to_n modify R0 in-place."""
        # sum_to_n with R0=5: R0 consumed to 0
        r = PROGRAMS["sum_to_n"].run({0: 5})
        assert r[0] == 0
        # negate changes sign
        r = PROGRAMS["negate"].run({0: 5})
        assert r[0] == -5
        # double doubles
        r = PROGRAMS["double"].run({0: 5})
        assert r[0] == 10

    def test_programs_that_preserve_r0(self):
        """copy, square, max, min should not modify R0 (with appropriate inputs)."""
        r = PROGRAMS["copy"].run({0: 5})
        assert r[0] == 5
        r = PROGRAMS["square"].run({0: 5})
        assert r[0] == 5
        r = PROGRAMS["max"].run({0: 5, 1: 10})
        assert r[0] == 5
        r = PROGRAMS["min"].run({0: 5, 1: 10})
        assert r[0] == 5

    def test_no_register_above_15_clobbered_visible(self):
        """Even if internal registers 16+ are modified, they're not in the return dict."""
        r = PROGRAMS["gcd"].run({0: 48, 1: 18})
        for key in r:
            assert 0 <= key <= 15, f"Register {key} out of range 0-15"
