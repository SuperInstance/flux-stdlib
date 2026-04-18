"""Tests for the ProgramCategory enum."""

import pytest
from stdlib import ProgramCategory


class TestProgramCategory:
    """Tests for ProgramCategory enum values and behavior."""

    def test_all_categories_exist(self):
        expected = {"MATH", "SORT", "SEARCH", "CRYPTO", "STRING", "FLEET", "SENSOR", "UTILITY"}
        actual = {cat.name for cat in ProgramCategory}
        assert actual == expected

    def test_category_values_are_lowercase(self):
        for cat in ProgramCategory:
            assert cat.value == cat.name.lower()

    def test_math_category(self):
        assert ProgramCategory.MATH.value == "math"

    def test_utility_category(self):
        assert ProgramCategory.UTILITY.value == "utility"

    def test_sort_category(self):
        assert ProgramCategory.SORT.value == "sort"

    def test_search_category(self):
        assert ProgramCategory.SEARCH.value == "search"

    def test_crypto_category(self):
        assert ProgramCategory.CRYPTO.value == "crypto"

    def test_string_category(self):
        assert ProgramCategory.STRING.value == "string"

    def test_fleet_category(self):
        assert ProgramCategory.FLEET.value == "fleet"

    def test_sensor_category(self):
        assert ProgramCategory.SENSOR.value == "sensor"

    def test_total_count(self):
        assert len(ProgramCategory) == 8

    def test_uniqueness_of_values(self):
        values = [cat.value for cat in ProgramCategory]
        assert len(values) == len(set(values))

    def test_iteration(self):
        categories = list(ProgramCategory)
        assert len(categories) == 8

    def test_comparison_by_identity(self):
        assert ProgramCategory.MATH is ProgramCategory.MATH
        assert ProgramCategory.MATH is not ProgramCategory.UTILITY
