
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from hysut.preprocess.time import (
    read_time_data
)

def test_read_time_data():

    # passing non list items like set
    out = read_time_data({2020,2021},"run")

    assert [*out] == ["error"]

    # passing a wrong item in the upper level list
    out = read_time_data(
        time_data = [2020,[2021,2022.1],'dummy'],
        item = 'run'
    )

    assert out['time'] == [2020]
    assert len(out['error']) == 2

    # passing range function
    out = read_time_data(
       time_data = ['range(2020,2023)','range(2023,2028,2)'],
       item = 'run'
    )

    assert out['time'] == [2020,2021,2022,2023,2025,2027]
    assert out['error'] is None

    # wrong range
    out = read_time_data(
       time_data = ['range(2020,2023,1.1)',],
       item = 'run'
    )

    assert out['time'] == []
    assert out['error'] == ["'float' object cannot be interpreted as an integer in 'range' for 'run'."]

    # passing int in lists
    out = read_time_data(
       time_data = [2020,2021,2023],
       item = 'run'
    )

    assert out['time'] == [2020,2021,2023]
    assert out['error'] is None

    # passing list[int] s
    out = read_time_data(
       time_data = [[2020,2021],[2023]],
       item = 'run'
    )

    assert out['time'] == [2020,2021,2023]
    assert out['error'] is None

    # combination of all cases
    out = read_time_data(
       time_data = [2020,2021,[2022,2023],'range(2024,2026)'],
       item = 'run'
    )

    assert out['time'] == list(range(2020,2026))
    assert out['error'] is None

