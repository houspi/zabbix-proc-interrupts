#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# For Zabbix
# Script returns the number of interrupts per CPU on the x86 architecture from the /proc/interrupts file
# For each IRQ and CPU pair, returns the number ot interrupts for this IRQ on this CPU
# When run without parameters, script works in LLD mode and returns the list of macros:
# {#CPUNUM} - kernel number. Culumn title from the /proc/interrupts file
# {#CPUIDX} - kernel index. Number from {#CPUNUM} 
# {#IRQ} - number of interrupt. Value from the first column of the /proc/interrupts file
# {#IRQLABEL}- type of interrupt and the name of the device that is located at that IRQ. Value from the last column of the /proc/interrupts file
#
# By houspi@gmail.com
#

import json
import re
import sys

INTERRUPTS_STAT_FILE = "/proc/interrupts"
ERROR_CODE = "-1"

def discovery():
    try :
        fh = open(INTERRUPTS_STAT_FILE, "r")
    except IOError :
        print ERROR_CODE
        return
    json_data = dict()
    json_data['data'] = []
    if fh:
        file_content = fh.readlines()
        fh.close()
        cpus = file_content[0].strip().split()
        cpus_count = len(cpus)
        for cpu in cpus :
            idx = int(re.search("\d+", cpu).group(0))
            for line in file_content[1:] :
                row = re.split("\s+", line.strip(), cpus_count+1)
                irq = re.sub(":$", "", row[0])
                label = "IRQ #" + irq + " " + re.sub("\s+", " ", row[-1])
                if (idx > 0 and ( irq == "ERR" or irq == "MIS" )) :
                    continue
                if(label == "0") :
                    label = irq
                json_data['data'].append( { '{#CPUNUM}': cpu, 
                                            '{#CPUIDX}': idx, 
                                            '{#IRQ}': irq, 
                                            '{#LABEL}': label } 
                                        )
    print json.dumps(json_data, indent=2, separators=(',', ':'), sort_keys=True )
    return

def get_data(cpu, irq):
    try :
        fh = open(INTERRUPTS_STAT_FILE, "r")
    except IOError :
        print ERROR_CODE
        return
    if fh :
        file_content = fh.readlines()
        fh.close()
        cpus = file_content[0].strip().split()
        cpus_count = len(cpus)
        try :
            idx = int(re.search("\d+", cpu).group(0))
        except AttributeError :
            print ERROR_CODE
            return
        for line in file_content[1:] :
            items = re.split("\s+", line.strip(), cpus_count+1)
            item_irq = re.sub(":$", "", items[0])
            if ( item_irq == irq ) :
                if ( idx < len(items)-1 ) :
                    print items[idx+1]
                else :
                    print 0
                break
    else :
        print ERROR_CODE
        return

    return

if __name__ == '__main__':
    if len(sys.argv) == 1 :
        discovery()
    elif len(sys.argv) == 3 :
        cpu = sys.argv[1]
        irq = sys.argv[2]
        get_data(cpu, irq)
    else :
        print ERROR_CODE


