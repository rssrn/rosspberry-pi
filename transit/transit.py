import logging
logging.basicConfig(format='%(asctime)s %(message)s',level='INFO')

from beeprint import pp
import googlemaps
from datetime import datetime
import time
import os
import re
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

mapkey = os.environ['MAPS_API_KEY']
gmaps = googlemaps.Client(key=mapkey)

dirs = gmaps.directions("TW9 2AL",
                        "Gunnersbury Station",
                        mode="transit",
                        transit_mode="bus",
                        departure_time=datetime.now())

duration = dirs[0]['legs'][0]['duration']['value']

# useful to get total elapsed time i.e. including waiting time
arr_time = dirs[0]['legs'][0]['arrival_time']['value']
elapsed = arr_time - int(time.time())

mode = None
try:
    for step in dirs[0]['legs'][0]['steps']:
        if 'Subway' in step['html_instructions']:
            mode = 0
            break
        elif 'Commuter train' in step['html_instructions']:
            mode = 1
            break
        elif 'Bus' in step['html_instructions']:
            mode = 2
            break
    if mode is None:
        print('unknown mode, not tube/train/bus:')
        for step in dirs[0]['legs'][0]['steps']:
            print(step['html_instructions'])
        mode = 3
except KeyError:
    logging.error("error parsing html_instructions")
    mode = 4

r = CollectorRegistry()
d = Gauge('transit_kew_duration_minutes', \
          'Duration of typical commute from Kew to Gunnersbury', \
          registry = r)
d.set(duration/60)

e = Gauge('transit_kew_elapsed_minutes', \
          'Elapsed time (including waiting time) of typical commute from Kew to Gunnersbury', \
          registry = r)
e.set(elapsed/60)

m = Gauge('transit_kew_fastestmode', \
          'Fastest mode of typical commute from Kew to Gunnersbury', \
          registry = r)
m.set(mode)
push_to_gateway('localhost:9091', job='transit', registry=r)

# metrics we want to end up with
# 1) total travel time (gauge)
# 2) best mode (0=tube,1=bus,2=walk)
#
# if best mode stays at 1 for a long time we can alert, etc
