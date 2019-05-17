from typing import*
from itertools import product
from pathlib import Path

from configparser import ConfigParser

confs_path = Path(__file__).parent.joinpath('confs')

def generate_spec_dicts(spec) -> List[Dict[str, Any]]:
    specs = [dict(zip(spec.keys(), conf)) for conf in product(*spec.values())]
    return specs

def generate_prefix(spec: Dict) -> str:
    bits = [ '{}_{}'.format(k, v) for k, v in spec.items() ]
    s = '-'.join(bits)
    return s

def generate_configs(spec: Dict[str, List]):
    """
    Relies on spec being sorted I believe
    """
    specs = generate_spec_dicts(spec)

    for spec in specs:
        config = ConfigParser()
        config['framework'] = { 'prefix': generate_prefix(spec) }
        config['params'] = spec
        yield config

def print_config(config: ConfigParser):
    import io
    with io.StringIO() as f:
        config.write(f)
        f.flush()
        f.seek(0)
        print(f.read())
    return config

def do_configs(spec, prefix=None, path=None, fixed={}):
    if path is None:
        path = Path(__file__).parent.joinpath('confs')
    path = Path(path)

    path.mkdir(parents=True, exist_ok=True)

    for config in generate_configs(spec):
        if fixed:
            config['common'] = fixed

        name = config['framework']['prefix']
        if prefix:
            name = 'prefix_{}'.format(name)

        # TODO
        # config['framework']['logpath'] = 'log/' + name

        print_config(config)
        config_path = path.joinpath(name + '.conf')
        with config_path.open('w') as f:
            config.write(f)

def load_config(config_path) -> ConfigParser:
    config_path = Path(config_path)
    # Bit dirty, but also load production settings
    config = ConfigParser()
    # config_str = Path(__file__).parent.parent.joinpath('conf/prod.conf').read_text()
    config_str = config_path.read_text()
    print(config_str)
    assert not '[' in config_str, 'Didnt expect headers'
    config_str = '[DEFAULT]\n' + config_str
    config.read_string(config_str)
    return config
