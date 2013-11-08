# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
'''
This module provides helper functions for geographical mappings of IP addresses.

For convenience, pseudo country codes are provided for unknown addresses
('??', 'Unknown') and multiple undetermined countries ('..', 'Others').
'''
import GeoIP

_geoip = GeoIP.new (GeoIP.GEOIP_STANDARD)
_geoip.set_charset(GeoIP.GEOIP_CHARSET_UTF8);
_country_cache = {}
unknown_code, unknown_label = '??', 'Unknown'
others_code, others_label = '..', 'Others'

def lookup (ipaddr):
  '''Retrieve country code for an IP address (passed as string). Returns 2 letter country code.'''
  global _country_cache
  cc = _country_cache.get (ipaddr, False)
  if cc is False: # uncached
    cc = _geoip.country_code_by_addr (ipaddr)
    if not cc:
      cc = unknown_code # unknown
    if len (_country_cache) > 65536 * 4:
      _country_cache = {} # avoid excessive cache growth
    _country_cache[ipaddr] = cc
  return cc

def country (country_code):
  '''Retrieve country name for a 2 letter country code. '''
  if country_code == unknown_code:
    return unknown_label
  if country_code == others_code:
    return others_label
  return GeoIP.country_names.get (country_code)

def country_color (country_code):
  '''Provide a color for a 2 letter country code, useful for siple graphs.'''
  preset = { 'CN' : '#ff0040', 'US' : '#110eee', 'DE' : '#fcc404', 'FR' : '#00eeee', 'GB' : '#041e69',
             'ES' : '#009900', 'RU' : '#e00020', 'NL' : '#fba400', 'IN' : '#bb00bb', 'IT' : '#e1ddd1',
             'BE' : '#111111', 'JP' : '#1c75b1', unknown_code : '#dddddd', others_code : '#999999' }
  colors = [ '#F660AB', '#7D2252', '#E55451', '#F62217', '#7F5A58', '#C8B560', '#806517', # pink red brown
             '#C9BE62', '#F87217', '#FBB117', '#CCFB5D', '#87F717', '#99C68E', '#347C17', # orange yellow green
             '#348781', '#5E7D7E', '#6698FF', '#736AFF', '#307D7E', '#8EEBEC', '#52F3FF', # cyan blue
             '#C6AEC7', '#E6A9EC', '#B93B8F', '#7E354D', '#F778A1', '#A23BEC', '#7D1B7E', # purple violet
             '#C031C7', '#FF00FF', ]
  col = preset.get (country_code)
  return col if col else colors[hash (country_code) % len (colors)]

def country_colors (cclist):
  '''Provide colors for a list of country codes, see country_color().'''
  return [country_color (cc) for cc in cclist]
