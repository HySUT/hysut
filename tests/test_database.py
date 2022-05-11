import sys
import os
import pytest



sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from hysut.preprocess.database import ModelDataBase
from hysut.utils.defaults import ModelSettings
from hysut.utils.enums import SETTINGS

def test_model_settings():
    settings = ModelSettings()

    # no settings passed
    test = ModelDataBase({})
    test._check_model_settings()

    for item in settings.KEYS:
        assert test.model_config[SETTINGS][item] == getattr(settings, item)
