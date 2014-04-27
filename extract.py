#! /usr/bin/env python

import re
import requests
import datetime
import time
from time import mktime as mktime
WEBSITE='https://malwr.com/analysis/?page='
ANALYSIS='https://malwr.com'
CLEAN='/media/astewart/Archive/Malwr/Benign/beneign_data.txt'
MALICIOUS='/media/astewart/Archive/Malwr/Mal/mal_data.txt'

MAL_COUNT=0
CLEAN_COUNT=0

def store_all(type,md5,timestamp,calls):
    global CLEAN_COUNT
    global MAL_COUNT
    integertime  = mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
    #print integertime
    if type == 0:
        CLEAN_COUNT+=1
        with open(CLEAN, 'a') as clean:
            for call in calls:

                clean.write("%s,%s,%s,%s,%s\n" % (md5,integertime,mktime(time.strptime(call[1], "%Y-%m-%d %H:%M:%S,%f")),call[0],call[2]))
    elif type == 1:
        MAL_COUNT+=1
        with open(MALICIOUS, 'a') as mal:
            for call in calls:
                
                mal.write("%s,%s,%s,%s,%s\n" % (md5,integertime,mktime(time.strptime(call[1], "%Y-%m-%d %H:%M:%S,%f")),call[0],call[2]))
    return


def get_calls(locations2):
    temp = re.compile("\"category\": \"(.*?)\", \"timestamp\": \"(.*?)\", \"api\": \"(.*?)\"", re.DOTALL|re.M)
    locations = temp.findall(locations2)
    
    #print locations
    return locations



def get_report(location,md5,score):
    try: 
            results = requests.get('%s%s' % (ANALYSIS, location))   
            #print results.content
            temp = re.compile("<section id=\"information\">.*?<td>FILE</td>.*?<td>(.*?)</td>.*?</section>", re.DOTALL|re.M)
            time = temp.findall(results.content)
            #print time
            
            graph_data = re.compile("<script type=\"text/javascript\">.*?var graph_raw_data = (.*?)</script>", re.DOTALL|re.M)
            locations2 = graph_data.findall(results.content)
            
            if int(score) == 0: #Benign Sample
                store_all(0,md5,time[0], get_calls(locations2[0]))
            elif int(score) > 15: #if AV score is greater than 15
                store_all(1,md5,time[0], get_calls(locations2[0]))
            #print location, locations
           # store_all(type,md5,time, get_calls(locations2[0]))
    except Exception as e:
            print e

def main():
    for i in range(1387): #1386
        try: 
            results = requests.get('%s%s' % (WEBSITE, i))   
            temp = re.compile("a href=\"(/analysis/[0-9a-zA-Z]+)/\"><span class=\"mono\">([0-9a-fA-F]{32})</span></a></td>.*?<td>(\d+)/(\d+)</td>", re.DOTALL|re.M)
            locations = temp.findall(results.content)
            print locations
            for record in locations:
                get_report(record[0],record[1],record[2])
            
        except Exception as e:
            print e
    print "Total Clean: %s" % CLEAN_COUNT
    print "Total MAL: %s" %MAL_COUNT

if __name__ == '__main__':
    main()