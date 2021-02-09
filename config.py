# -*- coding:utf-8 -*-
from pathlib import Path

ROOT_PATH = Path.cwd().joinpath('data')
DATA_PATH = ROOT_PATH.joinpath('data.txt')
DB_PATH = ROOT_PATH.joinpath('database.db').as_posix()
