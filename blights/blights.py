import json
import threading
import time
import logging
from pprint import pprint
from blinkstick import blinkstick
from datetime import datetime
from Queue import Queue

logging.basicConfig(format='%(asctime)s %(message)s',level='INFO')

leds = {}
control_queue = Queue()

bstick = blinkstick.find_first()
if bstick is not None:
    logging.info("Found blinkstick!")
    bstick.set_mode(2)
    time.sleep(0.02)
else:
    logging.warning("No blinkstick found!")


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,*args,**kwargs):
        super(StoppableThread,self).__init__(*args,**kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def main():
    
    for i in range(0,7):
        setColor(i,'black')

    # blinkstick gets confused if we give it commands too close together
    # so we need to do comms via a single thread so we can throttle
    consumer = threading.Thread(target = processQueue)
    consumer.start()
    
    while(1):
        readAndExecute()
        time.sleep(30)


def processQueue() :
    global control_queue
    global bstick
    
    while True :
        logging.info(" QQQQQQQQQQQ waiting for input")
        f = control_queue.get(block=True)
        logging.info(" QQQQQQQQQQQ processing input")
        f()
        # throttle comms so we don't overload the hardware's capabilities
        time.sleep(0.02)


def readAndExecute():
    logging.info('********* refreshing data from config file ************')
    with open('defs.json') as data_file:    
        data = json.load(data_file)

    # set intensity of all channels
    if 'intensity' in data.keys() and bstick is not None:
        bstick.set_max_rgb_value(data['intensity'])
    
    types = data['alert_types']

    for alert in data['alerts']:
        processAlert(alert, types)

    removeStaleAlerts(data['alerts'])


def removeStaleAlerts(alerts):
    logging.info("----------------> REMOVE STALE ALERTS")
    global leds

    defined_alerts = []
    for alert in alerts:
        defined_alerts.append(alert['position'])

    for led in leds.keys():
        logging.debug("STALE CHECK: " + str(led))
        if led not in defined_alerts:
            logging.warning("LED " + str(led) + " no longer in config, resetting black")
            # reset this led to black
            setColor(led,'black')
            entry = leds.pop(led)
            # kill off any existing thread for this led
            if 'thread' in entry.keys():
                thread = entry['thread']
                thread.stop()
                thread.join
            
def processAlert(alert,types):
    logging.info('processAlert ' + str(alert['position']))
    type = alert['type']
    pos = alert['position']

    if type == 'INDIVIDUAL':
        executeAlert(pos,alert['spec'])
    else:
        executeAlert(pos,types[type])


def executeAlert(pos,spec):
    global leds

    if pos in leds.keys():
        old_spec = leds[pos]['spec']
        if recursiveEquals(old_spec, spec):
            # we already have a thread running the identical spec
            # so do nothing
            logging.info("ALREADY running identical spec for position " + str(pos))
            return
        logging.info('  Stopping thread for position 4')
        thread = leds.pop(pos)['thread']
        thread.stop()
        thread.join
        logging.info("THREAD JOINED FOR LED: " + str(pos))
    
    if 'blink' in spec.keys():
        thread = StoppableThread(target = executeBlink, args = (pos,spec,))
        leds[pos] = {'spec': spec, 'thread': thread}
        thread.start()
    elif 'colors' in spec.keys():
        thread = StoppableThread(target = executeColorCycle, args = (pos,spec,))
        leds[pos] = {'spec': spec, 'thread': thread}
        thread.start()
    elif 'color' in spec.keys():
        executeColor(pos,spec)
        leds[pos] = {'spec': spec}


def executeColor(pos,spec):
    color = spec['color']
    setColor(pos,color)


def executeColorCycle(pos,spec):
    animate = spec['animate']
    if animate is None:
        animate = 1000

    while(1):
        for color in spec['colors']:
            setColor(pos,color)
            time.sleep(animate/1000.0)
        if threading.current_thread().stopped():
            break
    logging.info("COLOR CYCLE thread ends")


def executeBlink(pos,spec):
    on =  spec['blink']['on']
    off = spec['blink']['off']

    while(1):
        setColor(pos,spec['color'])
        time.sleep(on/1000.0)
        if threading.current_thread().stopped():
            break
        setColor(pos,'black')
        if threading.current_thread().stopped():
            break
        time.sleep(off/1000.0)
        if threading.current_thread().stopped():
            break
    logging.info("BLINK thread ends")


def setColor(pos,col):
    logging.info('setColorActual ' + str(pos) + ' ' + col)
    global control_queue
    global bstick
    
    if col[:1] == '#':
        logging.info(datetime.now().strftime('%H:%M:%S') + 'bstick.set_color(channel='+str(pos)+',hex='+col+')')
        control_queue.put(lambda: bstick.set_color(channel=0,index=pos,hex=col))
    else:
        logging.info(datetime.now().strftime('%H:%M:%S') + ' bstick.set_color(channel='+str(pos)+',name='+col+')')
        control_queue.put(lambda: bstick.set_color(channel=0,index=pos,name=col))


def recursiveEquals(spec1, spec2):
    return (json.dumps(spec1,sort_keys=True) == json.dumps(spec2,sort_keys=True))
    
main()
    
    


