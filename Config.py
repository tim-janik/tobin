# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, os

# Package defaults
package_name = 'tobin'
package_version, package_buildid = ('0.0-uninstalled', 'untracked')
package_datadir = '.'
# Config defaults
sitename = 'Localhost'

# Accessors & helpers
def version_info():
  return '%s %s (Build ID: %s)' % (package_name, package_version, package_buildid)
def usage_help():
  h = ''
  h += 'Usage: %s [OPTIONS] LOGFILES...\n' % package_name
  h += 'Options:\n'
  h += '  -h, --help                    Display this help and exit\n'
  h += '  -v, --version                 Display version and exit\n'
  return h.strip()

# Data file access
def package_data_file (filename, mode = 'r'):
  fpath = package_datadir + '/' + filename
  amask = 0
  if 'r' in mode: amask |= os.R_OK
  if 'w' in mode: amask |= os.W_OK
  if 'x' in mode: amask |= os.X_OK
  if not os.access (fpath, amask):
    raise IOError ("access failed: '%s'" % fpath)
  if 'D' in mode and not os.path.isdir (fpath):
    raise IOError ("not a directory: '%s'" % fpath)
  return fpath

# Command line argument processing
def process_arg (arg, val):
  if   arg == '-h' or arg == '--help':
    print usage_help()
    sys.exit (0)
  elif arg == '-v' or arg == '--version':
    print version_info()
    sys.exit (0)
def parse_args (args):
  import getopt
  short_options = 'h v'.replace (' ', '') # 'f:'
  long_options  = 'help version'.split() # 'foo='
  try:
    options, files = getopt.gnu_getopt (args, short_options, long_options)
  except getopt.GetoptError, ex:
    exmsg = "unrecognized option '-%s'" % ex.opt if ex.opt else str (ex)
    print >>sys.stderr, "%s: %s" % (package_name, exmsg)
    print >>sys.stderr, "Use '%s --help' for more information." % package_name
    sys.exit (1)
  for arg, val in options:
    process_arg (arg, val)
  return files

# Install package configuration
def package_install_configuration (pkgdict):
  for k in pkgdict.keys():
    assert k.startswith ('package_')
  globals().update (pkgdict)

# Wrap Config module to handle unknown settings
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
