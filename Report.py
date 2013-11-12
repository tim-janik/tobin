# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import datetime, Config
import HtmlStmt # tidy_html, with_tags for DIV, PRE, A, etc

def _report_title (statistics):
  return '%s - Usage Statistics %u' % (Config.sitename, statistics.stat_year)

@HtmlStmt.with_tags
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
      DIV (_class = 'tobin-footer') [
        'Created using ',
        A (href = Config.package_url, target = '_blank') [ Config.package_title ],
        ' %s.' % Config.package_version, ],
      COMMENT ['Generated on %s with %s' % (datetime.datetime.today(), Config.version_info())],
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
