from tabulate import tabulate


def type_consistency_check(data_list, item=None):
    """Checks if all the item in a give list have uniform data type

    Parameters
    ----------
    data_list : list
        list of data
    item : str
        specific item which the check is performed (for better error message)

    Returns
    -------
    list
        list of errors if any
    """

    if not all([type(item) == type(data_list[0]) for item in data_list]):
        return [f"'{item}' is not allowed to have different data type."]

    return []


def read_range_function(range_data, item):
    """Reads the range function in data and create a list for the given range

    Parameters
    ----------
    range_data : str
        str resembling the range function
    item : str
        the given item that range function is given for (for better error definition)

    Returns
    -------
    dict
        retuning the dat and errors in a dict
    """
    data = []
    errors = []

    try:
        data = list(eval(range_data))
    except Exception as error:
        errors = [f"{arg} in 'range' for '{item}'." for arg in error.args]

    return {"data": data, "error": errors}


def print_log(logs, save_file=None):
    """Make a tabular log file to print as a string/ save in a file

    Parameters
    ----------
    logs : list
        list of errors/warnings
    save_file : str, optional
        if it is not None,should contain the directory to save the file , by default None

    Returns
    -------
    str
        tablulated log
    """

    table = [[i + 1, logs[i]] for i in range(len(logs))]
    table = tabulate(table, headers=["Number", "Error/Warning"], tablefmt="pretty")

    if save_file:
        with open(save_file, "w") as file:
            file.write(table)

    return table
