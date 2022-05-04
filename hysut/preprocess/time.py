
from hysut.utils.enums import (
    RUN_PERIOD,
    WARM_PERIOD,
    COOL_PERIOD
)

def read_time_data(time_data,item):
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

    if not isinstance(time_data,list):
        return {"error" : f"time should be defined as a list for '{item}'."}

    for time in time_data:

        if isinstance(time,int):
            time_collection.append(time)

        elif isinstance(time,list):
            if not all([isinstance(i,int) for  i in time]):
                errors.append(f"time definition through lists can only contain integers for '{item}'.")
            else:
                time_collection.extend(time)

        elif isinstance(time,str) and 'range' in time:
            try:
                time_collection.extend(list(eval(time)))
            except Exception as error:
                errors.extend([f"{arg} in 'range' for '{item}'." for arg in error.args])
        else:
            errors.append(f"time definition can be a range (e.g. range(start,end,step)),an integer or a list of integers for '{item}'")

    return {
        "time":time_collection,
        "error": errors if len(errors) else None
        }


# def check_time_horizon(time_horizon):
#     warnings = []
#     errors   = []
#     time_data = {}

#     if RUN_PERIOD not in time_horizon:
#         errors.append(
#             f"A model cannot be created without a {RUN_PERIOD}."
#         )

#     for period in [RUN_PERIOD,WARM_PERIOD,COOL_PERIOD]:
#         if period in time_horizon:
#             given_period = time_horizon[period]
#             data = read_time_data(given_period)


#     return
# %%
