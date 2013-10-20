# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys

# Config defaults
sitename = 'Localhost'



# wrap Config module to handle unknown settings
class ConfigModule (object):
  def __init__ (self, sysmodule):
    self._sysmodule = sysmodule
  def __getattr__ (self, name):
    try:
      return getattr (self._sysmodule, name)
    except AttributeError:
      return None
sys.modules[__name__] = ConfigModule (sys.modules[__name__])
# +++ add nothing after ConfigModule has been installed +++
