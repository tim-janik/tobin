# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config, Statistics
from HtmlStmt import *  # DIV, PRE, A, etc

class TopVisits (Statistics.GaugeIface):
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.entry_visits = {}
    self.entry_top20 = None
  def hit (self, hit, new_visit):
    (time_stamp_usec, ip4addr, http_status, tx_bytes, url_quark, query_quark, referrer_quark, uagent_quark) = hit
    if new_visit:
      self.entry_visits.setdefault (url_quark, 0)
      self.entry_visits[url_quark] += 1
  def done (self):
    ev = self.entry_visits.items()
    ev = sorted (ev, key = lambda tup: tup[1], reverse = True)
    self.entry_top20 = ev[:20]
  def as_html (self):
    elist = []
    for u in self.entry_top20:
      elist += [ B ['%7u)' % u[1]], TT [ self.url (u[0]) ], BR, ]
    return DIV (_class = 'top-entry-visits') [ elist ]
