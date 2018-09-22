import logging
logging.basicConfig(format='%(asctime)s %(message)s',level='INFO')

# monitor some specific things and generate json
# the json will later be read by blights.py
from beeprint import pp
# use pp(var) to print complex variables

#     pip install weather-api
from weather import Weather, Unit

import json
import csv
import time



#owm = pyowm.OWM(os.environ['APIKEY_OWM'])
#w_current = owm.weather_at_place('Richmond,GB')
#print(w_current.get_wind())

def makeAlert(position, reason, color, blink):
    res = {}
    res['position'] = position
    res['reason'] = reason
    res['type'] = 'INDIVIDUAL'
    res['spec'] = {'color': color}
    if blink:
        res['spec']['blink'] = {'on': 1000, 'off': 1000}
    return res

def alertForTemperature(temp):
    blink = False

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

output['intensity'] = 25
output['alerts'] = []


####################################################
#
#  Light 0: Current Temperature
#
####################################################
weather = Weather(unit=Unit.CELSIUS)
lookup = weather.lookup(91731252) # code for Chiswick
reason = "Currently " + lookup.condition.temp + "&deg;"
color, blink = alertForTemperature(int(lookup.condition.temp))
output['alerts'].append(makeAlert(0, reason, color, blink))


####################################################
#
#  Light 1: Current Conditions
#
####################################################

# depends on previous call to yahoo weather api
condition = lookup.condition
reason = "Currently " + lookup.condition.text
color, blink = alertForCondition(lookup.condition.code)
output['alerts'].append(makeAlert(1, reason, color, blink))


####################################################
#
#  Light 2: Forecast temp
#
####################################################

# assuming before 5pm we want today's forecast; after 5pm tomorrow's
current_hour = int(time.strftime('%H'))
if current_hour < 17:
    fc_idx = 0
    day = 'today'
else:
    fc_idx = 1
    day = 'tomorrow'

high = lookup.forecast[fc_idx].high
reason = "Forecast high (" + day + "): " + \
         lookup.forecast[fc_idx].high + "&deg;" + \
         " (low " + lookup.forecast[fc_idx].low + "&deg;)" 
color, blink = alertForTemperature(int(high))
output['alerts'].append(makeAlert(2, reason, color, blink))

####################################################
#
#  Light 3: Forecast condition
#
####################################################
code = lookup.forecast[fc_idx].code
color, blink = alertForCondition(code)
reason = "Forecast (" + day + "): " + lookup.forecast[fc_idx].text
output['alerts'].append(makeAlert(3, reason, color, blink))

####################################################
#
#  Light 5: Tube / Overground status
#
####################################################
# https://api.tfl.gov.uk/Journey/JourneyResults/1000125/to/1000094
# Kew Gardens To Gunnersbury

print json.dumps(output, indent=4, sort_keys=True)


####################################################
#
# News
#
####################################################


#pp(lookup)
