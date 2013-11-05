# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config, Statistics, collections
import HtmlStmt # tidy_html, with_tags for DIV, PRE, A, etc

class TopVisits (Statistics.GaugeIface):
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.NN = 50                                        # top NN
    self.entry_visits = collections.defaultdict (int)   # resource -> count
    self.entry_count = 0
    self.total_visits = 0
    self.entry_topNN = None
    self.hidden_visits = {}                             # visitid -> resource
  def hit (self, hit, visitid, new_visit):
    (ipaddr, time_stamp_usec, method, resource, query, protocol, http_status, tx_bytes, referrer, uagent) = hit
    if new_visit:
      self.entry_visits[resource] += 1                  # count one new visit to resource
      if self.statistics.hide_url (resource.string):
        self.hidden_visits[visitid] = resource
        assert resource.string.find ('robots.txt') < 0 # FIXME
    elif self.hidden_visits.has_key (visitid) and not self.statistics.hide_url (resource.string):
      oldres = self.hidden_visits[visitid]              # move a visit from hidden to visible
      self.entry_visits[oldres] -= 1                    # sub from hidden
      assert oldres.string.find ('robots.txt') < 0 # FIXME
      self.entry_visits[resource] += 1                  # add to the visible
      del self.hidden_visits[visitid]                   # a visit can only be moved once
  def done (self):
    self.total_visits = sum (self.entry_visits.values())
    ev = [item for item in self.entry_visits.items() if item[1]]
    self.entry_count = len (ev)
    hidden_set = set (self.hidden_visits.values())
    ev = [item for item in ev if not item[0] in hidden_set]
    ev = sorted (ev, key = lambda item: item[1], reverse = True)
    self.entry_topNN = ev[:self.NN]
  @HtmlStmt.with_tags
  def as_html (self, destdir):
    title = 'Top %u Entry Pages' % self.NN
    sub   = 'Page requests ordered by visits'
    totalp = 'Total number of entry pages: %u' % self.entry_count
    totalv = 'Total number of entry visits: %u' % self.total_visits
    rowlist, i = [], 0
    ftotal = self.total_visits / 100.0
    for tup in self.entry_topNN:
      resource, count = tup
      i += 1
      row = TR [
        TD (_class = 'rank')  [ '%u)' % i ],
        TD (_class = 'score') [ '%u'  % count ],
        TD (_class = 'perc')  [ '%.1f%%' % (count / ftotal) ],
        TD (_class = 'url')   [ resource.string ],
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
