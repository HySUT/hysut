
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pytest
from hysut.utils.tools import read_range_function, type_consistency_check

def test_type_consistency_check():

    assert type_consistency_check([1,2,3,4],'dummy') == []
    assert type_consistency_check(['h',2,3,4],'dummy') == [f"'dummy' is not allowed to have different data type."]

def test_read_range_function():
    assert read_range_function('range(2020,2023)','dummy')['data'] == [2020,2021,2022]
    assert read_range_function('range(2020,2025,2)','dummy')['data'] == [2020,2022,2024]
    # error in range
    assert read_range_function('range(2020,2025,2.1)','dummy')['error'] == ["'float' object cannot be interpreted as an integer in 'range' for 'dummy'."]
