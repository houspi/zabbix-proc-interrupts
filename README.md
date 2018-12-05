# zabbix-proc-interrupts
Zabbix plugin for /proc/interrupts monitoring  

# proc_interrupts.py
Script returns the number of interrupts per CPU on the x86 architecture from the /proc/interrupts file  
For each IRQ and CPU pair, returns the number ot interrupts for this IRQ on this CPU  
When run without parameters, script works in LLD mode and returns the list of macros:  
 {#CPUNUM} - kernel number. Culumn title from the /proc/interrupts file  
 {#CPUIDX} - kernel index. Number from {#CPUNUM}  
 {#IRQ} - number of interrupt. Value from the first column of the /proc/interrupts file  
 {#IRQLABEL}- type of interrupt and the name of the device that is located at that IRQ. Value from the last column of the /proc/interrupts file  

# creategraphs_for_interrupts.py
The script creates stacked graphs for interrupts from the /proc/interrupts file  
For each interrupt, a graph containing all cores is created  
