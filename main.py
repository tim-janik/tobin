#!/usr/bin/env python
# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, Config

Config.package_install_configuration ({
  #@PACKAGE_INSTALL_CONFIGURATION_PAGE1@        # configuration settings substituted upon script installation
})

def main (argv):
  files = Config.parse_args (argv[1:])
  if not files:
    print >>sys.stderr, '%s: %s' % (sys.argv[0], 'missing input files')
    print >>sys.stderr, Config.usage_help()
    sys.exit (1)
  else:
    print "PROCESS:", files
main (sys.argv)
