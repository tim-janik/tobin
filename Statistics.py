# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config

# General Statistics
class Statistics (object):
  def __init__ (self):
    self.gauges = []            # [ GaugeIface ]
    self.visits = 0
    self.hits = 0
    self.last_hit_usecs = 0
    self.last_visits = {}       # (ip4addr, uagent) -> time_stamp_usec
    self.hour_stats = {}        # hourly_timestamp -> HourStat
    self.methods = {}           # string -> MethodString
    self.resources = {}         # string -> ResourceString
    self.queries = {}           # string -> QueryString
    self.protocols = {}         # string -> ProtocolString
    self.uagents = {}           # string -> UAgentString
    self.referrers = {}         # string -> ReferrerString
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
      assert time_stamp_usec >= self.last_hit_usecs # ensure ascending submissions
      self.last_hit_usecs = time_stamp_usec
      # determine new visits
      vkey = (ipaddr, uagent)
      vlast = self.last_visits.get (vkey, None)
      new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
      self.last_visits[vkey] = time_stamp_usec
      self.visits += new_visit
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
class MethodString (StringStat): pass
class ResourceString (StringStat): pass
class QueryString (StringStat): pass
class ProtocolString (StringStat): pass
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
    tx_bytes = hit[7]
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
