import yaml
from collections import namedtuple

class Device(object):
    def __init__(self, **kwargs):
        self.facts = kwargs

mac_dev = Device(mac_address='0123456789012', serial_number='1111111111', hw_model='0000000')
sn_dev = Device(mac_address='000000000000', serial_number='987654321', hw_model='000000000')
hw_dev = Device(mac_address='000000000000', serial_number='000000000', hw_model='987654321')

cfg_data = yaml.safe_load(open('/Users/bwatson/Projects/aeon-ztps/etc/profiles/sample/cumulus/os-selector.cfg'))
item_match = namedtuple('item_match', ['hw_match', 'data'])

matches = []


for group in cfg_data.iteritems():
    if group[0] != 'default':
        for fact_key, fact_value in group[1]['matches'].iteritems():
            if hw_dev.facts[fact_key] not in str(fact_value):
                # Stop checking this device group if any of the matches don't match
                break
        else:
            # If all matches in match group match, return item_match
            matches.append(group[0])
            print item_match(group[0], cfg_data[group[0]])

print matches