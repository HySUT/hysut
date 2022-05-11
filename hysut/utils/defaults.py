from functools import cached_property
import os
import cvxpy as cp


class Time:

    SLICE_NAME = "time_slice"
    T_SLICE = [1]


class ModelSettings:
    """Defines the default values for model settings in model_config along with validation methods
    """

    KEYS = ["solver", "log_path"]

    @cached_property
    def solver(self):
        free_solvers = ["CVXOPT", "ECOS", "ECOS_BB", "GLPK", "OSQP", "SCIPY"]

        for solver in free_solvers:
            if solver in cp.installed_solvers():
                return solver

        raise

    @cached_property
    def log_path(self):
        return r"{}/logs".format(os.getcwd())

    def validate_solver(self,solver):
        warning = []
        if solver.upper() in cp.installed_solvers():
            solver = solver.upper()

        else:

            warning.append(f'{solver} is not a valid solver or not installed on your machine. Default solver ({self.solver}) is used.')
            solver = self.solver
        return {'warning':warning,'value':solver}

    def validate_log_path(self,path):
        warning = []
        if not isinstance(path,str):
            path = self.log_path
            warning.append(f'log_path should be str. Default log_path ({path}) is used.')

        return {'warning':warning,'value':path}
