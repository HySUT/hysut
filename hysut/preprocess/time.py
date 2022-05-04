from hysut.utils.enums import RUN_PERIOD, WARM_PERIOD, COOL_PERIOD


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
            try:
                time_collection.extend(list(eval(time)))
            except Exception as error:
                errors.extend([f"{arg} in 'range' for '{item}'." for arg in error.args])
        else:
            errors.append(
                f"time definition can be a range (e.g. range(start,end,step)),an integer or a list of integers for '{item}'"
            )

    return {"time": time_collection, "error": errors if len(errors) else None}


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
    warnings = []
    errors = []
    time_data = {}

    if RUN_PERIOD not in time_horizon:
        errors.append(f"A model cannot be created without a {RUN_PERIOD}.")

    for period in [RUN_PERIOD, WARM_PERIOD, COOL_PERIOD]:
        if period in time_horizon:

            given_period = time_horizon[period]
            data = read_time_data(given_period, period)

            if data.get("error") is not None:
                errors.append(data.get("error"))

            else:
                # avoid deuplicate values and sort the years
                time_data[period] = sorted(set(data.get("time")))

        else:
            warnings.append(
                f"{period} is not a valid argument for for time_horizon definition and"
                " is ignored."
            )

    # catching the errors related to definition of time
    errors.append(check_time_period_overlaps(time_data))


# %%
