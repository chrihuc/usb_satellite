#!/usr/bin/env python
import pyudev
import subprocess
import sys
import os
from socket import socket, AF_INET, SOCK_DGRAM
from pictransfer_class import pictransfer
from beurer import copy_from_scale
#from mysql_con import setting_s
import time

SERVER_IP   = '192.168.192.10'
PORT_NUMBER = 5005
SIZE = 1024
mySocket = socket( AF_INET, SOCK_DGRAM )
trans = pictransfer()



def vfd_show(text):
    pass
#    mySocket.sendto(text,(SERVER_IP,PORT_NUMBER))
 
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.start()
monitor.filter_by('usb', 'usb_device')
#print "Started:", monitor.started
vfd_show("Started:")

def udp_send(szene):
    dicti = {}
    dicti['Szene'] = szene
    #dicti['Command'] = 'Update'
    hbtsocket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    hbtsocket.sendto(str(dicti),('192.168.192.10',5000))  

for device in iter(monitor.poll, None):
    #print device.action, device.subsystem, device
    vfd_show(device.action)
    try:
        atts = device.attributes
        print atts
        vendor = atts["idVendor"]
        product = atts["idProduct"]
        name = atts["product"]
        print "%s %s:%s" % (name, vendor, product)
        vfd_show("%s %s:%s" % (name, vendor, product))
    except (KeyError, TypeError) as e:
        continue
    if device.action !="add":
        continue
    if vendor == "04d9": #idProduct = 8010
        #print "call"
        vfd_show("call")
        copy_from_scale()
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")        
        vfd_show("done")
    if vendor == "0590": #idProduct = 0028
        #print "call"
        vfd_show("call")
        #subprocess.call("./omron.sh")
        #print "done"
        vfd_show("done")
    if vendor == "0bda": #idProduct = 0028
        #print "Cardreader"
        vfd_show("Cardreader")
        trans.check_transfer()
        udp_send('convert_mts')
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")
        vfd_show("done")
    if vendor == "054c": #idProduct = 0028
        #print "Handycam"
        vfd_show("Handycam")
        trans.check_transfer()
        udp_send('convert_mts')
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")
        vfd_show("done")
    if vendor == "07b4": #idProduct = 0028
        #print "Olympus"
        vfd_show("Olympus")
        time.sleep(10)  
        trans.check_transfer()
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")
        vfd_show("done")  
    if vendor == "054c": #idProduct = 0028
        #print "Olympus"
        vfd_show("Olympus")
        time.sleep(10)  
        trans.check_transfer()
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")
        vfd_show("done")          
    if vendor == "0781": #idProduct = 0028
        vfd_show("Music BMW")
        time.sleep(10)
        if os.path.exists("/media/usb0/Playlists"):
            os.system("sudo /home/chris/homecontrol/musbmws.sh")
#        setting_s("Durchsage", "Kopieren abgeschlossen")
#        set_szene("sz_BadDurchsage")
        vfd_show("done") 	  
    if vendor == "04a9" and product == "190a":
        time.sleep(5)
        os.system("sudo svc -du /etc/service/scand")
