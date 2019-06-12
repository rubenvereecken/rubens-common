from typing import *
from pathlib import Path
import sys
import yaml

from rubens.naming import logdir_re, inspect_experiment_id

def main():
    full_path = input()
    parts = inspect_experiment_id(full_path)

    if parts is None:
        sys.exit("Not a logdir? No match found for %s" % full_path)

    out = yaml.dump(parts)
    print(out)
