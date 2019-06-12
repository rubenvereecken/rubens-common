from rubens.exp.conf_gen import do_configs, confs_path, load_config


if __name__ == '__main__':
    spec = {
        'option_observer': ['psr.games.craft.CraftPRO{}'.format(k) for k in range(1,4+1)],
        'num_options': [1, 2],
        'term_prior_var': [1, 2, 3],
        'term_prior_mean': [0, -1, -2, -3],
    }

    fixed_config = {
        # 'term_prior_mean': 2,
    }

    import pkg_resources
    prod_conf_path = pkg_resources.resource_filename('irl', 'conf/prod.conf')
    fixed_config.update(load_config(prod_conf_path)['DEFAULT'])

    prefix = 'irl_options1'

    do_configs(spec, prefix=prefix, path=confs_path.joinpath(prefix), fixed=fixed_config)

