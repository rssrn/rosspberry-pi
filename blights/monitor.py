# monitor some specific things and generate json
# the json will later be read by blights.py
from beeprint import pp
# use pp(var) to print complex variables

#     pip install weather-api
from weather import Weather, Unit

import json
import logging
import csv
import time

logging.basicConfig(format='%(asctime)s %(message)s',level='INFO')

#owm = pyowm.OWM(os.environ['APIKEY_OWM'])
#w_current = owm.weather_at_place('Richmond,GB')
#print(w_current.get_wind())

def makeAlert(position,color, blink):
    res = {}
    res['position'] = position
    res['type'] = 'INDIVIDUAL'
    res['spec'] = {'color': color}
    if blink:
        res['spec']['blink'] = {'on': 1000, 'off': 1000}
    return res

def alertForTemperature(temp):
    blink = False
    color = 'magenta'

    logging.info("Current Temperature:" + str(temp))
    if (temp < 0):
        color = 'blue'
        blink = True
    elif (temp < 12):
        color = 'blue'
    elif (temp < 24):
        color = 'green'
    elif (temp < 30):
        color = 'orange'
    elif (temp < 35):
        color = 'red'
    else:
        color = 'red'
        blink = True

    return color,blink
        
def alertForCondition(code):
    color = 'magenta'
    blink = False
    
    csv_file = csv.reader(open('conditions.csv', "rb"), delimiter=",")
    for row in csv_file:
        if code == row[0]:
            color = row[2]
            if 3 in row and row[3] == 'blink':
                blink = True
            break
        
    return color,blink


output = {}

output['intensity'] = 10
output['alerts'] = []


####################################################
#
#  Light 1: Current Temperature
#
####################################################
weather = Weather(unit=Unit.CELSIUS)
lookup = weather.lookup(91731252) # code for Chiswick

color, blink = alertForTemperature(int(lookup.condition.temp))
output['alerts'].append(makeAlert(1, color, blink))


####################################################
#
#  Light 2: Current Conditions
#
####################################################

# depends on previous call to yahoo weather api
condition = lookup.condition
color, blink = alertForCondition(lookup.condition.code)
output['alerts'].append(makeAlert(2, color, blink))


####################################################
#
#  Light 3: Forecast temp
#
####################################################

# assuming before 5pm we want today's forecast; after 5pm tomorrow's
current_hour = int(time.strftime('%H'))
if current_hour < 17:
    fc_idx = 0
else:
    fc_idx = 1

high = lookup.forecast[fc_idx].high
color, blink = alertForTemperature(int(high))
output['alerts'].append(makeAlert(3, color, blink))

####################################################
#
#  Light 4: Forecast condition
#
####################################################
code = lookup.forecast[fc_idx].code
color, blink = alertForCondition(code)
output['alerts'].append(makeAlert(4, color, blink))

####################################################
#
#  Light 5: Tube / Overground status
#
####################################################
# https://api.tfl.gov.uk/Journey/JourneyResults/1000125/to/1000094
# Kew Gardens To Gunnersbury

print json.dumps(output, indent=4, sort_keys=True)

#pp(lookup)
