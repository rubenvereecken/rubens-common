#!/usr/bin/env python

from pathlib import Path
import sys
import os
import argparse
import logging

import jinja2 as j2
from configparser import ConfigParser

BASE_PATH = Path('/vol/hmi/projects/ruben')
BASE_LOGPATH = BASE_PATH.joinpath('log')
conda_base_path = BASE_PATH.joinpath('miniconda')

here = Path(__file__).parent
TEMPLATES_PATH = here.joinpath('templates')

class LeaveItUndefined(j2.Undefined):
    """
    Leaves undefined variables as template things.
    Only works when using {{ var }}.  Good for partial templates.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        logging.warn("Leaving variable '%s'", self.name)
        return '{{{{ {} }}}}'.format(self.name)


def generate_discovery_job(config_path, base_logpath, extra_args={}):
    config_path = Path(config_path).resolve()
    config = ConfigParser()
    config.read(str(config_path))
    prefix = config['framework']['prefix']

    env = dict(
        LD_LIBRARY_PATH='{}/lib:$ENV(LD_LIBRARY_PATH)'.format(str(conda_base_path)),
        PYTHONHOME=str(conda_base_path),
        PYTHONHASHSEED=0,
    )

    # TODO UNUSED
    pargs = dict(
        logpath=base_logpath.joinpath(prefix),
    )

    tpl_args = dict(
        python=str(conda_base_path.joinpath('bin/python')),
        base_path=str(BASE_PATH),
        env_string=' '.join('{}={}'.format(k, v) for k, v in env.items()),
        prefix=prefix,
        # Send it over to target machine
        config_path=config_path,
        args=extra_args['args'],
    )

#     if extra_args:
#         logging.info("Overwriting %s", extra_args.keys())
#         tpl_args.update(extra_args)

    # Change the `undefined` parameter for different undefined behaviour
    tpl_env = j2.Environment(loader=j2.FileSystemLoader('templates/'),
                             undefined=j2.Undefined)
    tpl = tpl_env.get_template('discovery_job.tpl')
    # tpl = Template(tpl_path.read_text())
    job = tpl.render(**tpl_args)
    return job


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('config_paths', type=str, nargs='+')
    parser.add_argument('-l', '--base_logpath', type=str)
    parser.add_argument('-o', '--out', type=str)
    parser.add_argument('-n', '--dry', action='store_true', default=False)
    parser.add_argument('-a', '--args', nargs='+')
    args, other = parser.parse_known_args()

    if other:
        print('unknown args', other)

    if args.out:
        args.out = Path(args.out)
        args.out.mkdir(exist_ok=True, parents=True)

    if args.args:
        extra_args = { 'args': ' '.join(args.args) }
    else:
        extra_args = {}

    if args.base_logpath is None:
        args.base_logpath = BASE_LOGPATH
        logging.warning("Falling back to default logpath %s", BASE_LOGPATH)

    for config_path in args.config_paths:
        config_path = Path(config_path)
        job = generate_discovery_job(config_path, args.base_logpath, extra_args)
        if args.out:
            job_path = args.out.joinpath(config_path.stem).with_suffix('.job')
        else:
            job_path = config_path.with_suffix('.job')

        if args.dry:
            print('Saving to', str(job_path), '\n')
            print(job, '\n')
            continue

        job_path.write_text(job)


if __name__ == '__main__':
    main()
