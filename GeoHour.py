# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
'''Statistics module to produce Visits-Per-Hour graphs.'''
import collections, time, calendar, Config, Statistics, GeoInfo
import matplotlib.pyplot as plt
import numpy as NP
import HtmlStmt # tidy_html, with_tags for DIV, PRE, A, etc

class GeoHour (Statistics.GaugeIface):
  '''Provide a graph for the distribution of country visits per hour.'''
  def __init__ (self, statistics):
    super (self.__class__, self).__init__ (statistics)
    self.hour_countries = [collections.defaultdict (int) for i in range (24)] # 24 * { country_code -> visits }
    self.total_countries = collections.defaultdict (int) # { country_code -> visits }
    self.ydays_counted = set()
  def done (self):
    for hstat in self.statistics.hour_stats.values():
      self.ydays_counted.add (hstat.yday)
      country_visits = self.hour_countries[hstat.hour]
      for cc, visits in hstat.countries.items():
        country_visits[cc] += visits
        self.total_countries[cc] += visits
  def color_legend (self, colors, labels):
    '''Create a matplotlib legend for a given set of colors and labels.'''
    while len (colors) < len (labels):
      colors = colors + colors
    colors = colors[:len (labels)]
    if False:   # Reverse
      colors.reverse()
      labels.reverse()
    proxies = []
    for c in colors:
      proxies += [ plt.Rectangle ((0, 0), 0, 0, fc = c) ] # proxy artist
    plt.legend (proxies, labels, ncol = 3, loc = 'upper center')
  def create_svg (self, destdir):
    # extract countries with the most visits
    country_codes = self.total_countries.items()
    country_codes.sort (reverse = True, key = lambda cv: cv[1]) # sort by visits
    country_codes = [cv[0] for cv in country_codes]             # extract country names
    NS = min (15, len (country_codes))                          # number of streams
    country_codes = country_codes[:NS-1]                        # constrain to top X
    # list country names
    country_names = [GeoInfo.country (cc) for cc in country_codes]
    country_codes = country_codes + [ GeoInfo.others_code ]     # to accumulate long tail
    country_names = country_names + [ GeoInfo.others_label ]
    others_index = country_codes.index (GeoInfo.others_code)
    # construct stream matrix, accumulate long tail in 'Others'
    dd = NP.zeros ((24 + 1, NS))
    country_index = {}
    for i in range (NS):
      country_index[country_codes[i]] = i
    for hour in range (24):
      country_visits = self.hour_countries[hour]
      for cv in country_visits.items():                         # (country_code, visits)
        index = country_index.get (cv[0], others_index)         # fallback to 'Others' bucket
        dd[hour][index] += cv[1]
    total_visits = sum (sum (dd))
    dd[24] = dd[0]                                              # hour 0 == 24
    if self.ydays_counted:
      dd[:,:] /= len (self.ydays_counted)                       # average stats
    # figure plotting
    fig = plt.figure()
    fig_size = (1024, 512)                      # desired figure size as width, height
    fig.set_size_inches (fig_size[0] / fig.get_dpi(), fig_size[1] / fig.get_dpi())
    colors = GeoInfo.country_colors (country_codes)
    if self.ydays_counted:
      sp = plt.stackplot (range (25), dd.T, colors = colors)
      self.color_legend (colors, country_names)
      plt.xticks (range (25))
      plt.ylim ([0, dd.sum (1).max() / 0.6])                    # space for legend
    plt.xlim ([0, 24])
    svgname = 'GeoHour.svg'
    plt.savefig (destdir + '/' + svgname, transparent = True, bbox_inches = 'tight', pad_inches = 0.1)
    return (svgname, total_visits)
  @HtmlStmt.with_tags
  def as_html (self, destdir):
    stat_year = self.statistics.stat_year
    title   = 'Visits per Hour'
    sub     = 'Geographical distribution of hourly visits in %u' % stat_year
    svgname, total_visits = self.create_svg (destdir)
    totalv  = 'Total number of visits: %u' % total_visits
    fig = TABLE (summary = title, _class = 'gauge graphxy hourly-geovisits', cellspacing = '0') [
      TR (_class = 'title')    [ TH (colspan = '1') [ title ], ],
      TR (_class = 'subtitle') [ TH (colspan = '1') [ sub ], ],
      TR (_class = 'info')     [ TD (colspan = '1') [ totalv ], ],
      TR [ TD [ IMG (_class = 'widegraph', src = svgname) ], ],
      ]
    return DIV (_class = 'hourly-geovisits') [
      A (name = 'hourly-geovisits'),
      fig
      ]
