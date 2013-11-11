# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, os, socket

# Package defaults
package_name, package_url = 'tobin', 'http://testbit.eu/tobin'
package_version, package_buildid = ('0.0-uninstalled', 'untracked')
package_datadir = '.'
package_title = package_name.capitalize()
# Config defaults
sitename = socket.gethostname()         # default site title
visit_timeout_usec = 1800 * 1000000     # time within which URLs from the same IP/UA are considered the same visit
stat_year = 2000                        # dynamically initialized from main

# Command line argument processing, usage and version
def version_info():
  return '%s %s (Build ID: %s)' % (package_title, package_version, package_buildid)
def usage_help():
  h = ''
  h += 'Usage: %s [OPTIONS] LOGFILES...\n' % package_name
  h += 'Options:\n'
  h += '  -h, --help                    Display this help and exit\n'
  h += '  -v, --version                 Display version and exit\n'
  h += '  -n, --name=<sitename>         Website name for the generated report\n'
  h += '  -y, --year=<year>             Year for which to generate report\n'
  return h.strip()
def process_arg (arg, val):
  if   arg == '-h' or arg == '--help':
    print usage_help()
    sys.exit (0)
  elif arg == '-v' or arg == '--version':
    print version_info()
    sys.exit (0)
  elif arg == '-n' or arg == '--name':
    global sitename
    sitename = val
  elif arg == '-y' or arg == '--year':
    global stat_year
    stat_year = val
def parse_args (args):
  import getopt
  short_options = 'h v n: y:'.replace (' ', '') # 'f:'
  long_options  = 'help version name= year='.split() # 'foo='
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

# Install package configuration
def package_install_configuration (pkgdict):
  for k in pkgdict.keys():
    assert k.startswith ('package_')
  globals().update (pkgdict)

# Wrap Config module to handle unknown settings
class ConfigModule (object):
  def __init__ (self, sysmodule):
    self.__dict__.update ({ '_sysmodule' : sysmodule })
  def __delattr__ (self, name):
    return self._sysmodule.__delattr__ (name)
  def __setattr__ (self, name, val):
    return self._sysmodule.__setattr__ (name, val)
  def __getattr__ (self, name):
    try:
      return getattr (self._sysmodule, name)
    except AttributeError:
      return None
sys.modules[__name__] = ConfigModule (sys.modules[__name__])
# +++ add nothing after ConfigModule has been installed +++
