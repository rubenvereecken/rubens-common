import argparse
from rubens.exp.conf_gen import do_configs, confs_path, load_config
from rubens.naming import inspect_experiment_id
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('options_path', type=str)
    parser.add_argument('-l', '--levelfile', required=True)
    parser.add_argument('-p', '--prefix', type=str)
    args = parser.parse_args()

    # This will be turned into a filename.. so doesn't work with path values
    spec = {
    }

    fixed_config = {
        'options': args.options_path,
        'abstract_actions': 'full',
        'domainfile': '/vol/hmi/projects/ruben/packages/psr/psr/games/craft/craft_axe.txt',
        # 'levelfile': '/vol/hmi/projects/ruben/packages/psr/psr/craftworld_axe_4x4/0.txt',
        'levelfile': args.levelfile,
    }

    import pkg_resources
    prod_conf_path = pkg_resources.resource_filename('psr', 'conf/craft-irl.conf')
    fixed_config.update(load_config(prod_conf_path)['DEFAULT'])

    prefix = inspect_experiment_id(args.options_path)['prefix']
    levelname = Path(args.levelfile).stem

    # Fall back to prefix with level name
    if args.prefix is None:
        args.prefix = levelname
    if args.prefix:
        prefix = args.prefix + '_' + prefix

    # Will only hold one but ah well
    # path = confs_path.joinpath('train_irl_' + levelname).joinpath(prefix)
    path = confs_path.joinpath(args.prefix).joinpath(prefix)

    do_configs(spec, prefix=prefix, path=path, fixed=fixed_config)
