#from subprocess import *
#from classes import myezcontrol

import os, time
import datetime
from datetime import date
from time import localtime,strftime
import shutil, glob
from os.path import expanduser

#from alarmevents import alarm_event

#aes = alarm_event()

home = expanduser("~")
dir_path = os.path.dirname(os.path.realpath(__file__))
# Photos
destin = home + '/Photos'
# Dictiergeaet
destinRec = '/mnt/array1/Bienchen/Belvoirpark/ZuSortieren'

sources = ['/media/usb/', '/media/usb0/', '/media/usb1/', '/media/usb2/']

def main():
    trans = pictransfer()
    trans.check_transfer()

class pictransfer:

    def __init__(self):
        self.safemode = False
        self.RAW_subdir = False

    def log(self, text):
        zeit =  time.time()
        datum = date.today()
        datei = str(datum) + '.log'
        f = open(datei, 'a')
        f.write('\n' + str(strftime("%Y-%m-%d %H:%M:%S",localtime(zeit)))+ ' Outputs: ' + str(text))
        f.closed  

    def create_folder(self,creationtime, destination):
        cyear = str(creationtime.tm_year)
        if creationtime.tm_mon < 10:
            cmonth = "0" + str(creationtime.tm_mon)
        else:
            cmonth = str(creationtime.tm_mon)
        if creationtime.tm_mday < 10:
            cday = "0" + str(creationtime.tm_mday)
        else:
            cday = str(creationtime.tm_mday)
        fname = destination + "/" + cyear
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        fname = destination + "/" + cyear + "/" + cyear + " " + cmonth + " " + cday
        if not os.path.exists(fname):
            os.makedirs(fname)
            self.log(fname + " erstellt")
            os.chmod(fname, 0777)
        return fname 

    def move_file(self,filename, destination):
        creationtime = date.timetuple(datetime.datetime.fromtimestamp((os.path.getctime(filename))))
        fname = self.create_folder(creationtime, destination)
        if self.safemode:
            shutil.copy(filename, fname)
            self.log(filename + " kopiert nach " + fname)
        else:
            try:
                os.chmod(filename, 0777) 
                shutil.move(filename, fname)
                self.log(filename + " verschoben nach " + fname)
            except (OSError, shutil.Error) as e:
                shutil.copy(filename, fname)
                self.log(filename + " kopiert nach " + fname)
        for root, dirs, files in os.walk(fname):
            for momo in files:
                try:
                    os.chmod(os.path.join(root, momo), 0777)  
                except:
                    pass

    def sync(self, source, destination):
        for counter in range(0,2):
            for dirname, dirnames, filenames in os.walk(source):
                for subdirname in dirnames:
                    folder = os.path.join(dirname, subdirname)
                    for filename in glob.glob(os.path.join(folder, '*.JPG')):
                        self.move_file(filename, destination)
                    for filename in glob.glob(os.path.join(folder, '*.jpg')):
                        self.move_file(filename, destination)
                    for filename in glob.glob(os.path.join(folder, '*.MP4')):
                        self.move_file(filename, destination)              
                    for filename in glob.glob(os.path.join(folder, '*.AVI')):
                        self.move_file(filename, destination) 
                    for filename in glob.glob(os.path.join(folder, '*.WAV')):
                        self.move_file(filename, destination)     
                    for filename in glob.glob(os.path.join(folder, '*.MTS')):
                        self.move_file(filename, destination)  
                    for filename in glob.glob(os.path.join(folder, '*.MP3')):
                        self.move_file(filename, destination)                          
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
                            self.move_file(filename, destination)
                
    def check_transfer(self):
        time.sleep(3)
        self.log("Check Started")
        for source in sources:
            if os.path.exists(source + "DCIM"):
                self.log("Pictures found")
                self.sync(source + "DCIM", home + '/Photos')            
            if os.path.exists(source + "AVCHD"):
                self.log("Videos found")
                self.sync(source + "AVCHD", home + '/Photos')
                
#                ffmpeg -i 00022.MTS -s 800x600 -c:a aac -q:a 2 -b:v 4000k -strict experimental 00022.MP4
                
            if os.path.exists(source + "MP_ROOT"):
                self.log("Videos found")
                self.sync(source + "MP_ROOT", home + '/Photos')            
    #        if os.path.exists("/media/usb0/RECORDER"):
    #            self.log("Audio Recordings found")
    #            self.sync("/media/usb0/RECORDER")          

if __name__ == '__main__':
    main() 