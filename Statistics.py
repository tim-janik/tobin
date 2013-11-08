# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import collections, time, calendar, re, Config, Mime, GeoInfo

# General Statistics
class Statistics (object):
  def __init__ (self, year = None):
    if not year:
      year = time.gmtime (time.time())[0]
    self.stat_year = year            # year of interest, defaults to now
    self.year_range = (calendar.timegm ((self.stat_year, 01, 01, 00, 00, 00)),
                       calendar.timegm ((self.stat_year + 1, 01, 01, 00, 00, 00)))      # half open timestamp interval
    self.leap_year = time.gmtime (calendar.timegm ([self.stat_year, 2, 29, 12, 59, 59])).tm_mon == 2
    self.year_days = 366 if self.leap_year else 365
    self.first_day = time.gmtime (calendar.timegm ([self.stat_year, 1, 1, 12, 59, 59])).tm_wday # 0 == Monday
    self.month_lengths = (31, 28 + self.leap_year, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    self.gauges = []            # [ GaugeIface ]
    self.visits = 0
    self.hits = 0
    self.last_hit_usecs = 0
    self.last_visits = {}       # (ip4addr, uagent) -> (time_stamp_usec, visitid)
    self.last_visitid = 0
    self.hour_stats = {}        # hourly_timestamp -> HourStat
    self.methods = {}           # string -> MethodString
    self.resources = {}         # string -> ResourceString
    self.queries = {}           # string -> QueryString
    self.protocols = {}         # string -> ProtocolString
    self.uagents = {}           # string -> UAgentString
    self.referrers = {}         # string -> ReferrerString
  def wordpress_url (self, url):
    '''Guess if "url" is a Wordpress file or directory'''
    if url.startswith ('/wp-'):
      slash = url.find ('/', 1)
      part = url[1:slash] if slash > 0 else url[1:]
      return part in self._wp_entries
    return False
  _wp_entries = set ('''wp-admin wp-content wp-includes wp-activate.php wp-blog-header.php wp-comments-post.php
                        wp-config-sample.php wp-cron.php wp-links-opml.php wp-load.php wp-login.php wp-mail.php
                        wp-settings.php wp-signup.php wp-trackback.php'''.split())
  def hide_url (self, url):
    '''Guess if "url" is an auxillary asset like an image or css file'''
    if self.wordpress_url (url):
      return True
    dot = url.rfind ('.')
    slash = url.rfind ('/')
    if dot < 0 or dot <= slash:
      return False                      # guessing text/html
    ext = url[dot:].lower()
    if ext in ('.css', '.rss'):
      return True                       # hide common web assets
    m = Mime.guess_extension_mime (ext, 'text/x-unknown')
    return not m.startswith ('text/')   # gues text/... is usually interesting
  def is_pagespeed_referrer (self, string):
    return string.startswith ('Serf/') and mpgs_pattern.match (string)
  _mpgs_pattern = re.compile (r'Serf/[0-9.-]* mod_pagespeed/[0-9.-]$')
  def is_content_status (self, http_status):
    return self._http_status_types.get (http_status) == 'C'
  _http_status_types = { # T-Temporary, C-Content, M-Modified, R-Redirect, E-ServerError, 4-Missing
    100 : 'T', # Continue
    101 : 'T', # Switching Protocols
    102 : 'T', # Processing WebDAV
    200 : 'C', # OK
    201 : 'M', # Created
    202 : 'T', # Accepted
    203 : '-', # Non-Authoritative Information
    204 : '-', # No Content
    205 : 'M', # Reset Content
    206 : 'C', # Partial Content
    207 : 'M', # Multi-Status WebDAV
    208 : '-', # Already Reported WebDAV
    226 : 'M', # IM Used
    300 : 'R', # Multiple Choices
    301 : 'R', # Moved Permanently
    302 : 'R', # Found
    303 : 'R', # See Other
    304 : 'C', # Not Modified
    305 : 'R', # Use Proxy
    306 : 'R', # Switch Proxy
    307 : 'R', # Temporary Redirect
    308 : 'R', # Permanent Redirect
    400 : '-', # Bad Request
    404 : '4', # Not Found
    451 : '-', # Unavailable For Legal Reasons
    500 : 'E', # Internal Server Error
    503 : 'E', # Service Unavailable
    507 : 'E', # Insufficient Storage
    }
  def is_stat_year_timestamp (self, timestamp):
    return timestamp >= self.year_range[0] and timestamp < self.year_range[1]
  def submit_method (self, string, tx_bytes, new_visit):
    method = self.methods.get (string)
    if not method:
      method = MethodString (string)
      self.methods[method.string] = method
    method.submit (tx_bytes, new_visit)
    return method
  def submit_resource (self, string, tx_bytes, new_visit):
    resource = self.resources.get (string)
    if not resource:
      resource = ResourceString (string)
      self.resources[resource.string] = resource
    resource.submit (tx_bytes, new_visit)
    return resource
  def submit_query (self, string, tx_bytes, new_visit):
    query = self.queries.get (string)
    if not query:
      query = QueryString (string)
      self.queries[query.string] = query
    query.submit (tx_bytes, new_visit)
    return query
  def submit_protocol (self, string, tx_bytes, new_visit):
    protocol = self.protocols.get (string)
    if not protocol:
      protocol = ProtocolString (string)
      self.protocols[protocol.string] = protocol
    protocol.submit (tx_bytes, new_visit)
    return protocol
  def submit_referrer (self, string, tx_bytes, new_visit):
    referrer = self.referrers.get (string)
    if not referrer:
      referrer = ReferrerString (string)
      self.referrers[referrer.string] = referrer
    referrer.submit (tx_bytes, new_visit)
    return referrer
  def submit_uagent (self, string, tx_bytes, new_visit):
    uagent = self.uagents.get (string)
    if not uagent:
      uagent = UAgentString (string)
      self.uagents[uagent.string] = uagent
    uagent.submit (tx_bytes, new_visit)
    return uagent
  def walk_hits (self, rawhit_iter):
    for rawhit in rawhit_iter:
      (ipaddr, ruser, luser, time_stamp_usec, method, resource, query, protocol, http_status, tx_bytes, referrer, uagent) = rawhit
      # ensure ascending submissions, select statistic year
      assert time_stamp_usec >= self.last_hit_usecs
      self.last_hit_usecs = time_stamp_usec
      if (not self.is_stat_year_timestamp (time_stamp_usec / 1000000) or
          self.is_pagespeed_referrer (referrer) or
          not self.is_content_status (http_status)):
        continue
      # determine new visits
      vkey = (ipaddr, uagent)
      vlast = self.last_visits.get (vkey, None)
      if vlast == None or time_stamp_usec - vlast[0] > Config.visit_timeout_usec:
        new_visit = True
        self.visits += 1
        self.last_visitid += 1
        vlast = (time_stamp_usec, self.last_visitid)
        self.last_visits[vkey] = vlast
        if self.last_visitid & 0xffff == 0:
          for k,v in self.last_visits.items():
            if v[0] + 3600000000 + 3 * Config.visit_timeout_usec < time_stamp_usec:
              del self.last_visits[k]
      else:
        new_visit = False
        vlast = (time_stamp_usec, vlast[1])
        self.last_visits[vkey] = vlast
      self.hits += 1
      # collect string stats
      method_stat = self.submit_method (method, tx_bytes, new_visit)
      resource_stat = self.submit_resource (resource, tx_bytes, new_visit)
      query_stat = self.submit_query (query, tx_bytes, new_visit)
      protocol_stat = self.submit_protocol (protocol, tx_bytes, new_visit)
      referrer_stat = self.submit_referrer (referrer, tx_bytes, new_visit)
      uagent_stat = self.submit_uagent (uagent, tx_bytes, new_visit)
      hit = (ipaddr, time_stamp_usec, method_stat, resource_stat, query_stat, protocol_stat, http_status, tx_bytes, referrer_stat, uagent_stat)
      # collect hourly stats
      time_hstamp = time_stamp_usec // 3600000000 * 3600 # timestamp in seconds, quantized to hours
      hstat = self.hour_stats.get (time_hstamp)
      if not hstat:
        hstat = HourStat (time_hstamp)
        self.hour_stats[hstat.timestamp] = hstat
      hstat.submit (hit, new_visit)
      # collect gauge stats
      for g in self.gauges:
        g.hit (hit, vlast[1], new_visit)
  def done (self):
    for g in self.gauges:
      g.done()
  def as_html (self, destdir):
    elements = []
    for g in self.gauges:
      htm = g.as_html (destdir)
      if hasattr (htm, '__iter__'):
        elements.extend (htm)
      else:
        elements += [ htm ]
    return elements

# String Statistics
class StringStat (object):
  __slots__ = ('string', 'visits', 'urls', 'bytes')
  def __init__ (self, string):
    self.string = string
    self.visits = 0
    self.urls = 0       # URL hits
    self.bytes = 0
  def __hash__ (self):
    return hash (self.string)
  def __repr__ (self):
    return 'StringStat("%s",%u,%u,%u)' % (self.string, self.visits, self.urls, self.bytes)
  def submit (self, tx_bytes, new_visit):
    self.urls += 1
    self.bytes += tx_bytes
    if new_visit:
      self.visits += 1
class MethodString (StringStat): pass
class ResourceString (StringStat): pass
class QueryString (StringStat): pass
class ProtocolString (StringStat): pass
class UAgentString (StringStat): pass
class ReferrerString (StringStat): pass

# Hourly Statistics
class HourStat (object):
  __slots__ = ('timestamp', 'visits', 'urls', 'bytes', 'countries', 'year', 'month', 'mday', 'hour', 'wday', 'yday')
  def __init__ (self, timestamp):
    self.timestamp = timestamp
    self.visits = 0
    self.urls = 0
    self.bytes = 0
    self.countries = collections.defaultdict (int) # country_code -> visits
    tm = time.gmtime (self.timestamp) # (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst)
    self.year = tm.tm_year
    self.month = tm.tm_mon
    self.mday = tm.tm_mday
    self.hour = tm.tm_hour
    self.wday = tm.tm_wday
    self.yday = tm.tm_yday
  def submit (self, hit, new_visit):
    ipaddr, tx_bytes = hit[0], hit[7]
    self.urls += 1
    self.bytes += tx_bytes
    if new_visit:
      self.visits += 1
      cc = GeoInfo.lookup (ipaddr)
      self.countries[cc] += 1

class GaugeIface (object):
  __slot__ = ('statistics',)
  def __init__ (self, statistics):
    self.statistics = statistics
  def hit (self, hit, visitid, new_visit):
    pass
  def done (self):
    pass
  def as_html (self, destdir):
    return []
