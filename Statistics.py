# Licensed GNU Affero GPL v3 or later: http://www.gnu.org/licenses/agpl.html
import Config

class Statistics:
  def __init__ (self):
    self.visits = 0
    self.hits = 0
  def walk_hits (self, hitlist):
    last_hit_usecs, vdict = 0, {}
    for hit in hitlist:
      time_stamp_usec, ip4addr, uagent_quark = hit[0], hit[1], hit[7]
      assert time_stamp_usec >= last_hit_usecs # check ascending submissions
      # determine new visits
      vkey = (ip4addr, uagent_quark)
      vlast = vdict.get (vkey, None)
      new_visit = vlast == None or time_stamp_usec - vlast > Config.visit_timeout_usec
      vdict[vkey] = time_stamp_usec
      self.visits += new_visit
      self.hits += 1
