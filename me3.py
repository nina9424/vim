from multiprocessing import Process
import sys
import commands
import os
from imaplib import Commands
import time
from pickle import NONE
import threading
import thread
import sys
import signal

OS_interface_id_cmd="sudo ovs-vsctl --columns=name,external-ids list Interface|grep external_ids| awk {'print $4'}|cut -c 11-46|grep -v '^$'"
interface_name_cmd="sudo ovs-vsctl --columns=name,external-ids list Interface|grep external_ids| awk {'print $4'}|cut -c 11-46|grep -v '^$'|cut -c -11"
OS_instance_id_cmd="sudo ovs-vsctl --columns=name,external-ids list Interface|grep external_ids| awk {'print $6'}|cut -c 10-45|grep -v '^$'"
OS_network_id_cmd="neutron port-show " + commands.getoutput(OS_interface_id_cmd) +"|grep network_id|awk {'print $4'}"
RX_cmd="netstat -i | grep " + commands.getoutput(OS_interface_id_cmd)+"|awk {'print $4'}"
TX_cmd="netstat -i | grep " + commands.getoutput(OS_interface_id_cmd)+"|awk {'print $8'}"

port_list = []
num_of_port=commands.getoutput(OS_interface_id_cmd+"|wc -l")


class Port:
        def __init__(self, interface_name="None", OS_instance_id="None", OS_interface_id="None", OS_network_id="None", RX="None", TX="None", TX_bps="None",RX_bps="None"):
            self.interface_name=interface_name
            self.OS_instance_id=OS_instance_id
            self.OS_interface_id=OS_interface_id
            self.OS_network_id=OS_network_id
            self.RX=RX
            self.TX=TX
	    self.TX_bps=TX_bps
	    self.RX_bps=RX_bps


def map_iface_OS_variable():
    global num_of_port
    int_name="temp"
    os_inst_id="temp"
    os_inter_name="temp"
    os_net_id="temp"
    while True:
        num_of_port=commands.getoutput(OS_interface_id_cmd+"|wc -l")
        for i in range(1,int(num_of_port)+1):
            port_list.append(Port())
	    int_name="qvo"+commands.getoutput(interface_name_cmd+"|sed -n -e "+str(i)+"p")
	    os_inst_id = commands.getoutput(OS_instance_id_cmd+"|sed -n -e "+str(i)+"p")
            os_inter_name=commands.getoutput(OS_interface_id_cmd+"|sed -n -e "+str(i)+"p")
            os_net_id=commands.getoutput("neutron port-show " +  os_inter_name +"|grep network_id|awk {'print $4'}")
            port_list[i-1]=Port(int_name, os_inst_id, os_inter_name, os_net_id)
        time.sleep(5)
'''
            port_list[i-1]=Port("qvo"+commands.getoutput(interface_name_cmd+"|sed -n -e "+str(i)+"p"), commands.getoutput(OS_instance_id_cmd+"|sed -n -e "+str(i)+"p"), commands.getoutput(OS_interface_id_cmd+"|sed -n -e "+str(i)+"p"), "none", commands.getoutput(RX_cmd+"|sed -n -e "+str(i)+"p"), commands.getoutput(TX_cmd+"|sed -n -e "+str(i)+"p"))
            port_list[i-1].OS_network_id=commands.getoutput("neutron port-show " + port_list[i-1].OS_interface_id +"|grep network_id|awk {'print $4'}")
'''



def update_traffic():
    while True:
        time.sleep(1)
        for i in range(1,int(num_of_port)+1):
            global port_list
            try:
                port_list[i-1].RX=commands.getoutput("netstat -i | grep " + port_list[i-1].interface_name+"|awk {'print $4'}")
                port_list[i-1].TX=commands.getoutput("netstat -i | grep " + port_list[i-1].interface_name+"|awk {'print $8'}")
                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                print "RX="+port_list[i-1].RX
                print "TX="+port_list[i-1].TX
            except IndexError:
                pass


def write_log():
  try:
    global port_list
    TX_bps_before= []
    RX_bps_before= []
    while True:
        f1=open('./testfile', 'w+')
	for i in range(1, int(num_of_port)+1):
            try:
		TX_bps_before.append("temp")
		RX_bps_before.append("temp")
		TX_bps_before[i-1]=commands.getoutput("ifconfig "+port_list[i-1].interface_name+"|grep bytes|awk {'print $2'}|cut -c 7- ")
                RX_bps_before[i-1]=commands.getoutput("ifconfig "+port_list[i-1].interface_name+"|grep bytes|awk {'print $6'}|cut -c 7- ")
	    except IndexError:
                pass
        time.sleep(1)
#        print "=========================="
        if TX_bps_before[0] !="temp" and RX_bps_before[0]!="temp":
            for i in range(1, int(num_of_port)+1):
                try:
                    port_list[i-1].RX=commands.getoutput("netstat -i | grep " + port_list[i-1].interface_name+"|awk {'print $4'}")
                    port_list[i-1].TX=commands.getoutput("netstat -i | grep " + port_list[i-1].interface_name+"|awk {'print $8'}")
	            port_list[i-1].TX_bps=str(int(commands.getoutput("ifconfig "+port_list[i-1].interface_name+"|grep bytes|awk {'print $2'}|cut -c 7- ")) - int(TX_bps_before[i-1]))
		    port_list[i-1].RX_bps=str(int(commands.getoutput("ifconfig "+port_list[i-1].interface_name+"|grep bytes|awk {'print $6'}|cut -c 7- ")) - int(RX_bps_before[i-1]))
#		    print  str(int(commands.getoutput("ifconfig "+port_list[i-1].interface_name+"|grep bytes|awk {'print $6'}|cut -c 7- ")))+"  "+str(int(RX_bps_before[i-1]))
                    f1.write("|Interface Name= "+port_list[i-1].interface_name+" |OS_instance_id= "+port_list[i-1].OS_instance_id+" |OS_interface_id= "+port_list[i-1].OS_interface_id+" |OS_network_id= "+port_list[i-1].OS_network_id+ " |TX= "+port_list[i-1].TX+ " |RX= "+port_list[i-1].RX+" |RX_Bps= "+port_list[i-1].RX_bps+" |TX_Bps= "+port_list[i-1].TX_bps+"\n")
#                    print "|Interface Name= "+port_list[i-1].interface_name+" |OS_instance_id= "+port_list[i-1].OS_instance_id+" |OS_interface_id= "+port_list[i-1].OS_interface_id+" |OS_network_id= "+port_list[i-1].OS_network_id+ " |TX= "+port_list[i-1].TX+ " |RX= "+port_list[i-1].RX+" |RX_Bps= "+port_list[i-1].RX_bps+" |TX_Bps= "+port_list[i-1].TX_bps+"\n"
                except (IndexError, ValueError):
                    pass
  except IndexError:
    pass
threads=[]

if __name__=='__main__':
    t = threading.Thread(target=map_iface_OS_variable)
    threads.append(t)
    t.start()
    t2 = threading.Thread(target=update_traffic)
    threads.append(t2)
    #t2.start()
    t3 = threading.Thread(target=write_log)
    threads.append(t3)
    t3.start()

