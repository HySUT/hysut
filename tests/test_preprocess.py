import sys
import os

import pytest


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from hysut.preprocess.time import (
    check_time_slices,
    read_time_data,
    check_time_period_overlaps,
    check_time_horizon,
    read_time_slice_data
)

from hysut.utils.enums import RUN_PERIOD, COOL_PERIOD, WARM_PERIOD,T_SLICE,SLICE_NAME
from hysut.utils.defaults import Time
from hysut.exceptions_logging.exceptions import EssentialSetMissing


def test_read_time_data():

    # passing non list items like set
    out = read_time_data({2020, 2021}, "run")

    assert [*out] == ["error"]

    # passing a wrong item in the upper level list
    out = read_time_data(time_data=[2020, [2021, 2022.1], "dummy"], item="run")

    assert out["time"] == [2020]
    assert len(out["error"]) == 2

    # passing range function
    out = read_time_data(
        time_data=["range(2020,2023)", "range(2023,2028,2)"], item="run"
    )

    assert out["time"] == [2020, 2021, 2022, 2023, 2025, 2027]
    assert out["error"] == []

    # wrong range
    out = read_time_data(time_data=["range(2020,2023,1.1)",], item="run")

    assert out["time"] == []
    assert out["error"] == [
        "'float' object cannot be interpreted as an integer in 'range' for 'run'."
    ]

    # passing int in lists
    out = read_time_data(time_data=[2020, 2021, 2023], item="run")

    assert out["time"] == [2020, 2021, 2023]
    assert out["error"] == []

    # passing list[int] s
    out = read_time_data(time_data=[[2020, 2021], [2023]], item="run")

    assert out["time"] == [2020, 2021, 2023]
    assert out["error"] == []

    # combination of all cases
    out = read_time_data(
        time_data=[2020, 2021, [2022, 2023], "range(2024,2026)"], item="run"
    )

    assert out["time"] == list(range(2020, 2026))
    assert out["error"] == []


def test_check_time_period_overlaps():

    # run and warm overlap
    periods = {RUN_PERIOD: [2020, 2022, 2023, 2025], WARM_PERIOD: [2024, 2028]}

    expected_error = f"time_horizon for 'run' and '{WARM_PERIOD}' have following intersections. \n{set([2024,2025])}"
    error = check_time_period_overlaps(periods)[0]

    assert error == expected_error

    # warm and cool overlap
    periods = {
        RUN_PERIOD: [2020, 2022, 2023, 2025],
        COOL_PERIOD: [2026, 2027],
        WARM_PERIOD: [2027, 2028],
    }

    expected_error = f"time_horizon for '{WARM_PERIOD}' and '{COOL_PERIOD}' have following intersections. \n{set([2027])}"
    error = check_time_period_overlaps(periods)[0]

    assert error == expected_error

    # run,cool, and warm overlap

    periods = {
        RUN_PERIOD: [2020, 2022, 2023, 2025],
        WARM_PERIOD: [2024, 2027],
        COOL_PERIOD: [2027, 2028],
    }

    expected_error = [
        f"time_horizon for 'run' and '{WARM_PERIOD}' have following intersections. \n{set([2024,2025])}",
        f"time_horizon for '{WARM_PERIOD}' and '{COOL_PERIOD}' have following intersections. \n{set([2027])}",
    ]

    error = check_time_period_overlaps(periods)

    assert error == expected_error

    # no error
    periods = {
        RUN_PERIOD: [2020, 2022, 2023, 2025],
        WARM_PERIOD: [2026, 2027],
        COOL_PERIOD: [2028, 2030],
    }

    error = check_time_period_overlaps(periods)
    assert error == []


def test_check_time_horizon():

    # not passing the run time horizon
    with pytest.raises(EssentialSetMissing) as msg:
        check_time_horizon({"dummy": "dummy"})

    assert "A model cannot be created without a" in str(msg.value)

    # check if periods are sorted and duplicates are delted
    time_horizon = {RUN_PERIOD: [2025, 2024, 2023, 2022, 2024, 2021]}
    output = check_time_horizon(time_horizon)

    assert output["time_horizon"][RUN_PERIOD] == [2021, 2022, 2023, 2024, 2025]
    assert output["errors"] == []
    assert output["warnings"] == []

    # making error
    time_horizon = {RUN_PERIOD: [2025.1]}
    error = check_time_horizon(time_horizon)["errors"]
    expexted_error = [
        f"time definition can be a range (e.g. range(start,end,step)),an integer or a list of integers for '{RUN_PERIOD}'"
    ]

    assert error == expexted_error

    # capture warnings
    time_horizon = {RUN_PERIOD: [2025], "dummy": [2026]}

    warning = check_time_horizon(time_horizon)["warnings"]
    expexted_warning = [
        f"{set(['dummy'])} is not a valid argument for for time_horizon definition and is ignored."
    ]

    assert warning == expexted_warning

def test_check_time_slices():

    time_slices = {}
    expected_output = {SLICE_NAME:Time.SLICE_NAME,T_SLICE:Time.T_SLICE}
    output = check_time_slices(time_slices)

    assert output['time_slices'] == expected_output
    assert output['warnings'] == []

    time_slices = {SLICE_NAME:"Hour",T_SLICE:list(range(1,25))}
    expected_output = time_slices
    output = check_time_slices(time_slices)['time_slices']

    assert expected_output == output

    # passing extra item
    time_slices = {"dummy":"dummy"}
    output = check_time_slices(time_slices)['warnings']
    expected_warning = [f"{{'dummy'}} is not a valid argument for for time_slices definition and is ignored."]

    assert output == expected_warning

    # passing duplicate values
    time_slices = {T_SLICE:[1,1,2]}
    output = check_time_slices(time_slices)['errors']
    expected_error = ["duplicate values are not allowed in 'time_slices'."]
    assert output == expected_error



def test_read_time_slice_data():
    slices = ['Night',['Morning',["Evening",24]]]
    expected_output = ['Night','Morning',"Evening",24]
    output = read_time_slice_data(slices)['time_slices']

    assert expected_output == output

    # non acceptable data type
    excepted_error = ["'time_slices accept only int, str (or range function) or a list of mentioned items."]
    error = read_time_slice_data(2.3)['errors']

    assert excepted_error == error

    # checking the range
    expected_output = [2020,2022,2024]
    output = read_time_slice_data('range(2020,2026,2)')['time_slices']

    assert expected_output == output