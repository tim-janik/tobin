# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import datetime, Config
from HtmlStmt import *  # HTML, HEAD, BODY, etc
import HtmlStmt         # for tidy_html

simple_title = '%s - Usage Statistics' % Config.sitename

report_index = HTML [
  HEAD [
    TITLE [ simple_title ],
    LINK (href = 'standard.css', rel = 'stylesheet', type = 'text/css'),
    ],
  BODY [
    COMMENT ['Tobin statistics generated on %s' % datetime.datetime.today()],
    DIV (_class = 'outer-wrapper') [
      DIV (_class = 'main report') [
        H1 [ simple_title ],
        ],
      ],
    ],
  ]

class LogReport:
  def __init__ (self, destdir):
    self.destdir = destdir
  def generate_index (self):
    fout = open (self.destdir + '/index.html', 'w')
    rawhtml = unicode (report_index)
    nice_html = HtmlStmt.tidy_html (rawhtml)
    fout.write (nice_html)
    fout.close()
  def generate_css (self):
    fout = open (self.destdir + '/standard.css', 'w')
    fcss = open (Config.package_data_file ('standard.css'))
    fout.write (fcss.read())
    fcss.close()
    fout.close()

def generate (destdir):
  lr = LogReport (destdir)
  lr.generate_index()
  lr.generate_css()
