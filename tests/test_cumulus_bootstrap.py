from bin import cumulus_bootstrap


def test_cli_parse():
    args = {
        'target': '1.1.1.1',
        'server': '2.2.2.2',
        'topdir': '/tmp/dir',
        'logfile': '/tmp/logfile',
        'reload_delay': '60',
        'init_delay': '90',
        'user': 'admin',
        'env_user': 'ENV_USER',
        'env_passwd': 'ENV_PASS'
    }
    parse = cumulus_bootstrap.cli_parse(['--target', args['target'],
                                         '--server', args['server'],
                                         '--topdir', args['topdir'],
                                         '--logfile', args['logfile'],
                                         '--reload-delay', args['reload_delay'],
                                         '--init-delay', args['init_delay'],
                                         '--user', args['user'],
                                         '--env_user', args['env_user'],
                                         '--env_passwd', args['env_passwd']])
    for arg in vars(parse):
        assert str(getattr(parse, arg)) == args[arg]