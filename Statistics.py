# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config

# General Statistics
class Statistics (object):
  def __init__ (self, stat_urls, stat_queries, stat_referrers, stat_uagents):
    self.gauges = []            # [ GaugeIface ]
    self.visits = 0
    self.hits = 0
    self.urls = stat_urls
    self.queries = stat_queries
    self.referrers = stat_referrers
    self.uagents = stat_uagents
    self.last_hit_usecs = 0
    self.last_visits = {}       # (ip4addr, uagent) -> time_stamp_usec
    self.hour_stats = {}        # hourly_timestamp -> HourStat
  def walk_hits (self, hitlist):
    for hit in hitlist:
      time_stamp_usec, ip4addr, uagent_quark = hit[0], hit[1], hit[7]
      assert time_stamp_usec >= self.last_hit_usecs # ensure ascending submissions
      self.last_hit_usecs = time_stamp_usec
      # determine new visits
      vkey = (ip4addr, uagent_quark)
      vlast = self.last_visits.get (vkey, None)
      new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
      self.last_visits[vkey] = time_stamp_usec
      self.visits += new_visit
      self.hits += 1
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

# Hourly Statistics
class HourStat (object):
  def __init__ (self, timestamp):
    self.timestamp = timestamp
    self.visits = 0
    self.urls = 0
    self.bytes = 0
    # (year, mon, mday, hour, Min, sec, wday, yday, isdst) = time.gmtime (time_stamp_usec / 1000000)
  def submit (self, hit, new_visit):
    (time_stamp_usec, ip4addr, http_status, tx_bytes, url_quark, query_quark, referrer_quark, uagent_quark) = hit
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
  def url (self, quark):
    return self.statistics.urls[quark]
  def query (self, quark):
    return self.statistics.queries[quark]
  def referrer (self, quark):
    return self.statistics.referrers[quark]
  def uagent (self, quark):
    return self.statistics.uagents[quark]
