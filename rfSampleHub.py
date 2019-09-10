import h5py
import numpy as np

import tables
import time
import datetime
import os
from vnaGPIBMocMod import vnaHP8753C_GpibMock
from vna2PortGPIBMod import vnaHP8753C_Gpib
from dbHdf5TablesMod import hdf5DataTable

import matplotlib.pyplot as plt

import rfSampleHub_interface

setUp = {
  'time' : None,
  'session': 0,
  'freqSt': '2GHZ',
  'freqEn': '3GHZ',
  'material' : 'water',
  'concentrate' : 0.8
}

logBaseName = "sampleData"
LOCATIONS = ['Proto_Station_0']
MATERIALS = ['H2O', 'Air']
SAMPLE_SHAPE = (2,100)
MAX_SESS_SAMPLES = 100
MOCK = False
MAX_GRAPH = 10

hdStore = None
hp8753 = None
hp8753Mock = None

dataBaseName = "dataFile0"

def unixTimePostfix(time):
  now = datetime.datetime.fromtimestamp(time)
  postfix = now.strftime("%d_%H%M%S")
  return postfix

def timeLogPostfix():
  now = datetime.datetime.now()
  postfix = now.strftime("%d_%H%M%S")
  return postfix

def plotMeas(w_,X_):
  w = np.array(w_)
#  X = np.array(X_)
  cpal = ['skyblue', 'green', 'red', 'yellow']
  plt.subplot(2,1,1)
  for i, X in enumerate(X_):
    magX = np.abs(X);
    #print (X)
    plt.plot(w,magX, marker='', color=cpal[i], linewidth=1)
 #   plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('|H|');
  plt.subplot(2,1,2)
  for i, X in enumerate(X_):
    magX = np.abs(X);
    angX = np.angle(X);
    plt.plot(w,angX, marker='', color=cpal[i], linewidth=1)
    plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('Phase response');
#    plt.title('Phase Response')
  plt.show()
  

def plotMeas2(title, w_,X_):
  w = np.array(w_)
  X = np.array(X_)
  magX = 20*np.log10(np.abs(X));
  angX = np.angle(X);
  plt.subplot(2,1,1)
  plt.plot(w,magX)
  plt.xlabel('frequency in GHZ units'); 
  plt.ylabel(title+': |H|');
  plt.subplot(2,1,2)
  plt.plot(w,angX)
  plt.xlabel('frequency in GHZ units'); 
  plt.ylabel(title+': Phase response');
  #plt.title('Phase Response')
  plt.show()



class rfSampleHubHP(rfSampleHub_interface.rfSampleHub):

  def __init__(self, dataBaseFile, MOCK ):
    self.dbfile = dataBaseFile
    
    self.hp8753Mock = vnaHP8753C_GpibMock(Addr=16)
    if MOCK:
      self.hp8753 = self.hp8753Mock
      print ('HP mock :' +str( self.hp8753))
    else:
      try:
        self.hp8753 = self.vnaHP8753C_Gpib(Addr=16, numSamples_=10)
      except:
        print ("Failed to open GPIB device")
        self.hp8753 = None
    self.device = self.hp8753

    filters1 = tables.Filters(complevel=0)
    self.hdStore = hdf5DataTable(filters=filters1, dataBase_=dataBaseFile, restore = True)
    self.dbfile = self.hdStore.filename
    print("MOCK:"+str(MOCK))
    print("DBFile:"+self.dbfile)
    rows = self.hdStore.query('/lab0',"session >0")
    print (type(rows[0]))
    print (len(rows))
    if (len(rows) >0):
      self.maxsess = max([x['session'] for x in rows])
    else:
      self.maxsess = 0
    print ("Max session:" + str(self.maxsess))
    return 

  #
  # cmd:   
  #  print ("Options: Session, Today, LastHour, LastMinutes, Yesterday, All")
  def getDataPlot(self, cmd, param):
    global MAX_GRAPH
    if cmd[0]=='@':
      qstr = cmd[1:]
    else:
      if 'Session' in cmd:
        if param == 0:
            sess = self.maxsess #TODO hdStore.getCurrSess()
        else:
            sess = param
        qstr = "session == %d"%(sess)
      else: #if 'Last' in cmd:
        ts=self.hdStore.getTimeStamp(cmd, param)  
        qstr = "unix_timestamp >= %d"%(param)
      #print ("Debug: using query"+ qstr)
    rows = self.hdStore.query('/lab0',qstr)
    clist = []
    print ("Found %d entries"%(len(rows)))
    grlen= min(MAX_GRAPH, len(rows))
    sp = 0
    for it in rows[:grlen]:
        values = it['sData'] #it[2] #'sData']
        complex_sample = np.empty((201),dtype=complex)
        print("Data type on query:", values.dtype) 
        complex_sample[:] = values[sp,:] + 1j*values[sp+1,:]
        print(complex_sample.shape) 
        print(type(complex_sample[0]))
        clist.append(complex_sample)
    plotMeas(self.hp8753.freqL, clist)
    return

  def startSample(self, experiment_setup):
    dataSamp = self.hp8753.startSample()
#    setUp['concentrate'] = np.random.uniform()
    self.hdStore.writeSamples(dataSamp,'/lab0', experiment_setup)
    return dataSamp
#    complex_sample21 = np.empty((201),dtype=complex)
#    complex_sample11 = np.empty((201),dtype=complex)
#    complex_sample21[:] = dataSamp[0,:] + 1j*dataSamp[1,:]
#    complex_sample11[:] = dataSamp[2,:] + 1j*dataSamp[3,:]
#    plotMeas2('S11', hp8753.freqL, complex_sample21)
#    plotMeas2('S21', hp8753.freqL, complex_sample11)




    
