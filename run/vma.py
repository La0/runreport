from collections import namedtuple
import time
import datetime

Pace = namedtuple('Pace', ['name', 'percent'])

class VmaCalc:
  _vma = 0.0
  _paces = [
    Pace('L', 50),
    Pace('1', 60),
    Pace('2', 70),
    Pace('EMA 1', 80),
    Pace('EMA 2', 85),
    Pace('EMA 3', 90),
    Pace('VMA L', 95),
    Pace('VMA C', 100),
    Pace('VMA C', 105),
  ]

  _distances = [100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 10000]

  def __init__(self, vma):
    self._vma = vma

  def get_paces(self):
    return self._paces

  def get_distances(self):
    return self._distances

  def get_speed(self, pace):
    '''
    Get the speed in km/h at a pace
    '''
    return self._vma * pace.percent / 100.0

  def get_time(self, pace, distance):
    '''
    Get the time object needed to run a distance at a pace
    '''
    t = time.localtime((distance * 3600) / (self.get_speed(pace) * 1000))
    return datetime.time(t.tm_hour-1, t.tm_min, t.tm_sec)
