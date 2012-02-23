import os
from os.path import dirname, abspath, join

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

activate_this = os.path.join(_PROJECT_ROOT, "ve/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

os.environ['AUTHZ_SETTINGS_OVERRIDE'] = os.path.join(_PROJECT_ROOT, 'app.cfg')

from authz.application import create
application = create()
