# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config, Statistics
from HtmlStmt import *  # DIV, PRE, A, etc

class TopVisits (Statistics.GaugeIface):
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.entry_visits = {}      # url -> nvisits
    self.entry_count = 0
    self.total_visits = 0
    self.entry_top20 = None
  def hit (self, hit, new_visit):
    (time_stamp_usec, ip4addr, http_status, tx_bytes, url, query, referrer, uagent) = hit
    if new_visit:
      self.entry_visits.setdefault (url, 0)
      self.entry_visits[url] += 1
  def done (self):
    ev = self.entry_visits.items()
    self.entry_count = len (ev)
    self.total_visits = sum ([tup[1] for tup in ev])
    ev = sorted (ev, key = lambda tup: tup[1], reverse = True)
    self.entry_top20 = ev[:20]
  def as_html (self, destdir):
    title = 'Top 20 Entry Pages'
    sub   = 'Page requests ordered by visits'
    totalp = 'Total number of entry pages: %u' % self.entry_count
    totalv = 'Total number of entry visits: %u' % self.total_visits
    rowlist, i = [], 0
    ftotal = self.total_visits / 100.0
    for tup in self.entry_top20:
      url, count = tup
      i += 1
      row = TR [
        TD (_class = 'rank')  [ '%u)' % i ],
        TD (_class = 'score') [ '%u'  % count ],
        TD (_class = 'perc')  [ '%.1f%%' % (count / ftotal) ],
        TD (_class = 'url')   [ url.string ],
        ]
      rowlist += [ row ]
    fig = TABLE (summary = title, _class = 'gauge topx entry-pages', cellspacing = '0') [
      TR (_class = 'title')    [ TH (colspan = '4') [ title ], ],
      TR (_class = 'subtitle') [ TH (colspan = '4') [ sub ], ],
      TR (_class = 'info')     [ TD (colspan = '4') [ totalp ], ],
      TR (_class = 'info')     [ TD (colspan = '4') [ totalv ], ],
      rowlist,
      ]
    return DIV (_class = 'top-entry-visits') [
      A (name = 'top-entry-pages'),
      fig
      ]
