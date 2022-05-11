from hysut.utils.enums import ALL_PERIOD, RUN_PERIOD, WARM_PERIOD, COOL_PERIOD, T_SLICE, SLICE_NAME
from hysut.exceptions_logging.exceptions import EssentialSetMissing
from hysut.utils.defaults import Time
from hysut.utils.tools import read_range_function, type_consistency_check


def read_time_data(time_data, item):
    """Reading the time_data for specific item and checking the possible errors

    Parameters
    ----------
    time_data : list
        list of collective time definition for a given item
    item : str
        specific time item (run, warm_up, ...) to well specify the error

    Returns
    -------
    dict
        collection of the errors and final time definitions.
        e.g.
        {
            "time": [2020,2022,2023],
            "error": ["time definition through lists can only contain integers for 'run'."]
        }
    """

    time_collection = []
    errors = []

    if not isinstance(time_data, list):
        return {"error": f"time should be defined as a list for '{item}'."}

    for time in time_data:

        if isinstance(time, int):
            time_collection.append(time)

        elif isinstance(time, list):
            if not all([isinstance(i, int) for i in time]):
                errors.append(
                    f"time definition through lists can only contain integers for '{item}'."
                )
            else:
                time_collection.extend(time)

        elif isinstance(time, str) and "range" in time:
            rng_data = read_range_function(time, item)
            time_collection.extend(rng_data["data"])
            errors.extend(rng_data["error"])

        else:
            errors.append(
                f"time definition can be a range (e.g. range(start,end,step)),an integer or a list of integers for '{item}'"
            )

    return {"time": time_collection, "error": errors}


def check_time_period_overlaps(periods):
    """Checks if any overlap in the periods exist

    Parameters
    ----------
    periods : dict
        dict containing the time_data for different periods (values are sorted time horizons)

    Returns
    -------
    list
        a list of errors
    """

    errors = []
    periods = {
        period: list(range(sorted_list[0], sorted_list[-1] + 1))
        for period, sorted_list in periods.items()
    }
    # Checking if duplicate values exist in different periods with run
    for period in [WARM_PERIOD, COOL_PERIOD]:
        if period in periods:
            intersects = set(periods[RUN_PERIOD]).intersection(periods[period])
            if intersects:
                errors.append(
                    f"time_horizon for 'run' and '{period}' have following intersections."
                    f" \n{intersects}"
                )

    # checking if warm and cool period have intersects
    if all([period in periods for period in [WARM_PERIOD, COOL_PERIOD]]):
        intersects = set(periods[WARM_PERIOD]).intersection(periods[COOL_PERIOD])

        if intersects:
            errors.append(
                f"time_horizon for '{WARM_PERIOD}' and '{COOL_PERIOD}' have following intersections."
                f" \n{intersects}"
            )

    return errors


def check_time_horizon(time_horizon):
    """Checks/reform the time horzon definition and collects all errors/warnings through multiple functions

    Parameters
    ----------
    time_horizon : dict
        main dict of time_horizon (from yaml file)

    Returns
    -------
    dict
        {
            "errors" : list of errors
            "warnings" : list of warnings
            "time_horizon" : dict of refined time_horizon which is valid only if no error exist.
        }
    """
    warnings = []
    errors = []
    time_data = {}

    if RUN_PERIOD not in time_horizon:
        raise EssentialSetMissing(f"A model cannot be created without a {RUN_PERIOD}.")

    for period in [RUN_PERIOD, WARM_PERIOD, COOL_PERIOD]:
        if period in time_horizon:

            given_period = time_horizon[period]
            data = read_time_data(given_period, period)

            if len(data.get("error")):
                errors.extend(data.get("error"))

            else:
                # avoid deuplicate values and sort the years
                time_data[period] = sorted(set(data.get("time")))

    extra_give_periods = set(time_horizon).difference(
        set([RUN_PERIOD, WARM_PERIOD, COOL_PERIOD])
    )

    if extra_give_periods:
        warnings.append(
            f"{extra_give_periods} is not a valid argument for for time_horizon definition and"
            " is ignored."
        )

    # catching the errors related to definition of time
    errors.extend(check_time_period_overlaps(time_data))

    # set all_years
    time_data[ALL_PERIOD] = sorted([year for period in time_data.values() for year in period])
    return {"errors": errors, "warnings": warnings, "time_horizon": time_data}


def read_time_slice_data(slices):
    """Read/reform the data for time slices with different formats

    Parameters
    ----------
    slices : list,int,str

    Returns
    -------
    dict
        {
            'time_slices' : List of time_slices
            'errors: errors found in reading the data
        }
    """

    time_slices = []
    errors = []
    if isinstance(slices, str):
        if "range" in slices:
            rng_data = read_range_function(slices, "time_slices")
            time_slices.extend(rng_data["data"])
            errors.extend(rng_data["error"])
        else:
            time_slices.append(slices)

    elif isinstance(slices, int):
        time_slices.append(slices)

    # if a list is passed
    elif isinstance(slices, list):
        # if all data in the list have the same data type
        if type_consistency_check(slices) == []:
            time_slices.extend(slices)

        # otherwise make a recursive process to flatten the list
        else:
            for i in slices:
                data = read_time_slice_data(i)
                time_slices.extend(data["time_slices"])
                errors.extend(data["errors"])

    else:
        errors.append(
            "'time_slices accept only int, str (or range function) or a list of mentioned items."
        )

    return {"time_slices": time_slices, "errors": errors}


def check_time_slices(time_slices):
    """Checks/reforms time_slices definition and collect all the errors and warnings

    Parameters
    ----------
    time_slices : dict
        {
            "name" : 'name of the time slice e.g. Hour',
            "slices" : definition of slices can be given in different modes like: ['Day','Night'] or 'range(1,8761)'
        }

    Returns
    -------
    dict
        {
            "errors" : List of errors,
            "warnings": List of warnings,
            "time_slices" : reformed dict of time_slices
        }
    """

    warnings = []
    errors = []

    # check if the defualt values do not exist, take care of them!
    name = time_slices.setdefault(SLICE_NAME, Time.SLICE_NAME)
    slices = time_slices.setdefault(T_SLICE, Time.T_SLICE)

    slices_data = read_time_slice_data(slices)
    time_slices[T_SLICE] = slices_data["time_slices"]
    errors.extend(slices_data["errors"])

    extra_given_items = set(time_slices).difference(set([SLICE_NAME, T_SLICE]))

    if extra_given_items:
        warnings.append(
            f"{extra_given_items} is not a valid argument for for time_slices definition and"
            " is ignored."
        )

    # check the type_consistency
    errors.extend(type_consistency_check(slices, "time_slices"))

    # check if duplicate values exist
    if len(set(slices)) != len(slices):
        errors.append("duplicate values are not allowed in 'time_slices'.")

    return {"errors": errors, "warnings": warnings, "time_slices": time_slices}
