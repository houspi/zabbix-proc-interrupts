#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# For Zabbix
# The script creates stacked graphs for interrupts from the /proc/interrupts file
# For each interrupt, a graph containing all cores is created
#
# By houspi@gmail.com
#

import sys
import requests
import json
import re
from pprint import pprint

# taken from the zabbix php
color_palette = [ '1A7C11', 'F63100', '2774A4', 'A54F10', 'FC6EA3', '6C59DC', 'AC8C14', 
                  '611F27', 'F230E0', '5CCD18', 'BB2A02', '5A2B57', '89ABF8', '7EC25C', 
                  '274482', '2B5429', '8048B4', 'FD5434', '790E1F', '87AC4D', 'E89DF4',
                ]

graph_width  = 900
graph_height = 200
items_key = "system.irq"
app = "/zabbix/api_jsonrpc.php"

headers = {'Content-type': 'application/json-rpc'}

def usage():
    print '''Usage: %s zabbix_host_name proto user password host_id 

zabbix_host_name:   FQDN or ip-address of Zabbix server
proto:              http | https
user:               zabbix username with permissions to create graph
password:           password
host_id:            host_id for which the graphs are created
''' % sys.argv[0]

def main():
    print "Hello I'm here";
    if len(sys.argv) < 6 :
        usage()
        sys.exit(0)

    zabbix_host_name = sys.argv[1]
    proto = sys.argv[2]
    user = sys.argv[3]
    password = sys.argv[4]
    host_id = sys.argv[5]

    url = proto + "://" + zabbix_host_name + app
    
    apiinfo = {'jsonrpc':'2.0','method':'apiinfo.version','id':1,'auth':None,'params':{}}
    try :
        r = requests.post(url, data=json.dumps(apiinfo), headers=headers)
    except Exception as e:
        print "Connection error: ", str(e)
        sys.exit(1)

    if r.status_code != 200 :
        print "HTTP error: ", r.status_code
        sys.exit(1)
    json_result = r.json()
    if ( "result" in json_result) :
        api_version = json_result["result"]
    else :
        print "JSON Error: ", r.text
        sys.exit(1)

    print "Zabbix API version:", api_version
    
    user_login = {'jsonrpc':'2.0','method':'user.login','id':1,'auth':None,'params':{'user':user,'password':password}}
    r = requests.post(url, data=json.dumps(user_login), headers=headers)
    
    try :
        auth_id = r.json()['result']
    except :
        print "Auth error:", r.text
        sys.exit(1)

    items_get = {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
                        "output": "extend",
                        "hostids": host_id,
                        "search": {
                            "key_": items_key
                        },
                        "sortfield": "name"
                    },
                    "auth": auth_id,
                    "id": 1
    }
    r = requests.post(url, data=json.dumps(items_get), headers=headers)
    try :
        items = r.json()['result']
    except :
        print "item.get error\n", r.text
        sys.exit(1)

    graph_list = dict()
    for item in items :
        name = item["name"]
        matches = re.findall(r"^(#\w+).+? on (.+?), (.+?)$", name)
        irq_num = matches[0][0].encode('ascii','ignore')
        cpu_name = matches[0][1].encode('ascii','ignore')
        irq_name = matches[0][2].encode('ascii','ignore')
        graph_name = "IRQ %s, %s"%(irq_num, irq_name)
        if graph_name in graph_list :
            graph_list[graph_name][cpu_name] = item["itemid"].encode('ascii','ignore')
        else :
            graph_list[graph_name] = dict()
            graph_list[graph_name][cpu_name] = item["itemid"].encode('ascii','ignore')

    for graph in graph_list :
        gitems = list()
        idx = 0;
        for cpu in sorted(graph_list[graph]) :
            gitems.append( {"itemid": graph_list[graph][cpu],
                            "sortorder": idx,
                            "color": color_palette[ int(idx) % (len(color_palette)-1) ], 
                            } )
            idx+=1
        new_graph = {
            "jsonrpc": "2.0",
            "method": "graph.create",
            "params": {
                "name"  : graph,
                "width" : graph_width,
                "height": graph_height,
                "graphtype": "1",
                "show_triggers": "0",
                "ymin_type" : "1",
                "yaxismin": "0.0000",
                "gitems": gitems, 
            },
            "auth": auth_id,
            "id": 1
        }
        print "graph.create:", graph
        r = requests.post(url, data=json.dumps(new_graph), headers=headers)
        print "graph.create Result:\n", r.text
        
    
if __name__ == '__main__':
    main()
