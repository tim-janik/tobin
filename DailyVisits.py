# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config, Statistics, time, calendar
import matplotlib.pyplot as plt
import numpy as NP
from HtmlStmt import *  # DIV, PRE, A, etc

class DailyVisits (Statistics.GaugeIface):
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.daily_visits = None
  def daily_stats (self):
    count, vsum, ma, mi = 0, 0, 0, self.daily_visits[0]
    for vv in self.daily_visits:
      if vv:
        count += 1
        vsum += vv
        ma = max (ma, vv)
        mi = min (mi, vv)
    return (count, vsum, ma, mi)
  def done (self):
    stat_year, year_days = self.statistics.stat_year, self.statistics.year_days
    self.daily_visits = NP.zeros (year_days)
    for hstat in self.statistics.hour_stats.values():
      self.daily_visits[hstat.yday - 1] += hstat.visits # daily_visits uses 0-indexing
  def create_svg (self, destdir):
    year_days, month_lengths = self.statistics.year_days, self.statistics.month_lengths
    x = NP.linspace (0, year_days - 1, num = year_days)
    y = self.daily_visits
    fig = plt.figure ()
    # print fig, fig.get_size_inches(), fig.get_dpi() # Figure(640x480), [ 8.  6.], 80
    fig_size = (1024, 512)      # desired figure size as width, height
    fig_dpi = fig.get_dpi()
    fig.set_size_inches (fig_size[0] / fig_dpi, fig_size[1] / fig_dpi)
    colors = ('#0000ff', '#1111ff', '#2222ff', '#3333ff', '#4444ff', '#7777ff', '#9999ff')
    for i in range (self.statistics.first_day): # rotate colors left if the year didn't start on Monday
      colors = colors[1:] + colors[:1]
    plt.bar (x, y, width = 1, align = 'center', linewidth = 0.1, alpha = 0.5, color = colors)
    #plt.xticks (NP.arange (year_days + 1))
    mdays = [sum (month_lengths[:i]) for i in range (12)] # cumulative days
    plt.xticks (mdays, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation = 45)
    plt.xlim ([-1.5, year_days + .5])
    svgname = 'DailyVisits.svg'
    plt.savefig (destdir + '/' + svgname, transparent = True, bbox_inches = 'tight', pad_inches = 0.1)
    return svgname
  def as_html (self, destdir):
    stat_year = self.statistics.stat_year
    (count, vsum, ma, mi) = self.daily_stats()
    avg = int (vsum / max (1, count) + 0.5)
    title   = 'Daily Visits'
    sub     = 'Annual daily visits %u' % stat_year
    totalv  = 'Total number of visits: %u' % vsum
    dayavg  = 'Daily visits min, avg, max: %u, %u, %u' % (mi, avg, ma)
    svgname = self.create_svg (destdir)
    fig = TABLE (summary = title, _class = 'gauge graphxy daily-visits', cellspacing = '0') [
      TR (_class = 'title')    [ TH (colspan = '1') [ title ], ],
      TR (_class = 'subtitle') [ TH (colspan = '1') [ sub ], ],
      TR (_class = 'info')     [ TD (colspan = '1') [ totalv ], ],
      TR (_class = 'info')     [ TD (colspan = '1') [ dayavg ], ],
      TR [ TD [ IMG (_class = 'widegraph', src = svgname) ], ],
      ]
    return DIV (_class = 'daily-visits') [
      A (name = 'daily-visits'),
      fig
      ]
