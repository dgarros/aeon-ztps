import sys
import re
from bin import cumulus_bootstrap
from StringIO import StringIO


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


def test_setup_logging():

    # Suppress stdout from log testing
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        log = cumulus_bootstrap.setup_logging('test_log', None, '1.1.1.1')
        log.info('testing logging')
        sys.stdout.flush()
        new_stdout = sys.stdout.getvalue()
    finally:
        # resume stdout
        sys.stdout.close()
        sys.stdout = old_stdout
    log_search = re.search('(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}:INFO:1.1.1.1:testing logging\n)', new_stdout)
    assert log_search.group(0) == new_stdout