#!/usr/bin/env python
 
"""
ID 04d9:8010 Holtek Semiconductor, Inc. 
"""
import usb.core
import usb.util as util
from array import array
import sys
from optparse import OptionParser, make_option
import pickle
from struct import unpack
import MySQLdb as mdb
 
dev = None
 
VID = 0x04d9
PID = 0x8010
 
# define HID constants
 
REQ_HID_GET_REPORT   = 0x01
REQ_HID_GET_IDLE     = 0x02
REQ_HID_GET_PROTOCOL = 0x03
 
REQ_HID_SET_REPORT   = 0x09
REQ_HID_SET_IDLE     = 0x0A
REQ_HID_SET_PROTOCOL = 0x0B
 
HID_REPORT_TYPE_INPUT   = 1<<8
HID_REPORT_TYPE_OUTPUT  = 2<<8
HID_REPORT_TYPE_FEATURE = 3<<8
 
def openDev():
    global dev
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        raise ValueError('Device not found')
 
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    dev.set_configuration() # do reset and set active conf. Must be done before claim.
    # intf number changed from None to 0
    util.claim_interface(dev, 0)
 
def setReport(reportId, data):
    #PYUSB_DEBUG=debug
    #LIBUSB_DEBUG=3
    #print "test"
    #print util.build_request_type(util.CTRL_OUT, util.CTRL_TYPE_CLASS, util.CTRL_RECIPIENT_INTERFACE)
    r = dev.ctrl_transfer(
        util.build_request_type(util.CTRL_OUT, util.CTRL_TYPE_CLASS, util.CTRL_RECIPIENT_INTERFACE), # bmRequestType,
        REQ_HID_SET_REPORT,
        0x0300, #HID_REPORT_TYPE_OUTPUT | reportId,
        0,                 # feature_interface_num
        data,              # data
        timeout=6000       # timeout (1000 was too small for C_FREE)
    )
    #ctrl_transfer(0x21, 0x09, 0x209, 0, data, timeout)
    #dev.ctrl_transfer(0x21, 0x09, 0x0300, 0, data, timeout)
    return r
 
def read():
    openDev()
    try:
        dev.read(0x81,64) #flush 
    except usb.core.USBError:
        #print "USB error"
        #print usb.core.USBError
        pass
     
    setReport(9, array('B',(0x10,0,0,0,0,0,0,0)))
 
    # Every user can have upto 12 variables
    # and additional 8*64 for user data
    r = []
    for i in xrange(120+8):
        x = dev.read(0x81,64)
        if not x:
            print >> sys.stderr, "Read failed"
            exit(1)
        if x[0]==0xff and (i<120):
            print >> sys.stderr,"Invalid data",x
            exit(1)
        r.append(x)    
 
    # Each variable can have upto 32 values
    frmt = "!" + "H"*32
    s = []
    for i in xrange(120) :
        x = unpack(frmt, r[i])
         
        # Variables 5 .. 10 are not available on my scale
        #if i>5 and i<10:
        #    err = [item for item in x if item!=0]
        #else:
        err = [item for item in x if item==0xffff]
        if len(err):
            print >> sys.stderr, "INVALID:", err
            exit(1)
 
        s.append(x)
    return s
 
def getUserliste(s, user):
    # Transpose from 12x32 to 32x12 and format
    dicti = {}
    liste = [] 
    j = 12*user
    for i in xrange(32):
        x = s[j+5][i] # date
        if not x:
           break
        #print "{:d}-{:02d}-{:02d}T07:00:00 {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:d} {:d}".format(
        #   1920+(x>>9), x>>5&0xf, x&0x1f,
        #   s[j+0][i]/10., s[j+1][i]/10., s[j+2][i]/10., s[j+3][i]/10., s[j+4][i]/10., s[j+6][i]/10., s[j+7][i]/10., s[j+8][i]/10., s[j+9][i]/10., s[j+10][i], s[j+11][i])
        dicti = {'Datum':"{:d}-{:02d}-{:02d}".format(1920+(x>>9), x>>5&0xf, x&0x1f),'Gewicht':s[j+0][i]/10., 'BF':s[j+1][i]/10., 'Wasser':s[j+2][i]/10., 'Muskel':s[j+3][i]/10., 'Knochen':s[j+4][i]/10., 'BF oben':s[j+6][i]/10. , 'BF unten':s[j+7][i]/10., 'Muskel oben':s[j+8][i]/10., 'Muskel unten':s[j+9][i]/10., 'BMR':s[j+10][i], 'AMR':s[j+11][i]}
        liste.append(dicti)
        ditcti = {}
    return liste 

def write_msql(user, liste):
    con = mdb.connect('192.168.192.2', 'beurer', 'beurer', 'Gesundheit')
    with con:
        cur = con.cursor()
        for eintrage in liste:
            Datum = eintrage.get("Datum")
            sql = 'SELECT * FROM ' + user + ' WHERE Datum = "' + str(Datum) +'"'
            cur.execute(sql)
            results = cur.fetchall()
            if results == ():
                sql = 'INSERT INTO ' + user + '(Datum, Gewicht, BF, Wasser, Muskel, Knochen, BF_oben, BF_unten, Muskel_oben, Muskel_unten, BMR, AMR) VALUES("' + str(eintrage.get("Datum")) + '", ' + str(eintrage.get("Gewicht")) + ', ' + str(eintrage.get("BF")) + ', ' + str(eintrage.get("Wasser")) + ', ' + str(eintrage.get("Muskel")) + ', ' + str(eintrage.get("Knochen")) + ', ' + str(eintrage.get("BF oben")) + ', ' + str(eintrage.get("BF unten")) + ', ' + str(eintrage.get("Muskel oben")) + ', ' + str(eintrage.get("Muskel unten")) + ', ' + str(eintrage.get("BMR")) + ', ' + str(eintrage.get("AMR")) + ')'
                #"UPDATE " + user +" SET hue = '" + str(eintrage.get("hue")) + "', bri = '" + str(eintrage.get("bri")) + "', sat = '" + str(eintrage.get("sat")) + "', an = '" + str(eintrage.get("an")) + "' WHERE Name = '" + device +"'"
                cur.execute(sql) 
 
 
def copy_from_scale():
 
    option_list = [
        make_option("-c", "--cached", action="store_true", dest="cached"),
        #make_option("-w", "--write",action="store",      dest="output_file"),
        make_option('-u', '--user', action='store',      dest='user'),
    ]
 
    parser = OptionParser(option_list=option_list, usage='Usage: %prog [options]')
    options, args = parser.parse_args()
 
    if options.cached:
        with open("dump.pickle") as f: s = pickle.load(f)
    else:
        s = read()
        with open("dump.pickle","w") as f: pickle.dump(s,f)
 
    user = 0
    if options.user:
        user=int(options.user)-1
 
    write_msql("Gewicht_Chris",getUserliste(s, 0))
    write_msql("Gewicht_Sabina",getUserliste(s, 1))
 
 
if __name__ == '__main__':
    #openDev()
    copy_from_scale()
