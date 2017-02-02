import imp
import os

bin_path = os.path.realpath('bin')

cumulus_bootstrap = imp.load_source('cumulus_bootstrap', os.path.join(bin_path, 'cumulus_bootstrap'))
