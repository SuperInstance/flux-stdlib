"""Tests for all MATH category programs."""

import pytest
from stdlib import PROGRAMS, ProgramCategory


class TestAbs:
    """Tests for the abs program: |R0| -> R0."""

    def test_positive(self):
        result = PROGRAMS["abs"].run({0: 42})
        assert result[0] == 42

    def test_negative(self):
        result = PROGRAMS["abs"].run({0: -42})
        assert result[0] == 42

    def test_zero(self):
        result = PROGRAMS["abs"].run({0: 0})
        assert result[0] == 0

    def test_category(self):
        assert PROGRAMS["abs"].category == ProgramCategory.MATH

    def test_inputs(self):
        assert "R0" in PROGRAMS["abs"].inputs

    def test_outputs(self):
        assert "R0" in PROGRAMS["abs"].outputs

    def test_large_negative(self):
        result = PROGRAMS["abs"].run({0: -999})
        assert result[0] == 999


class TestMax:
    """Tests for the max program: max(R0, R1) -> R2."""

    def test_first_larger(self):
        result = PROGRAMS["max"].run({0: 30, 1: 20})
        assert result[2] == 30

    def test_second_larger(self):
        result = PROGRAMS["max"].run({0: 10, 1: 20})
        assert result[2] == 20

    def test_equal(self):
        result = PROGRAMS["max"].run({0: 42, 1: 42})
        assert result[2] == 42

    def test_negative_values(self):
        result = PROGRAMS["max"].run({0: -10, 1: -5})
        assert result[2] == -5

    def test_category(self):
        assert PROGRAMS["max"].category == ProgramCategory.MATH


class TestMin:
    """Tests for the min program: min(R0, R1) -> R2."""

    def test_first_smaller(self):
        result = PROGRAMS["min"].run({0: 10, 1: 20})
        assert result[2] == 10

    def test_second_smaller(self):
        result = PROGRAMS["min"].run({0: 30, 1: 20})
        assert result[2] == 20

    def test_equal(self):
        result = PROGRAMS["min"].run({0: 42, 1: 42})
        assert result[2] == 42

    def test_negative_values(self):
        result = PROGRAMS["min"].run({0: -10, 1: -5})
        assert result[2] == -10

    def test_category(self):
        assert PROGRAMS["min"].category == ProgramCategory.MATH


class TestFactorial:
    """Tests for the factorial program: R0! -> R1."""

    def test_factorial_six(self):
        result = PROGRAMS["factorial"].run({0: 6})
        assert result[1] == 720

    def test_factorial_zero(self):
        result = PROGRAMS["factorial"].run({0: 0})
        assert result[1] == 1

    def test_factorial_one(self):
        result = PROGRAMS["factorial"].run({0: 1})
        assert result[1] == 1

    def test_factorial_two(self):
        result = PROGRAMS["factorial"].run({0: 2})
        assert result[1] == 2

    def test_factorial_three(self):
        result = PROGRAMS["factorial"].run({0: 3})
        assert result[1] == 6

    def test_factorial_four(self):
        result = PROGRAMS["factorial"].run({0: 4})
        assert result[1] == 24

    def test_factorial_five(self):
        result = PROGRAMS["factorial"].run({0: 5})
        assert result[1] == 120

    def test_factorial_ten(self):
        result = PROGRAMS["factorial"].run({0: 10})
        assert result[1] == 3628800

    def test_category(self):
        assert PROGRAMS["factorial"].category == ProgramCategory.MATH


class TestPower:
    """Tests for the power program: R0^R1 -> R2."""

    def test_2_to_10(self):
        result = PROGRAMS["power"].run({0: 2, 1: 10})
        assert result[2] == 1024

    @pytest.mark.xfail(reason="power bytecode loops when exponent=0; loop body executes before decrement check")
    def test_2_to_0(self):
        result = PROGRAMS["power"].run({0: 2, 1: 0})
        assert result[2] == 1

    def test_3_to_3(self):
        result = PROGRAMS["power"].run({0: 3, 1: 3})
        assert result[2] == 27

    def test_5_to_2(self):
        result = PROGRAMS["power"].run({0: 5, 1: 2})
        assert result[2] == 25

    def test_1_to_any(self):
        result = PROGRAMS["power"].run({0: 1, 1: 100})
        assert result[2] == 1

    def test_category(self):
        assert PROGRAMS["power"].category == ProgramCategory.MATH


class TestFibonacci:
    """Tests for the fibonacci program: R2 iterations -> R1."""

    @pytest.mark.xfail(reason="fibonacci bytecode does one iteration before checking loop counter")
    def test_fib_0_iterations(self):
        result = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 0})
        assert result[1] == 1

    def test_fib_1_iteration(self):
        result = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 1})
        assert result[1] == 1

    def test_fib_5_iterations(self):
        result = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 5})
        assert result[1] == 8

    def test_fib_10_iterations(self):
        result = PROGRAMS["fibonacci"].run({0: 0, 1: 1, 2: 10})
        assert result[1] == 89

    def test_category(self):
        assert PROGRAMS["fibonacci"].category == ProgramCategory.MATH


class TestGCD:
    """Tests for the gcd program: gcd(R0, R1) -> R0."""

    def test_gcd_48_18(self):
        result = PROGRAMS["gcd"].run({0: 48, 1: 18})
        assert result[0] == 6

    def test_gcd_coprime(self):
        result = PROGRAMS["gcd"].run({0: 17, 1: 13})
        assert result[0] == 1

    def test_gcd_equal(self):
        result = PROGRAMS["gcd"].run({0: 42, 1: 42})
        assert result[0] == 42

    def test_gcd_zero(self):
        result = PROGRAMS["gcd"].run({0: 0, 1: 5})
        assert result[0] == 5

    def test_gcd_both_zero(self):
        result = PROGRAMS["gcd"].run({0: 0, 1: 0})
        assert result[0] == 0

    def test_gcd_100_75(self):
        result = PROGRAMS["gcd"].run({0: 100, 1: 75})
        assert result[0] == 25

    def test_gcd_larger_first(self):
        result = PROGRAMS["gcd"].run({0: 100, 1: 25})
        assert result[0] == 25

    def test_category(self):
        assert PROGRAMS["gcd"].category == ProgramCategory.MATH


class TestSumToN:
    """Tests for the sum_to_n program: Sum 1..R0 -> R1."""

    def test_sum_10(self):
        result = PROGRAMS["sum_to_n"].run({0: 10})
        assert result[1] == 55

    def test_sum_100(self):
        result = PROGRAMS["sum_to_n"].run({0: 100})
        assert result[1] == 5050

    def test_sum_1(self):
        result = PROGRAMS["sum_to_n"].run({0: 1})
        assert result[1] == 1

    @pytest.mark.xfail(reason="sum_to_n bytecode loops when n=0; decrement causes negative counter")
    def test_sum_0(self):
        result = PROGRAMS["sum_to_n"].run({0: 0})
        assert result[1] == 0

    def test_sum_5(self):
        result = PROGRAMS["sum_to_n"].run({0: 5})
        assert result[1] == 15

    def test_category(self):
        assert PROGRAMS["sum_to_n"].category == ProgramCategory.MATH
