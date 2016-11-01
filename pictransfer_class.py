from subprocess import *
#from classes import myezcontrol
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
import os, sys, time
import datetime
from datetime import date
from time import localtime,strftime
import shutil, glob
#from alarmevents import alarm_event

#aes = alarm_event()

def main():
    trans = pictransfer()
    trans.check_transfer()

class pictransfer:

    def __init__(self):
        self.source = '/media/usb0/DCIM'
        self.source1 = '/media/usb/DCIM'
        self.sourceV = '/media/usb0/AVCHD/BDMV'
        self.destin = '/home/christoph/Photos'
        self.sourceRec = '/media/usb0/RECORDER'
        self.destinRec = '/mnt/array1/Bienchen/Belvoirpark/ZuSortieren'
        self.safemode = True
        self.SERVER_IP   = '192.168.192.10'
        self.PORT_NUMBER = 5005
        self.mySocket = socket( AF_INET, SOCK_DGRAM )
        self.finished = False
        self.RAW_subdir = False

    def log(self, text):
        zeit =  time.time()
        datum = date.today()
        datei = '/home/christoph/spyder/usb_devs/pictransfer' + str(datum) + '.log'
        f = open(datei, 'a')
        f.write('\n' + str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))+ ' Outputs: ' + str(text))
        f.closed  


    def create_folder(self,creationtime):
        cyear = str(creationtime.tm_year)
        if creationtime.tm_mon < 10:
            cmonth = "0" + str(creationtime.tm_mon)
        else:
            cmonth = str(creationtime.tm_mon)
        if creationtime.tm_mday < 10:
            cday = "0" + str(creationtime.tm_mday)
        else:
            cday = str(creationtime.tm_mday)
        fname = self.destin + "/" + cyear
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        fname = self.destin + "/" + cyear + "/" + cyear + " " + cmonth + " " + cday
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        return fname 

    def create_folderRec(self,creationtime):
        cyear = str(creationtime.tm_year)
        if creationtime.tm_mon < 10:
            cmonth = "0" + str(creationtime.tm_mon)
        else:
            cmonth = str(creationtime.tm_mon)
        if creationtime.tm_mday < 10:
            cday = "0" + str(creationtime.tm_mday)
        else:
            cday = str(creationtime.tm_mday)
        fname = self.destinRec + "/" + cyear
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        fname = self.destinRec + "/" + cyear + "/" + cyear + " " + cmonth + " " + cday
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        return fname 

    def move_file(self,filename):
        creationtime = date.timetuple(datetime.datetime.fromtimestamp((os.path.getctime(filename))))
        fname = self.create_folder(creationtime)
        if self.safemode:
            #print "Copy from " + filename + " to " + fname
            self.mySocket.sendto('Copy ' + filename,(self.SERVER_IP,self.PORT_NUMBER))
            shutil.copy(filename, fname)
            self.log(filename + " kopiert nach " + fname)
        else:
            #print "Move from " + filename + " to " + fname
            self.mySocket.sendto('Move ' + filename,(self.SERVER_IP,self.PORT_NUMBER))
            try:
                shutil.move(filename, fname)
                self.log(filename + " verschoben nach " + fname)
            except (OSError, shutil.Error) as e:
                self.log(e.errno)
                self.log(e.filename)
                self.log(e.strerror)
        for root, dirs, files in os.walk(fname):
            for momo in files:
                os.chmod(os.path.join(root, momo), 0777)   

    def move_fileRec(self,filename):
        creationtime = date.timetuple(datetime.datetime.fromtimestamp((os.path.getctime(filename))))
        fname = self.create_folderRec(creationtime)
        if self.safemode:
            #print "Copy from " + filename + " to " + fname
            self.mySocket.sendto('Copy ' + filename,(self.SERVER_IP,self.PORT_NUMBER))
            shutil.copy(filename, fname)
            self.log(filename + " kopiert nach " + fname)
        else:
            #print "Move from " + filename + " to " + fname
            self.mySocket.sendto('Move ' + filename,(self.SERVER_IP,self.PORT_NUMBER))
            try:
                shutil.move(filename, fname)
                self.log(filename + " verschoben nach " + fname)
            except (OSError, shutil.Error) as e:
                self.log(e.errno)
                self.log(e.filename)
                self.log(e.strerror)
        for root, dirs, files in os.walk(fname):
            for momo in files:
                os.chmod(os.path.join(root, momo), 0777)                
    
    def sync(self):
        for dirname, dirnames, filenames in os.walk(self.source):
            for subdirname in dirnames:
                folder = os.path.join(dirname, subdirname)
                for filename in glob.glob(os.path.join(folder, '*.JPG')):
                    self.move_file(filename)
                for filename in glob.glob(os.path.join(folder, '*.jpg')):
                    self.move_file(filename)
                for filename in glob.glob(os.path.join(folder, '*.MP4')):
                    self.move_file(filename)              
                for filename in glob.glob(os.path.join(folder, '*.AVI')):
                    self.move_file(filename) 
                for filename in glob.glob(os.path.join(folder, '*.WAV')):
                    self.move_file(filename)                     
                for filename in glob.glob(os.path.join(folder, '*.ARW')):
                    if self.RAW_subdir:
                      creationtime = date.timetuple(datetime.datetime.fromtimestamp((os.path.getctime(filename))))
                      fname = self.create_folder(creationtime)            
                      rawfolder = fname + "/RAW"
                      if not os.path.exists(rawfolder):
                          os.makedirs(rawfolder)
                          self.log(rawfolder + " erstellt")
                          os.chmod(rawfolder, 0777)
                      if self.safemode:
                          shutil.copy(filename, rawfolder)
                          self.log(filename + " kopiert nach " + rawfolder)
                      else:
                          shutil.move(filename, rawfolder)
                          self.log(filename + " verschoben nach " + rawfolder)
                    else:
                        self.move_file(filename)
                        
        for dirname, dirnames, filenames in os.walk(self.source1):
            for subdirname in dirnames:
                folder = os.path.join(dirname, subdirname)
                for filename in glob.glob(os.path.join(folder, '*.JPG')):
                    self.move_file(filename)
                for filename in glob.glob(os.path.join(folder, '*.jpg')):
                    self.move_file(filename)
                for filename in glob.glob(os.path.join(folder, '*.MP4')):
                    self.move_file(filename)   
                for filename in glob.glob(os.path.join(folder, '*.AVI')):
                    self.move_file(filename)     
                for filename in glob.glob(os.path.join(folder, '*.WAV')):
                    self.move_file(filename)                     
                for filename in glob.glob(os.path.join(folder, '*.ARW')):
                    if self.RAW_subdir:
                      creationtime = date.timetuple(datetime.datetime.fromtimestamp((os.path.getctime(filename))))
                      fname = self.create_folder(creationtime)            
                      rawfolder = fname + "/RAW"
                      if not os.path.exists(rawfolder):
                          os.makedirs(rawfolder)
                          self.log(rawfolder + " erstellt")
                          os.chmod(rawfolder, 0777)
                      if self.safemode:
                          shutil.copy(filename, rawfolder)
                          self.log(filename + " kopiert nach " + rawfolder)
                      else:
                          shutil.move(filename, rawfolder)
                          self.log(filename + " verschoben nach " + rawfolder)
                    else:
                        self.move_file(filename)

    def syncV(self):
        for dirname, dirnames, filenames in os.walk(self.sourceV):
            for subdirname in dirnames:
                folder = os.path.join(dirname, subdirname)
                for filename in glob.glob(os.path.join(folder, '*.MTS')):
                    self.move_file(filename)

    def syncRec(self):
        for dirname, dirnames, filenames in os.walk(self.sourceRec):
            for subdirname in dirnames:
                folder = os.path.join(dirname, subdirname)
                for filename in glob.glob(os.path.join(folder, '*.MP3')):
                    self.move_fileRec(filename)                    

    def check_transfer(self):
        self.mySocket.sendto('Checking',(self.SERVER_IP,self.PORT_NUMBER))
        time.sleep(3)
        self.log("Check Started")
#        aes.new_event(description="USB Check started", prio=0)
        if os.path.exists("/media/usb0/DCIM"):
            self.mySocket.sendto('Starting',(self.SERVER_IP,self.PORT_NUMBER))
            self.log("Pictures found")
            self.sync()
            self.mySocket.sendto('Finished',(self.SERVER_IP,self.PORT_NUMBER))
            time.sleep(30)
#        if os.path.exists("/media/usb0/MP_ROOT"):
#            self.mySocket.sendto('Starting',(self.SERVER_IP,self.PORT_NUMBER))
#            self.log("Pictures found")
#            self.sync()
#            self.mySocket.sendto('Finished',(self.SERVER_IP,self.PORT_NUMBER))
#            time.sleep(30)            
        if os.path.exists("/media/usb0/AVCHD/BDMV"):
            self.finished = False            
            self.mySocket.sendto('Starting',(self.SERVER_IP,self.PORT_NUMBER))
            self.log("Videos found")
            self.syncV()
            self.mySocket.sendto('Finished',(self.SERVER_IP,self.PORT_NUMBER))
            time.sleep(30)
        if os.path.exists("/media/usb0/RECORDER"):
            self.mySocket.sendto('Starting',(self.SERVER_IP,self.PORT_NUMBER))
            self.log("Audio Recordings found")
            self.syncRec()
            self.mySocket.sendto('Finished',(self.SERVER_IP,self.PORT_NUMBER))
#            aes.new_event(description="Dictiergeraet geleert", prio=3)
            time.sleep(30)            
        self.mySocket.sendto('',(self.SERVER_IP,self.PORT_NUMBER))

if __name__ == '__main__':
    main() 