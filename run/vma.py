from collections import namedtuple
import time
import datetime

Pace = namedtuple('Pace', ['name', 'percent'])

class VmaCalc:
  _vma = 0.0
  _paces = [
    Pace('Footing Lent', 50),
    Pace('Footing 1', 60),
    Pace('Footing 2', 70),
    Pace('EMA 1', 80),
    Pace('EMA 2', 85),
    Pace('EMA 3', 90),
    Pace('VMA L', 95),
    Pace('VMA C', 100),
  ]

  def __init__(self, vma):
    self._vma = vma

  def get_paces(self):
    return self._paces

  def get_speeds(self, distances=(1000, 100)):
    out = {}
    for pace in self._paces:
      speed = self._vma * pace.percent / 100.0 
      pace_data = {
        'speed' : speed,
      }
      for dist in distances:
        t = time.localtime((dist * 3600) / (speed * 1000))
        pace_data[dist] = datetime.time(t.tm_hour, t.tm_min, t.tm_sec)
      out[pace] = pace_data

    return out

