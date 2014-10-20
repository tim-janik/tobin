#!/usr/bin/env python
# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, os, time, Config, Statistics, Report

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
  # set dynamic defaults
  Config.stat_year = time.gmtime (time.time())[0]
  # process command line arguments
  files = Config.parse_args (argv[1:])
  if not files:
    print >>sys.stderr, '%s: %s' % (sys.argv[0], 'missing input files')
    print >>sys.stderr, Config.usage_help()
    sys.exit (1)
  # read, parse and sort input
  import LogParser
  print >>sys.stderr, '%s: sorting %u files...' % (sys.argv[0], len (files))
  sort_pool = LogParser.log_file_sort_pool (files)
  print >>sys.stderr, '%s: parsing %u sorted files...' % (sys.argv[0], len (sort_pool))
  lparser = LogParser.log_file_parse_pool (sort_pool)
  # collect statistics
  stats = Statistics.Statistics (int (Config.stat_year))
  import TopVisits, DailyVisits, GeoHour
  stats.gauges += [ TopVisits.TopVisits (stats),
                    DailyVisits.DailyVisits (stats),
                    GeoHour.GeoHour (stats) ]
  stats.walk_hits (lparser)
  print >>sys.stderr, '%s: generating report...' % sys.argv[0]
  stats.done()
  # generate report
  print "Hits:\t\t%s" % stats.hits
  print "Visits:\t\t%s" % stats.visits
  print "Redirects:\t%s" % stats.redirects
  destdir = './logreport'
  if not os.path.isdir (destdir) or not os.access (destdir, os.X_OK):
    try:
      os.mkdir (destdir)
    except OSError, ex:
      die (5, "failed to create or access directory %s: %s" % (destdir, ex.strerror))
  statistics_html_content = stats.as_html (destdir)
  Report.generate (destdir, stats, statistics_html_content)

main (sys.argv)
