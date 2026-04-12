"""Tests for all UTILITY category programs."""

import pytest
from stdlib import PROGRAMS, ProgramCategory


class TestSwap:
    """Tests for the swap program: swap R0 and R1 via stack."""

    def test_swap_basic(self):
        result = PROGRAMS["swap"].run({0: 42, 1: 99})
        assert result[0] == 99
        assert result[1] == 42

    def test_swap_same_value(self):
        result = PROGRAMS["swap"].run({0: 5, 1: 5})
        assert result[0] == 5
        assert result[1] == 5

    def test_swap_zero_and_value(self):
        result = PROGRAMS["swap"].run({0: 0, 1: 77})
        assert result[0] == 77
        assert result[1] == 0

    def test_swap_negative_values(self):
        result = PROGRAMS["swap"].run({0: -10, 1: 20})
        assert result[0] == 20
        assert result[1] == -10

    def test_category(self):
        assert PROGRAMS["swap"].category == ProgramCategory.UTILITY

    def test_inputs_outputs(self):
        assert PROGRAMS["swap"].inputs == ["R0", "R1"]
        assert PROGRAMS["swap"].outputs == ["R0", "R1"]


class TestCopy:
    """Tests for the copy program: Copy R0 to R1."""

    def test_copy_basic(self):
        result = PROGRAMS["copy"].run({0: 42})
        assert result[1] == 42

    def test_copy_zero(self):
        result = PROGRAMS["copy"].run({0: 0})
        assert result[1] == 0

    def test_copy_negative(self):
        result = PROGRAMS["copy"].run({0: -99})
        assert result[1] == -99

    def test_copy_large(self):
        result = PROGRAMS["copy"].run({0: 999999})
        assert result[1] == 999999

    def test_source_unchanged(self):
        result = PROGRAMS["copy"].run({0: 42})
        assert result[0] == 42

    def test_category(self):
        assert PROGRAMS["copy"].category == ProgramCategory.UTILITY


class TestNegate:
    """Tests for the negate program: Negate R0."""

    def test_negate_positive(self):
        result = PROGRAMS["negate"].run({0: 42})
        assert result[0] == -42

    def test_negate_negative(self):
        result = PROGRAMS["negate"].run({0: -42})
        assert result[0] == 42

    def test_negate_zero(self):
        result = PROGRAMS["negate"].run({0: 0})
        assert result[0] == 0

    def test_double_negate(self):
        """Negating twice should be identity, test via two runs."""
        r1 = PROGRAMS["negate"].run({0: 42})
        r2 = PROGRAMS["negate"].run({0: r1[0]})
        assert r2[0] == 42

    def test_category(self):
        assert PROGRAMS["negate"].category == ProgramCategory.UTILITY


class TestDouble:
    """Tests for the double program: Double R0."""

    def test_double_positive(self):
        result = PROGRAMS["double"].run({0: 21})
        assert result[0] == 42

    def test_double_zero(self):
        result = PROGRAMS["double"].run({0: 0})
        assert result[0] == 0

    def test_double_negative(self):
        result = PROGRAMS["double"].run({0: -5})
        assert result[0] == -10

    def test_double_one(self):
        result = PROGRAMS["double"].run({0: 1})
        assert result[0] == 2

    def test_category(self):
        assert PROGRAMS["double"].category == ProgramCategory.UTILITY


class TestSquare:
    """Tests for the square program: Square R0 -> R1."""

    def test_square_basic(self):
        result = PROGRAMS["square"].run({0: 12})
        assert result[1] == 144

    def test_square_zero(self):
        result = PROGRAMS["square"].run({0: 0})
        assert result[1] == 0

    def test_square_one(self):
        result = PROGRAMS["square"].run({0: 1})
        assert result[1] == 1

    def test_square_negative(self):
        result = PROGRAMS["square"].run({0: -7})
        assert result[1] == 49

    def test_square_source_unchanged(self):
        result = PROGRAMS["square"].run({0: 7})
        assert result[0] == 7

    def test_category(self):
        assert PROGRAMS["square"].category == ProgramCategory.UTILITY
