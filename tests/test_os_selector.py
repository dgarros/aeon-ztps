import imp
import os
import yaml
import tempfile
import pytest
import json


bin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../bin')

os_selector = imp.load_source('aztp_os_selector', os.path.join(bin_path, 'aztp_os_selector'))


def os_sel_file(contents=None):
    """
    Used to create a temporary os-selector file
    :param contents: python dictionary that will be converted to yaml
    :return: returns a temporary file string
    """
    if not contents:
        contents = {'default': {
                'regex_match': '3\.1\.[12]',
                'image': 'CumulusLinux-3.1.2-amd64.bin'}}
    os_sel = tempfile.TemporaryFile()
    os_sel.write(yaml.dump(contents, default_flow_style=False))
    return os_sel


def test_cli_parse():
    osf = os_sel_file()
    parse = os_selector.cli_parse(['-j', '{"test_key": "test_value"}', '-c', str(osf)])
    assert json.loads(parse.json)['test_key'] == 'test_value'
    assert parse.config_file == str(osf)


def test_cli_parse_parsererror():
    osf = os_sel_file()
    with pytest.raises(os_selector.ArgumentParser.ParserError) as e:
        parse = os_selector.cli_parse(['-c', str(osf)])
    assert 'ParserError' in str(e)


def test_exit_results():
    results = json.loads('{"ok": "True"}')
    try:
        os_selector.exit_results(results)
    except SystemExit as e:
        print e