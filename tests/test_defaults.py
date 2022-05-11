import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from cvxpy import installed_solvers
from hysut.utils.defaults import ModelSettings


def test_ModelSettings():

    settings = ModelSettings()

    # wrong solver
    output = settings.validate_solver('dummy')
    expected_output = {"value":settings.solver,'warning':[f'dummy is not a valid solver or not installed on your machine. Default solver ({settings.solver}) is used.']}

    assert output == expected_output

    # wrong log_path
    output = settings.validate_log_path(12)
    expected_output = {"value":settings.log_path,"warning":[f'log_path should be str. Default log_path ({settings.log_path}) is used.']}