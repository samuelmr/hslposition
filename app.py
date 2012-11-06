#!/usr/bin/python

import gtfs_realtime_pb2
from flask import Flask
from urllib import urlopen
import time
import os

live_api_url = 'http://83.145.232.209:10001/?type=vehicles' + \
               '&lng1=23&lat1=60&lng2=26&lat2=61&online=1'
gtfs_version = '20120224'
weekdays = ['Su', 'Ma', 'Ti', 'Ke', 'To', 'Pe', 'La', 'Su']
weekdays[-1] = 'Su';
lt = time.localtime()
wd = weekdays[lt[6]+1]
yd = weekdays[lt[6]]

app = Flask(__name__)

@app.route('/', defaults={'line': '', 'dir': ''})
@app.route('/<line>/<int:dir>')
def index(line, dir):
  url = live_api_url
  if (line and dir):
    url += '&lines=' + line + '.' + str(dir)
  print url
  feed = urlopen(url)
  msg = gtfs_realtime_pb2.FeedMessage()
  msg.header.gtfs_realtime_version = "1.0"
  msg.header.incrementality = msg.header.FULL_DATASET
  msg.header.timestamp = int(time.time())
  
  cnt = 0
  for line in feed:
    # print line
    row = line.strip().split(';')
    if (len(row) < 4):
      print line
      continue
    if ((row[2] == 0) or (row[3] == 0)):
      continue;
    # print row
    ent = msg.entity.add()
    ent.id = str(cnt)
    day = wd
    if ((row[8] > 1800) and (lt[3] < 6)):
      # trip start time in the evening but current date early in the morning,
      # assuming yesterday's trip
      day = yd
    trip = row[1] + '_' + gtfs_version + '_' + day + '_' + str(row[5]) + \
           '_' + row[8]
    ent.vehicle.trip.trip_id = trip
    ent.vehicle.trip.schedule_relationship = ent.vehicle.trip.SCHEDULED

    ent.vehicle.vehicle.id = row[0]
    ent.vehicle.vehicle.label = row[1]
    ent.vehicle.position.latitude = float(row[2])
    ent.vehicle.position.longitude = float(row[2])
    ent.vehicle.position.bearing = int(row[4])

  # print(msg);
  return msg.SerializeToString()

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.debug = True
  app.run(host='0.0.0.0', port=port)
