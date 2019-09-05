# coding:utf-8
import json
import os
bath_path = os.path.dirname(os.path.abspath(__file__))
print(bath_path)


def conf():
    with open(os.path.join(bath_path, 'conf.json')) as f:
        config = json.load(f)
    return config


CONFIG = conf()
