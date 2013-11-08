# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import datetime, Config
from HtmlStmt import *  # HTML, HEAD, BODY, etc
import HtmlStmt         # for tidy_html

def _report_title (statistics):
  return '%s - Usage Statistics %u' % (Config.sitename, statistics.stat_year)

def _build_report_html (html_elements, statistics):
  simple_title = _report_title (statistics)
  return HTML [
    HEAD [
      # META (charset = 'UTF-8'), # HTML5
      META (http_equiv = 'Content-type', content = 'text/html; charset=UTF-8'), # HTML4
      TITLE [ simple_title ],
      LINK (href = 'standard.css', rel = 'stylesheet', type = 'text/css'),
      ],
    BODY [
      DIV (_class = 'outer-wrapper') [
        DIV (_class = 'main report') [
          H1 [ simple_title ],
          html_elements,
          ],
        ],
      COMMENT ['Tobin statistics generated on %s' % datetime.datetime.today()],
      ],
    ]

class LogReport:
  def __init__ (self, destdir, statistics):
    self.destdir = destdir
    self.statistics = statistics
  def generate_index (self, html_elements):
    fout = open (self.destdir + '/index.html', 'w')
    rawhtml = unicode (_build_report_html (html_elements, self.statistics))
    nice_html = HtmlStmt.tidy_html (rawhtml)
    fout.write (nice_html)
    fout.close()
  def generate_css (self):
    fout = open (self.destdir + '/standard.css', 'w')
    fcss = open (Config.package_data_file ('standard.css'))
    fout.write (fcss.read())
    fcss.close()
    fout.close()

def generate (destdir, statistics, html_elements = None):
  lr = LogReport (destdir, statistics)
  lr.generate_css()
  lr.generate_index (html_elements if html_elements else [])
