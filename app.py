#!/usr/bin/python

import gtfs_realtime_pb2
from flask import Flask
from urllib import urlopen
import time
import os

# prod
api_ip = '83.145.232.209'

#test
# api_ip = '213.157.92.101'

live_api_url = 'http://' + api_ip + ':10001/?type=vehicles' + \
               '&lng1=23&lat1=60&lng2=26&lat2=61&online=1'

app = Flask(__name__)

@app.route('/', defaults={'line': '', 'dir': ''})
@app.route('/<line>/<int:dir>')
def index(line, dir):
  url = live_api_url
  if (line and dir):
    url += '&lines=' + line + '.' + str(dir)
  feed = urlopen(url)
  msg = gtfs_realtime_pb2.FeedMessage()
  msg.header.gtfs_realtime_version = "1.0"
  msg.header.incrementality = msg.header.FULL_DATASET
  msg.header.timestamp = int(time.time())
  
  cnt = 0
  for line in feed:
    row = line.strip().split(';')
    if (len(row) < 4):
      continue
    if ((row[2] == 0) or (row[3] == 0)):
      continue;
    ent = msg.entity.add()
    ent.id = str(cnt)
    ent.vehicle.trip.route_id = row[1]
    if (row[8]):
      ent.vehicle.trip.start_time = row[8][:2] + ':' + row[8][2:]
    ent.vehicle.trip.schedule_relationship = ent.vehicle.trip.SCHEDULED

    ent.vehicle.vehicle.id = row[0]
    ent.vehicle.vehicle.label = row[1]
    ent.vehicle.position.latitude = float(row[2])
    ent.vehicle.position.longitude = float(row[3])
    ent.vehicle.position.bearing = int(row[4])
    # speed not available in this message
    # if (len(row) >= 12):
    #   ent.vehicle.position.speed = float(row[12]/3.6)
    cnt += 1
  print(msg);
  return msg.SerializeToString()

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.debug = True
  app.run(host='0.0.0.0', port=port)
