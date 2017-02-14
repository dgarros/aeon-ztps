import pytest
import sys
import re
import mock
from aeon_ztp.bin import cumulus_bootstrap
from StringIO import StringIO
from aeon.cumulus.device import Device

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

facts = {
    'os_name': 'cumulus-vx',
    'vendor': 'cumulus',
    'hw_part_number': '1234',
    'hostname': 'cumulus',
    'fqdn': 'cumulus.localhost',
    'virtual': True,
    'service_tag': '1234',
    'os_version': '3.1.1',
    'hw_version': '1234',
    'mac_address': '0123456789012',
    'serial_number': '09786554',
    'hw_model': 'cvx1000'
}


@mock.patch('aeon.cumulus.device.Connector')
@pytest.fixture()
def device(mock_con):
    dev = Device(args['target'], no_probe=True, no_gather_facts=True)
    dev.facts = facts
    return dev


@pytest.fixture(scope='session')
def cli_args():

    parse = cumulus_bootstrap.cli_parse(['--target', args['target'],
                                         '--server', args['server'],
                                         '--topdir', args['topdir'],
                                         '--logfile', args['logfile'],
                                         '--reload-delay', args['reload_delay'],
                                         '--init-delay', args['init_delay'],
                                         '--user', args['user'],
                                         '--env_user', args['env_user'],
                                         '--env_passwd', args['env_passwd']])
    return parse


@mock.patch('aeon_ztp.bin.cumulus_bootstrap.requests.put')
@pytest.fixture(scope='session')
def cb_obj(mock_requests, cli_args):
    cb = cumulus_bootstrap.CumulusBootstrap(args['server'], cli_args)
    return cb


def test_cli_parse(cli_args):
    for arg in vars(cli_args):
        assert str(getattr(cli_args, arg)) == args[arg]


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


def test_cumulus_bootstrap(cli_args, cb_obj):
    assert args['server'] == cb_obj.self_server
    assert cli_args == cb_obj.cli_args


@mock.patch('aeon_ztp.bin.cumulus_bootstrap.requests')
def test_post_device_facts(mock_requests, device, cb_obj):
    cb_obj.post_device_facts(device)
    mock_requests.put.assert_called_with(json={
        'os_version': facts['os_version'],
        'os_name': cumulus_bootstrap._OS_NAME,
        'ip_addr': device.target,
        'hw_model': facts['hw_model'],
        'serial_number': facts['serial_number']
    },
        url='http://{}/api/devices/facts'.format(args['server']))


@mock.patch('aeon_ztp.bin.cumulus_bootstrap.requests')
def test_post_device_status(mock_requests, device, cb_obj):
    kw = {
        'dev': device,
        'target': device.target,
        'message': 'Test message',
        'state': 'DONE'
    }
    cb_obj.post_device_status(**kw)
    mock_requests.put.assert_called_with(json={
        'message': kw['message'],
        'os_name': cumulus_bootstrap._OS_NAME,
        'ip_addr': device.target,
        'state': kw['state']
    },
        url='http://{}/api/devices/status'.format(args['server']))


@mock.patch('aeon_ztp.bin.cumulus_bootstrap.CumulusBootstrap.post_device_status')
def test_exit_results(mock_post, cb_obj, device):
    kw = {
        'results': {'ok': True},
        'dev': device,
        'target': device.target,
        'exit_error': None,
    }
    with pytest.raises(SystemExit) as e:
        cb_obj.exit_results(**kw)
    mock_post.assert_called_with(
        dev=kw['dev'],
        target=kw['target'],
        state='DONE',
        message='bootstrap completed OK'
    )
    assert e.value.code == 0

    # Test bad exit
    kw = {
        'results': {'ok': False,
            'message': 'Error Message'},
        'dev': device,
        'target': device.target,
        'exit_error': 1,
    }
    with pytest.raises(SystemExit) as e:
        cb_obj.exit_results(**kw)
    mock_post.assert_called_with(
        dev=kw['dev'],
        target=kw['target'],
        state='FAILED',
        message=kw['results']['message']
    )
    assert e.value.code == 1
