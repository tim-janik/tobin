# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config

# General Statistics
class Statistics (object):
  def __init__ (self, stat_urls, stat_queries, stat_referrers, stat_uagents):
    self.gauges = []            # [ GaugeIface ]
    self.visits = 0
    self.hits = 0
    self.url_quarks = stat_urls
    self.query_quarks = stat_queries
    self.referrer_quarks = stat_referrers
    self.uagent_quarks = stat_uagents
    self.last_hit_usecs = 0
    self.last_visits = {}       # (ip4addr, uagent) -> time_stamp_usec
    self.hour_stats = {}        # hourly_timestamp -> HourStat
    self.urls = {}              # string -> UrlString
    self.queries = {}           # string -> QueryString
    self.uagents = {}           # string -> UAgentString
    self.referrers = {}         # string -> ReferrerString
  def submit_url (self, string, tx_bytes, new_visit):
    url = self.urls.get (string)
    if not url:
      url = UrlString (string)
      self.urls[url.string] = url
    url.submit (tx_bytes, new_visit)
    return url
  def submit_query (self, string, tx_bytes, new_visit):
    query = self.queries.get (string)
    if not query:
      query = QueryString (string)
      self.queries[query.string] = query
    query.submit (tx_bytes, new_visit)
    return query
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
  def walk_qhits (self, hitlist):
    for qhit in hitlist:
      (time_stamp_usec, ip4addr, http_status, tx_bytes, url_quark, query_quark, referrer_quark, uagent_quark) = qhit
      assert time_stamp_usec >= self.last_hit_usecs # ensure ascending submissions
      self.last_hit_usecs = time_stamp_usec
      # determine new visits
      vkey = (ip4addr, uagent_quark)
      vlast = self.last_visits.get (vkey, None)
      new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
      self.last_visits[vkey] = time_stamp_usec
      self.visits += new_visit
      self.hits += 1
      # collect string stats
      url_string = self.submit_url (self.url_quarks[url_quark], tx_bytes, new_visit)
      query_string = self.submit_query (self.query_quarks[query_quark], tx_bytes, new_visit)
      referrer_string = self.submit_referrer (self.referrer_quarks[referrer_quark], tx_bytes, new_visit)
      uagent_string = self.submit_uagent (self.uagent_quarks[uagent_quark], tx_bytes, new_visit)
      hit = (time_stamp_usec, ip4addr, http_status, tx_bytes, url_string, query_string, referrer_string, uagent_string)
      # collect hourly stats
      time_hstamp = time_stamp_usec // 3600000000 * 3600 # timestamp in seconds, quantized to hours
      hstat = self.hour_stats.get (time_hstamp)
      if not hstat:
        hstat = HourStat (time_hstamp)
        self.hour_stats[hstat.timestamp] = hstat
      hstat.submit (hit, new_visit)
      # collect gauge stats
      for g in self.gauges:
        g.hit (hit, new_visit)
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
class UrlString (StringStat): pass
class QueryString (StringStat): pass
class UAgentString (StringStat): pass
class ReferrerString (StringStat): pass

# Hourly Statistics
class HourStat (object):
  __slots__ = ('timestamp', 'visits', 'urls', 'bytes')
  def __init__ (self, timestamp):
    self.timestamp = timestamp
    self.visits = 0
    self.urls = 0
    self.bytes = 0
    # (year, mon, mday, hour, Min, sec, wday, yday, isdst) = time.gmtime (time_stamp_usec / 1000000)
  def submit (self, hit, new_visit):
    tx_bytes = hit[3]
    self.urls += 1
    self.bytes += tx_bytes
    if new_visit:
      self.visits += 1

class GaugeIface (object):
  __slot__ = ('statistics',)
  def __init__ (self, statistics):
    self.statistics = statistics
  def hit (self, hit, new_visit):
    pass
  def done (self):
    pass
  def as_html (self, destdir):
    return []
