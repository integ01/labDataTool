########################################################
#
#
#
#  TODO - 
# 31-Oct-2019 Add field freqList to database

import h5py
import numpy as np

import tables
import time
import datetime
import os

import logging
import labDataToolClient
import sys
sys.path.append("../HDF/")
#from dbHdf5TablesMod import hdf5DataTable
from dbHdf5TablesMod_v2_3 import hdf5DataTable
from dbHdf5TablesMod_v2_3 import hdf5Client

import matplotlib.pyplot as plt
### Unix time : time.time()
### Unix to regular : datetime.datetime.fromtimestamp(1172969203.1)
#### datetime.datetime(2007, 3, 4, 2, 46, 43, 100000)


#
setUp = {
  #'time' : None,
  'session': 0,
  'author': 'ben',
  'title' : 'water and Nacl',
  'experimentOK' : 1,
  'volume' :  100, 
  'numberOfMeasurements' : 5,
  'measurmentNumber' : 1,
  'numberOfComponents' : 2,
  'component0' : 'water',
  'component1' : 'Nacl',
  'P0_volume' : 100,
  'P1' : 22
}

logBaseName = "sampleData"
LOCATIONS = ['lab0']
MATERIALS = ['H2O', 'Air']
SAMPLE_SHAPE = (2,100)
MAX_SESS_SAMPLES = 100
MOCK = True


dataBaseName = "dataFile0"

def unixTimePostfix(time):
  now = datetime.datetime.fromtimestamp(time)
  postfix = now.strftime("%d_%H%M%S")
  return postfix

def timeLogPostfix():
  now = datetime.datetime.now()
  postfix = now.strftime("%d_%H%M%S")
  return postfix


def test_db(hdStore, numOper):
  global hp8753Mock
  if hdStore == '':
    filters1 = tables.Filters(complevel=0)
    hdStore = hdf5DataTable(filters=filters1)
  countItems = 0
  writeOps = 0
  rmOps = 0
  st = time.time()
  for x in range(numOper):
    oper = np.random.randint(1,10)
    if oper > 1:
      dataSamp = hp8753Mock.startSample()  
      #TODO fix this
      setUp['concentrate'] = np.random.uniform()
      hdStore.writeSamples(dataSamp,'/lab0', setUp) 
      countItems += 1
      writeOps += 1
    elif countItems > 10:
#      delta = removeDataRnd(file1, "/lab0")
      hdStore.removeSamples('/lab0') 
      countItems -= 1
      rmOps += 1
  en = time.time()
  hdStore.printData( "/lab0", setUp )
  print("Number of Writes:%d"%(writeOps))
  print("Numer of deletes:%d"%(rmOps))
  print("Total Time:%4.3f sec"%(en-st))
  return


def showSampleParams():
  global setUpParam
  global hdStore

  print("Show Sample Params: (TBD)")
  print ("TODO - Add query here")
  hdStore.printData('/lab0', setUp)
#  for it in setUpParam.items():
#    print (it)
  return

#####################
# loadScript()
#Load script from file path , filter out '# comment lines
def loadScript(input_file_path):
    f=open(input_file_path,"r")
    inData =list(f.readlines())
    f.close()
    return list(filter(lambda x: x[0] != '#' and x[0] != '!' and x[0] != '/' and x[0]!='\n', inData))
    
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

def setEnaParams(paramItems):
  enaParamKeys = ['Meas_id', 'ENADataMode', 'NumOfPoints', 'freq_STAR',
                     'freq_STOP', 'freq_CENT', 'freq_SPAN', 'dataFormat', 
                      'S11', 'S21', 'S12', 'S22' ]
  enaP = {}
  if len(paramItems) != len(enaParamKeys):
     print ("set Ena Params Error: List length mishmatch")
     return 
  for key, item  in zip(enaParamKeys, paramItems):
       enaP[key] = item
  return enaP

def measureRemoteCall(rpcClient):
        dataSamps, ffs = rpcClient.lab_start_sample()
        #setUp['concentrate'] = np.random.uniform()
        #hdStore.writeSamples(np.vstack(dataSamps),'/lab0', setUp) 
        complex_sample21 = np.empty((201),dtype=complex)
        complex_sample11 = np.empty((201),dtype=complex)
        complex_sample21[:] = (dataSamps[0])[0::2] + 1j*(dataSamps[0])[1::2]
        complex_sample11[:] = (dataSamps[1])[0::2] + 1j*(dataSamps[1])[1::2]
        #TODO - add this to the read fields
        #freqL = np.linspace(2e+9,3e+9,201)
        plotMeas2('S11', ffs[0], complex_sample21)
        plotMeas2('S21', ffs[0], complex_sample11)


def printUsageSelect():
  print ("=======================")
  print ("1. Open Existing DataBase ")
  print ("2. Get Data from Database ")
  print ("3. VNA setup (TBD)")
  print ("4. Start Sample")
  print ("5. Plot Data")
  print ("6(TBD). Run Test Script and Save data")
  print ("7. Test DB")
  print ("8. Start New DataBase ")
  print ("9. Quit")
  print ("Otherwise enter command")
  print ("\n=======================")
  print("\nEnter selection (1,2, 3 or command)")


def main(rpcClient):

  global MOCK
  global hdStore
  global hdClient


  while (1):
    global gEna
    printUsageSelect()
    try:
      cmds = []
      #cmd = raw_input ("term>")
      cmd = input ("term>")
      if len(cmd) == 0:
         continue
#      cmd = input ("term>")
      if ( cmd[0] == '8'):
         filepath = input ("Enter New Date Base name(Default=%s)"%(dataBaseName))
         if filepath == '':
            filepath = dataBaseName
         filters1 = tables.Filters(complevel=0)
         hdStore = hdf5DataTable(filters=filters1, dataBase_=filepath)
         #hdClient = hdf5Client(filepath, filters1)
         ##hdStore.createH5DataBase(filepath, LOCATIONS) 
      elif ( cmd[0] == '1'):
         #filepath = raw_input ("Enter Date Base name(Default=%s)"%(dataBaseName))
         filepath = input ("Enter Date Base name(Default=%s)"%(dataBaseName))
         if filepath == '':
            filepath = dataBaseName
         filters1=tables.Filters(complevel=0)
         hdStore = hdf5DataTable(filters=filters1, dataBase_=filepath, restore=True)
         #hdClient = hdf5Client(filepath, filters1)
      elif ( cmd[0] == '2'):
        showSampleParams()
      elif ( cmd[0] == '6' or cmd[0]=='3'):
        filepath = raw_input ("Enter Sample Parameters file name:")
        cmds = loadScript(filepath)
      elif ( cmd[0] == '4'):
      # ['Meas_id', 'ENADataMode', 'NPoints', 'fSTAR', 'fSTOP', 'fCENT', 'fSPAN',
      # 'dFormat', 'S11', 'S21', 'S12', 'S22' ]
        #enaP = setEnaParams( [0, 1, 801, 1e9, 2e9, 1.5e9, 1e9, 0, 1, 2, -1, -1])
        
        gEna['Meas_id'] =  gEna['Meas_id'] + 1
        print (gEna)
        dataSamps, ffs, sampsIDs = rpcClient.lab_start_sample(gEna)
#        dataSamp = hp8753.startSample()
        

        numPoints = dataSamps[0].shape[0]//2
        print("ff len:",ffs[0].shape)
        print("numPoints: {}".format(numPoints))
        print (dataSamps[0].shape)
        print ("Reply Meas_id, S_type :{}".format(sampsIDs[0]))

        ######## TODO - checkmeasID and S_type match request ena  
       # setUp['concentrate'] = np.random.uniform()

#        hdStore.writeSamples(np.vstack(dataSamps),'/lab0', setUp) 
        complexSamples = [ np.array((samp[0::2] + 1j*samp[1::2])) for samp
            in dataSamps]

        ndarry = {'raw': (np.vstack(complexSamples).transpose()), 'ff': ffs[0]}
        hdStore.aggParams2TableWrite(setUp, ndarry, gEna, grp='/lab0') 

#        complex_sample21 = np.empty((numPoints),dtype=complex128)
#        complex_sample11 = np.empty((numPoints),dtype=complex128)
#        complex_sample21[:] = (dataSamps[0])[0::2] + 1j*(dataSamps[0])[1::2]
#        complex_sample11[:] = (dataSamps[1])[0::2] + 1j*(dataSamps[1])[1::2]
        #TODO - add this to the read fields
        #freqL = np.linspace(2e+9,3e+9,201)
        plotMeas2('S11', ffs[0], complexSamples[0])
        plotMeas2('S21', ffs[0], complexSamples[1])

#        countItems += 1
#        writeOps += 1
      elif ( cmd[0] == '7'):
        test_db(hdStoreM, 100)
      elif ( cmd[0] == '5'):
        parami = 0
        print ("Options: Today, LastHour, LastMinutes, Yesterday, All")
        cmd = raw_input ("Enter query for DB items (for raw cmd use '@' prefix):")
        if cmd[0]=='@':
          qstr = cmd[1:]
        else:
          if 'Last' in cmd:
            param = input ("Enter how many:")
            parami = int(param)
          ts=hdStore.getTimeStamp(cmd, parami)  
          qstr = "unix_timestamp >= %d"%(ts)
        #print ("Debug: using query"+ qstr)
          rows = hdStore.query('/lab0',qstr)
          clist = []
          print ("Found %d entries"%(len(rows)))
          grlen= min(3, len(rows))
          print ("Plotting %d entries"%(grlen))
          splot = raw_input("Select 1- S11, 2- S21 :")
          try:
            sp = int(splot) -1
          except ValueError:
            print ("Wrong value -- using Option 1 ")
            sp = 0
          if (sp != 0 and sp !=1):
            print ("Wrong value -- using Option 1 ")
            sp = 0
          for it in rows[:grlen]:
            values = it[2] #'sData']
            complex_sample = np.empty((201),dtype=complex)
            print("Data type on query:", values.dtype) 
            complex_sample[:] = values[sp,:] + 1j*values[sp+1,:]
            print(complex_sample.shape) 
            print(type(complex_sample[0]))
            clist.append(complex_sample)
          plotMeas(hp8753.freqL, clist)
      elif ( cmd[0] == '9'):
         print("====== Quiting =========")
         return
      else:
        cmds = [cmd]

      for cm in cmds:
#filte        inst.write(cm)
        print ("Wrtings cmd:", cm)
        time.sleep(0.1)
    except KeyboardInterrupt:
      print("KeyboardInterrupt has been caught.")
      printUsageSelect()


if __name__ == '__main__':  # You should keep this line for our auto-grading code.
  logging.basicConfig()
  gEna = setEnaParams( [0, 1, 801, 1e9, 2e9, 1.5e9, 1e9, 0, 1, 1,0,0])
  rpcClient = labDataToolClient.clientRpcAPI()
  main(rpcClient)

