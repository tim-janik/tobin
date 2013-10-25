#!/usr/bin/env python
# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, os, Config, Report

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
  stat_hits = logdata_dict['hits']
  stat_urls = logdata_dict['urls']
  stat_queries = logdata_dict['queries']
  stat_referrers = logdata_dict['referrers']
  stat_uagents = logdata_dict['uagents']
  # walk hits and visits
  last_hit_usecs, visits = 0, {}
  xv, xh = 0, 0
  for hit in stat_hits:
    # check ascending submissions
    time_stamp_usec, ip4addr, uagent_quark = hit[0], hit[1], hit[7]
    assert time_stamp_usec >= last_hit_usecs
    # determine new visits
    vkey = (ip4addr, uagent_quark)
    vlast = visits.get (vkey, None)
    new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
    visits[vkey] = time_stamp_usec
    xh += 1
    xv += new_visit
  del (last_hit_usecs, visits, vkey, vlast, new_visit)
  print "Hits:\t%s" % xh
  print "Visits:\t%s" % xv
  # generate report
  destdir = './logreport'
  if not os.path.isdir (destdir) or not os.access (destdir, os.X_OK):
    try:
      os.mkdir (destdir)
    except OSError, ex:
      die (5, "failed to create or access directory %s: %s" % (destdir, ex.strerror))
  Report.generate (destdir)

main (sys.argv)
