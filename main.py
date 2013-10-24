#!/usr/bin/env python
# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, Config, os

Config.package_install_configuration ({
  #@PACKAGE_INSTALL_CONFIGURATION_PAGE1@        # configuration settings substituted upon script installation
})
tmpprefix = Config.package_name + '-tmp'

def die (exitcode, message, filename = None):
  error_message = '%s: ' % sys.argv[0]
  if filename:
    error_message += '%s: ' % filename
  error_message += message
  print >>sys.stderr, error_message
  sys.exit (exitcode)

def main (argv):
  # process command line arguments
  files = Config.parse_args (argv[1:])
  if not files:
    print >>sys.stderr, '%s: %s' % (sys.argv[0], 'missing input files')
    print >>sys.stderr, Config.usage_help()
    sys.exit (1)
  # preprocess input, write to and read from JSON temporary file
  if not os.access ('./xstat', os.X_OK | os.R_OK):
    die (2, "missing internal helper './xstat'")
  import tempfile, subprocess, json
  tfile, tname = tempfile.mkstemp (prefix = tmpprefix + 'logs', suffix = '.json')
  os.close (tfile)
  rcode = subprocess.call ('./xstat ' + ' '.join (files) + ' >' + tname, shell = True)
  if rcode != 0:
    os.unlink (tname) # cleanup
    die (3, "failed to preprocess log files (exitcode=%d)" % rcode)
  logdata_dict = json.load (open (tname, 'rb'))
  os.unlink (tname)
  print "LOGDATA:", logdata_dict.keys()

main (sys.argv)
