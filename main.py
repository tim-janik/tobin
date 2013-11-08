#!/usr/bin/env python
# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, os, Config, Statistics, Report

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
  # read, parse and sort input
  import LogParser
  if len (files) != 1:
    die (1, 'exactly one input file required') # FIXME: support multiple files
  filehandle = open (files[0])
  lparser_unsorted = LogParser.log_line_parser (filehandle)
  lparser = LogParser.log_line_sorter (lparser_unsorted)
  # collect statistics
  stats = Statistics.Statistics()
  import TopVisits
  stats.gauges += [ TopVisits.TopVisits (stats) ]
  stats.walk_hits (lparser)
  stats.done()
  # generate report
  print "Hits:\t%s" % stats.hits
  print "Visits:\t%s" % stats.visits
  destdir = './logreport'
  statistics_html_content = stats.as_html (destdir)
  if not os.path.isdir (destdir) or not os.access (destdir, os.X_OK):
    try:
      os.mkdir (destdir)
    except OSError, ex:
      die (5, "failed to create or access directory %s: %s" % (destdir, ex.strerror))
  Report.generate (destdir, statistics_html_content)

main (sys.argv)
