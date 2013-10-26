# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config

class Statistics (object):
  def __init__ (self, stat_urls, stat_queries, stat_referrers, stat_uagents):
    self.gauges = []    # [ GaugeIface ]
    self.visits = 0
    self.hits = 0
    self.urls = stat_urls
    self.queries = stat_queries
    self.referrers = stat_referrers
    self.uagents = stat_uagents
  def walk_hits (self, hitlist):
    last_hit_usecs, vdict = 0, {}
    for hit in hitlist:
      time_stamp_usec, ip4addr, uagent_quark = hit[0], hit[1], hit[7]
      assert time_stamp_usec >= last_hit_usecs # check ascending submissions
      # determine new visits
      vkey = (ip4addr, uagent_quark)
      vlast = vdict.get (vkey, None)
      new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
      vdict[vkey] = time_stamp_usec
      self.visits += new_visit
      self.hits += 1
      for g in self.gauges:
        g.hit (hit, new_visit)
  def done (self):
    for g in self.gauges:
      g.done()
  def as_html (self):
    elements = []
    for g in self.gauges:
      htm = g.as_html()
      if hasattr (htm, '__iter__'):
        elements.extend (htm)
      else:
        elements += [ htm ]
    return elements

class GaugeIface (object):
  __slot__ = ('statistics',)
  def __init__ (self, statistics):
    self.statistics = statistics
  def hit (self, hit, new_visit):
    pass
  def done (self):
    pass
  def as_html (self):
    return []
  def url (self, quark):
    return self.statistics.urls[quark]
  def query (self, quark):
    return self.statistics.queries[quark]
  def referrer (self, quark):
    return self.statistics.referrers[quark]
  def uagent (self, quark):
    return self.statistics.uagents[quark]
