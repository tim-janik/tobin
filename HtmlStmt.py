# Licensed under the MIT License: http://opensource.org/licenses/MIT
# This module was heavily inspired by throw_out_your_templates.py and Breve

class Tag (object):
  after_head = ''
  after_tail = ''
  isempty    = False
  __slots__ = ('name', 'attrs', 'children')
  def __init__ (self, name):
    self.name = name
    self.attrs = {}
    self.children = []
  def __getitem__ (self, children):
    assert len (self.children) == 0
    if hasattr (children, '__iter__'):
      self.children.extend (children)
    else:
      self.children += [ children ]
    return self
  def __call__ (self, **kw):
    assert len (self.attrs) == 0
    attributes = [(k.strip (u'_').replace (u'_', u'-'), v) for k,v in kw.items ()]
    self.attrs.update (dict (attributes))
    return self
  @staticmethod
  def escape (txt, equot = True):
    for c,sub in (('&', '&amp;'),
                  ('<', '&lt;'),
                  ('>', '&gt;')):
      txt = txt.replace (c, sub)
    if equot:
      txt = txt.replace ('"', '&quot;')
    return txt
  def _str_tag (self, prefix, qattrs = '', postfix = ''):
    if qattrs:
      qattrs = ' ' + qattrs.strip()
    aftertag = self.after_tail if prefix.find ('/') >= 0 or postfix.find ('/') >= 0 else self.after_head
    return u'<%s%s%s%s>%s' % (prefix, self.name, qattrs, postfix, aftertag)
  def _str_attributes (self, attrs):
    qattrs = []
    for k,v in attrs.items():
      if not v is None:
        if not isinstance (v, unicode):
          v = unicode (v, 'UTF-8')
        qattrs += [ u' %s="%s"' % (k, self.escape (v)) ]
    return u''.join (qattrs)
  def _strings (self):
    qattrs = self._str_attributes (self.attrs)
    if self.isempty and not self.children:
      yield self._str_tag ('', qattrs, '/')
      raise StopIteration
    else:
      yield self._str_tag ('', qattrs, '')
    def _strings_iter (elist):
      for element in elist:
        if isinstance (element, basestring):
          yield self.escape (element, False)
        elif isinstance (element, (tuple, list)):
          for string in _strings_iter (element):
            yield string
        else:
          for string in element._strings():
            yield string
    for string in _strings_iter (self.children):
      yield string
    yield self._str_tag ('/', '', '')
  def __str__ (self):
    return ''.join (self._strings())

class BlockTag (Tag):
  after_tail = '\n'
  __slots__ = ()
class OuterTag (BlockTag):
  after_head = '\n'
  __slots__ = ()
class EmptyTag (Tag):
  isempty = True
  __slots__ = ()
class LineTag (EmptyTag):
  after_tail = '\n'
  __slots__ = ()
class CommentTag (Tag):
  __slots__ = ()
  def __call__ (self, **kw):
    raise TypeError ('%s: no attributes permitted' % self.__class__.__name__)
  def _strings (self):
    yield u'<!-- %s -->\n' % u' '.join (self.escape (c, False) for c in self.children)

class ProtoTag (object):
  __slots__ = ('klass', 'name')
  def __init__ (self, klass, name):
    self.klass = klass
    self.name = unicode (name)
  def __call__ (self, **kw):
    return self.klass (self.name) (**kw)
  def __getitem__ (self, children):
    return self.klass (self.name) [children]
  def _strings (self):
    return self.klass (self.name)._strings()
  def __str__ (self):
    return ''.join (self._strings())

def make_html_tags():
  outer_tags  = '''BODY HEAD HTML TITLE'''
  block_tags  = '''ADDRESS ARTICLE ASIDE AUDIO BLOCKQUOTE CANVAS DD DIV DL DT FIELDSET FIGCAPTION FIGURE FOOTER FORM
                   H1 H2 H3 H4 H5 H6 HEADER HGROUP NOSCRIPT OL OUTPUT P PRE SECTION TABLE TFOOT UL VIDEO'''
  normal_tags = '''CAPTION COLGROUP DATALIST DEL DETAILS IFRAME INS LEGEND LI MARK MENU METER NAV OPTGROUP OPTION
                   PROGRESS RP RT RUBY S STYLE SUMMARY TBODY TD TH THEAD TIME TR U
                   ACRONYM APPLET BIG CENTER FONT FRAMESET NOBR NOFRAMES STRIKE''' # deprecated
  inline_tags = '''A ABBR ACRONYM B BDI BDO BIG BR BUTTON CITE CODE DFN EM I KBD LABEL MAP
                   OBJECT Q SAMP SCRIPT SELECT SMALL SPAN STRONG SUB SUP TEXTAREA VAR
                   TT''' # deprecated
  empty_tags  = '''AREA BASE COL COMMAND EMBED IMG INPUT KEYGEN LINK META PARAM SOURCE TRACK WBR
                   BASEFONT ISINDEX FRAME''' # deprecated
  line_tags   = '''BR HR'''
  tags        = { 'COMMENT' : ProtoTag (CommentTag, 'COMMENT') }
  for tagname in outer_tags.split():
    tags[tagname] = ProtoTag (OuterTag, tagname)
  for tagname in block_tags.split() + normal_tags.split():
    tags[tagname] = ProtoTag (BlockTag, tagname)
  for tagname in inline_tags.split():
    tags[tagname] = ProtoTag (Tag, tagname)
  for tagname in empty_tags.split():
    tags[tagname] = ProtoTag (EmptyTag, tagname)
  for tagname in line_tags.split():
    tags[tagname] = ProtoTag (LineTag, tagname)
  return tags

tag_statements = make_html_tags()
del make_html_tags
locals().update (tag_statements)
__all__ = tag_statements.keys()
del tag_statements

def tidy_html (text):
  from tidylib import tidy_document
  opts = { 'output-xhtml' : 0, 'uppercase-tags' : 1, }
  docheader = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">\n'
  document, errors = tidy_document (docheader + unicode (text), options = opts)
  if errors:
    import sys
    print >>sys.stderr, errors
  return unicode (document)

# Test Examples
if __name__ == '__main__':
  doc = HTML [
    HEAD [
      TITLE [ 'A HtmlStmt Examples' ],
      COMMENT [ '...oooOOOooo...' ],
      ],
    BODY [
      H1 (_class = 'header') [ 'Brief Header' ],
      BR (_class = 'break'),
      DIV (style = 'text-align: center', _class = 'frob') [
        SPAN (_class = 'myspan') [ '''
            The HTML tag statments support attributes and map
            closely to the structure of the generated HTML.
            ''' ]
        ],
      BR,
      'Preformatted example text:',
      PRE [ '''This is preformatted & quoted
        text
          for
        you.''' ]
      ]
    ]
  def bs_prettyify (string):
    import BeautifulSoup
    soup = BeautifulSoup.BeautifulSoup (output)
    return soup.prettify() # BeautifulSoup adds buggy whitespaces inside <pre>
  print tidy_html (unicode (doc)),
