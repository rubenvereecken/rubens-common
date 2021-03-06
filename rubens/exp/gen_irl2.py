from rubens.exp.conf_gen import do_configs, confs_path, load_config


if __name__ == '__main__':
    spec = {
    }

    fixed_config = {
        'num_options': 2,
        'term_prior_var': 3,
        'term_prior_mean': 0,
        'option_observer': 'psr.games.craft.CraftPRO3',
    }

    import pkg_resources
    prod_conf_path = pkg_resources.resource_filename('irl', 'conf/prod.conf')
    fixed_config.update(load_config(prod_conf_path)['DEFAULT'])

    prefix = 'irl2'

    do_configs(spec, prefix=prefix, path=confs_path.joinpath(prefix), fixed=fixed_config)


