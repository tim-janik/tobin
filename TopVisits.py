# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config, Statistics
from HtmlStmt import *  # DIV, PRE, A, etc

class TopVisits (Statistics.GaugeIface):
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.entry_visits = {}
    self.entry_count = 0
    self.entry_top20 = None
  def hit (self, hit, new_visit):
    (time_stamp_usec, ip4addr, http_status, tx_bytes, url_quark, query_quark, referrer_quark, uagent_quark) = hit
    if new_visit:
      self.entry_visits.setdefault (url_quark, 0)
      self.entry_visits[url_quark] += 1
  def done (self):
    ev = self.entry_visits.items()
    self.entry_count = len (ev)
    ev = sorted (ev, key = lambda tup: tup[1], reverse = True)
    self.entry_top20 = ev[:20]
  def as_html (self):
    title = 'Top 20 Entry Pages'
    sub   = 'Page requests ordered by visits'
    total = 'Total number of pages: %u' % self.entry_count
    rowlist, i = [], 0
    for u in self.entry_top20:
      i += 1
      row = TR [
        TD (_class = 'rank')  [ '%u)' % i ],
        TD (_class = 'score') [ '%u'  % u[1] ],
        TD (_class = 'url')   [ self.url (u[0]) ],
        ]
      rowlist += [ row ]
    fig = TABLE (summary = title, _class = 'topx entry-pages', cellspacing = '0') [
      TR (_class = 'title')    [ TH (colspan = '3') [ title ], ],
      TR (_class = 'subtitle') [ TH (colspan = '3') [ sub ], ],
      TR (_class = 'info')     [ TD (colspan = '3') [ total ], ],
      rowlist,
      ]
    return DIV (_class = 'top-entry-visits') [
      A (name = 'top-pages'),
      fig
      ]
