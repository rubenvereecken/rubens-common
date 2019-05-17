from rubens.exp.conf_gen import do_configs, confs_path, load_config


if __name__ == '__main__':
    spec = {
        'term_prior_mean': [-.5, -1, -2],
        'term_prior_var': [1, 2, 4],
    }

    fixed_config = {
        # 'option_observer': 'psr.games.craft.CraftPro1',
        'option_observer': 'psr.games.craft.CraftOneHot500',
        'num_options': 1,
    }

    import pkg_resources
    prod_conf_path = pkg_resources.resource_filename('irl', 'conf/prod.conf')
    fixed_config.update(load_config(prod_conf_path)['DEFAULT'])

    prefix = 'term_priors0'

    do_configs(spec, prefix=prefix, path=confs_path.joinpath(prefix), fixed=fixed_config)

