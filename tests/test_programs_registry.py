"""Tests for the PROGRAMS registry and structural integrity."""

import pytest
from stdlib import PROGRAMS, ProgramCategory


class TestProgramsRegistry:
    """Tests for the PROGRAMS dictionary."""

    def test_programs_is_dict(self):
        assert isinstance(PROGRAMS, dict)

    def test_total_program_count(self):
        assert len(PROGRAMS) == 13

    def test_all_math_programs_present(self):
        expected = {"abs", "max", "min", "factorial", "power", "fibonacci", "gcd", "sum_to_n"}
        actual = {name for name, p in PROGRAMS.items() if p.category == ProgramCategory.MATH}
        assert actual == expected

    def test_all_utility_programs_present(self):
        expected = {"swap", "copy", "negate", "double", "square"}
        actual = {name for name, p in PROGRAMS.items() if p.category == ProgramCategory.UTILITY}
        assert actual == expected

    def test_all_names_are_strings(self):
        for name in PROGRAMS:
            assert isinstance(name, str)

    def test_all_names_nonempty(self):
        for name in PROGRAMS:
            assert len(name) > 0

    def test_all_have_valid_category(self):
        for p in PROGRAMS.values():
            assert isinstance(p.category, ProgramCategory)

    def test_all_have_nonempty_description(self):
        for p in PROGRAMS.values():
            assert isinstance(p.description, str)
            assert len(p.description) > 0

    def test_all_have_bytecode(self):
        for p in PROGRAMS.values():
            assert isinstance(p.bytecode, list)
            assert len(p.bytecode) > 0

    def test_all_bytecodes_are_ints(self):
        for p in PROGRAMS.values():
            for b in p.bytecode:
                assert isinstance(b, int)
                assert 0 <= b <= 255

    def test_all_have_inputs_list(self):
        for p in PROGRAMS.values():
            assert isinstance(p.inputs, list)

    def test_all_have_outputs_list(self):
        for p in PROGRAMS.values():
            assert isinstance(p.outputs, list)

    def test_all_bytecodes_end_with_halt(self):
        for p in PROGRAMS.values():
            assert p.bytecode[-1] == 0x00, f"{p.name} bytecode doesn't end with HALT"

    def test_size_bytes_matches_bytecode_length(self):
        for p in PROGRAMS.values():
            assert p.size_bytes == len(p.bytecode)

    def test_all_author_is_stdlib(self):
        for p in PROGRAMS.values():
            assert p.author == "stdlib"

    def test_no_duplicate_names(self):
        names = list(PROGRAMS.keys())
        assert len(names) == len(set(names))

    def test_program_name_matches_key(self):
        for name, p in PROGRAMS.items():
            assert p.name == name

    def test_all_programs_runnable(self):
        """Every program should be able to execute with empty/default initial regs."""
        for name, p in PROGRAMS.items():
            result = p.run()
            assert isinstance(result, dict)
            assert set(result.keys()) == set(range(16))


class TestCategoryDistribution:
    """Tests for category distribution across programs."""

    def test_only_math_and_utility_have_programs(self):
        used_categories = {p.category for p in PROGRAMS.values()}
        assert used_categories == {ProgramCategory.MATH, ProgramCategory.UTILITY}

    def test_math_has_8_programs(self):
        math_count = sum(1 for p in PROGRAMS.values() if p.category == ProgramCategory.MATH)
        assert math_count == 8

    def test_utility_has_5_programs(self):
        util_count = sum(1 for p in PROGRAMS.values() if p.category == ProgramCategory.UTILITY)
        assert util_count == 5
