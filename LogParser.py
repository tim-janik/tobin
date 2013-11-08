# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import sys, calendar

_month_dict = { 'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' :  4, 'May' :  5, 'Jun' :  6,
                'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12 }
def parse_logtime (string):
  # e.g. string = '07/Aug/2013:21:14:18 +0200'
  tup = (int (string[7:11]), _month_dict[string[3:6]], int (string[:2]),
         int (string[12:14]), int (string[15:17]), int (string[18:20]))
  tzone = int (string[22:24]) * 3600 + int (string[24:26]) * 60 # TZ offset in seconds
  seconds = calendar.timegm (tup) # this is faster than using strptime
  if string[21] == '+':
    seconds -= tzone
  else:
    seconds += tzone
  return seconds # unix time stamp in UTC

def log_line_parser (logfile):
  import re
  s    = r'\s+'                                                 # sparator
  ip   = r'([0-9.abcdef:ABCDEF]{7,39})'                         # ip4/ip6 addresses
  #idt = r'([\w\d/.$+-]+)'                                      # unquoted identifier (too strict for some corrupted user names)
  idt  = r'([^\s]+)'                                            # space separated string
  num  = r'([0-9]{1,9})'                                        # integer
  xnum = r'(-|[0-9]{1,9})'                                      # maybe integer
  dt   = r'\[(\d\d/\w\w\w/\d{4}:\d\d:\d\d:\d\d\s[+-]\d{4})\]'   # [dd/MMM/yyyy:hh:mm:ss +-zone]
  #qx  = r'"((?:[^"\\]|\\.)*)"'                                 # quoted text (slow), allows escaped quotes
  qx   = r'"([^"\\]*(?:[^"\\]|\\.)*)"'                          # fast quoted text, unconditionalize/speed up the common case
  logpattern = re.compile (ip + s + idt + s + idt + s + dt + s + qx + s + num + s + xnum + '(?:' + s + qx + s + qx + ')?')
  urlpattern = re.compile (r'([A-Z]+)\s(.*)\s(HTTP[0-9./]*)$')
  lineno = 0
  for line in logfile:
    lineno += 1
    m = logpattern.match (line)
    u = urlpattern.match (m.group (5)) if m else None
    if not m or not u:
      print >>sys.stderr, '%s: malformed: %s:%u: %s' % (sys.argv[0], logfile.name, lineno, line)
      continue
    hit = m.groups()
    time_stamp_usec = 1000000 * parse_logtime (hit[3])          # time_stamp_usec
    http_status = int (hit[5])                                  # http_status
    tx_bytes = 0 if hit[6] == '-' else int (hit[6])             # tx_bytes
    referrer = '' if hit[7] == '-' else hit[7]                  # referrer
    uagent = '' if hit[8] == '-' else hit[8]                    # uagent
    # split request URL
    method = u.group (1)
    url = u.group (2)
    protocol = u.group (3)
    qpos = url.find ('?')
    resource, query = (url[:qpos], url[qpos:]) if qpos >= 0 else (url, '')
    # yield result
    yield (hit[0], hit[1], hit[2], time_stamp_usec, method, resource, query, protocol, http_status, tx_bytes, referrer, uagent)

def log_line_sorter (line_iter):
  sl = sorted (line_iter, key = lambda e: e[3])         # key = time_stamp_usec
  for e in sl:
    yield e
