import logging
from spyne import Application, rpc, ServiceBase, \
    Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from collections import defaultdict
import requests
from spyne import srpc
#import urllib2

"""
req = urllib2.Request('https://api.spotcrime.com/crimes.json?lat=37.334164&lon=-121.884301&radius=0.02&key=.')
response = urllib2.urlopen(req)
r = response.read()"""

class CrimeDetect(ServiceBase):
    @srpc(Unicode,Unicode,Unicode,_returns=Iterable(Unicode))

    def checkcrime(lat, lon, radius ):

        total_crime = 0
        firstAM = 0
        secondAM=0;
        thirdAM=0;
        fourthAM=0;
        firstPM = 0
        secondPM = 0;
        thirdPM = 0;
        fourthPM = 0;
        total_crime = 0
        resp = {}
        respCrimeType = {}
        respTime = {}
        crimetype={}
        typelist=[]
        r= requests.get("https://api.spotcrime.com/crimes.json?lat=" +lat + "&lon="+ lon +" &radius=" +radius + "&key=.").json()
        mylist = []
        myliststreet=[]
        for crime in r["crimes"]:
            total_crime += 1
            hour = int(crime["date"][9:11])
            minutes = int(crime['date'][12:14])
            ampm = crime['date'][15:17]
            typelist.append(crime['type'])
            mylist.append(crime['address'])

            if ((hour == 12 and minutes > 0 and minutes < 60) or (hour == 1 and minutes < 60) or ( hour == 2 and minutes < 60) or (hour == 3 and minutes == 0)):
                if (ampm == 'AM'):
                    firstAM += 1
                elif (ampm == 'PM'):
                    firstPM += 1
            elif ((hour == 3 and minutes > 0 and minutes < 60) or (hour == 4 and minutes < 60) or (hour == 5 and minutes < 60) or (hour == 6 and minutes == 0)):
                if (ampm == 'AM'):
                    secondAM += 1
                elif (ampm == 'PM'):
                    secondPM += 1
            elif ((hour == 6 and minutes > 0 and minutes < 60) or (hour == 7 and minutes < 60) or ( hour == 8 and minutes < 60) or (hour == 9 and minutes == 0)):
                if (ampm == 'AM'):
                    thirdAM += 1
                elif (ampm == 'PM'):
                    thirdPM += 1
            elif ((hour == 9 and minutes > 0 and minutes < 60) or (hour == 10 and minutes < 60) or (hour == 11 and minutes < 60)):
                if (ampm == 'AM'):
                    fourthAM += 1
                elif (ampm == 'PM'):
                    fourthPM += 1
            elif(hour == 12 and minutes == 0):
                if (ampm == 'PM'):
                    fourthAM += 1
                elif (ampm == 'AM'):
                    fourthPM += 1




        for type in typelist:
            if type in crimetype:
                crimetype[type] += 1
            else:
                crimetype[type] = 1

        for word in mylist:
            if "OF" in word:
                words= word.split('OF')
                myliststreet.append(words[1])
            elif "&" in word:
                words = word.split('&')
                myliststreet.append(words[0])
                myliststreet.append(words[1])



        respTime["12:01am - 3am"] = firstAM
        respTime["12:01pm-3pm"] = firstPM
        respTime["3:01am-6am"]=secondAM
        respTime["3:01pm-6pm"] = secondPM
        respTime["6:01am-9am"]=thirdAM
        respTime[ "6:01pm-9pm"]=thirdPM
        respTime["9:01am-12noon"] = fourthAM
        respTime["9:01pm-12midnight"] =fourthPM
        top = 3
        counts = defaultdict(int)
        for x in myliststreet:
            counts[x] += 1

        resp["event_time_count"]=respTime
        resp["crime_type_count"]=crimetype
        resp["total_crime"] = total_crime


        resp["the_most_dangerous_streets"] = sorted( counts,reverse=True, key=counts.get)[:top]

        yield resp




application = Application([CrimeDetect],
                          tns='spyne.examples.hello',
                          in_protocol=HttpRpc(validator='soft'),
                          out_protocol=JsonDocument()
                          )
if __name__ == '__main__':

    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
