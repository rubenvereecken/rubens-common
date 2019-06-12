from typing import *
from pathlib import Path
import time
import re


def timestamp() -> str:
    """
    Granularity is one second.
    """
    time_str = time.strftime("%d-%m-%Y-%H-%M-%S", time.gmtime())
    return time_str


def gen_experiment_id(prefix=None) -> str:
    """
    Suitable for directory name
    """
    time_str = timestamp()

    if prefix == '' or prefix is None:
        base_logpath = time_str
    else:
        base_logpath = '{}_{}'.format(prefix, time_str)

    return base_logpath

prefix_re = r'((?P<prefix>[^\/]*?)_)?'
timestamp_re = '(?P<timestamp>[0-9]{2}-[0-9]{2}-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2})'
condor_rep_re = '(\.(?P<rep>[0-9]+))?'

# This works with a full path, even with files following
logdir_re = re.compile(''.join((prefix_re, timestamp_re, condor_rep_re)))

def _clean_parts(parts: dict):
    if parts['rep'] is not None:
        parts['rep'] = int(parts['rep'])
    return parts

def inspect_experiment_id(full_path: Union[Path, str]) -> Dict:
    full_path = Path(full_path).resolve()

    match = logdir_re.search(str(full_path))
    if match is None:
        return None

    parts = match.groupdict()
    parts = _clean_parts(parts)
    return parts
