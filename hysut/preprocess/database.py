import pandas as pd
from hysut.preprocess.time import check_time_horizon
from hysut.utils.enums import TIME_HORIZON, SETTINGS
from hysut.exceptions_logging.exceptions import TimeHorizonError
from hysut.utils.defaults import ModelSettings
from hysut.utils.tools import print_log
from copy import deepcopy


class ModelDataBase:
    def __init__(self, model_config):
        self.warnings = []
        self.model_config = deepcopy(model_config)

    def _extract_time_horizon_data(self):
        time = check_time_horizon(self.model_config[TIME_HORIZON])
        errors = time["errors"]
        print(errors)
        self.warnings.extend(time["warnings"])
        if errors:
            save_directory = self.model_config[SETTINGS]["log_path"]
            print_log(logs=errors, save_file=save_directory + "/error_log.txt")
            raise TimeHorizonError(
                f"{len(errors)} exists in the definition of {TIME_HORIZON}. The errors are listed in the error_log file located at {save_directory}"
            )

        self.years = time["time_horizon"]

    def _check_model_settings(self):

        default_settings = ModelSettings()
        settings = self.model_config.setdefault(SETTINGS, {})

        for option in default_settings.KEYS:
            item_set = settings.setdefault(option, getattr(default_settings, option))

            validation = getattr(default_settings, "validate_" + option)(item_set)
            self.warnings.extend(validation["warning"])
            settings[option] = validation["value"]

        # check extra keys
        differences = set(settings).difference(default_settings.KEYS)
        if differences:
            self.warnings.append(
                f"Following keys in the model {SETTINGS} are not valid and are ignored: \n{differences}"
            )

        self.model_config[SETTINGS] = settings
