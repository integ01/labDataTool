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
#sys.path.append("../HDF/")
#from dbHdf5TablesMod_v2_3 import hdf5DataTable
from dbHdf5TablesMod import hdf5DataTable
import guiRpc_pb2

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
def fullTimeLogPostfix():
  now = datetime.datetime.now()
  postfix = now.strftime("%y%m%d_%H%M%S")
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
  global hdStore

  print("Show Sample Params: (TBD)")
  print ("TODO - Add query here")
  hdStore.printData('/lab0')
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

'''
def plotMeasLabels2(w_,X_,X2_, labels):
  w = np.array(w_)
#  X = np.array(X_)
  #cpal = ['skyblue', 'green', 'red', 'yellow', 'black', ']
  cpal = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'indigo', 'gray', 'darkorange']
  #plt.subplot(2,1,1)
  XZ = zip(X_,X2_)
  for i, (X, X2) in enumerate(XZ):
    #magX = np.abs(X);
    magX = 20*np.log10(np.abs(X));

    #print (X)
    plt.subplot(2,1,1)
    plt.plot(w,magX, marker='', color=cpal[i], label = labels[i], linewidth=1)
 #   plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('S21 |H|');
    plt.legend()
    plt.subplot(2,1,2)
  #for i, X in enumerate(X2_):
    #magX = np.abs(X);
    magX2 = 20*np.log10(np.abs(X2));

#    angX = np.angle(X);
    plt.plot(w,magX2, marker='', color=cpal[i], label = labels[i], linewidth=1)
    #plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('S11 |H|');
    plt.legend()
#    plt.title('Phase Response')
  plt.show()
'''

def plotMeasLabelsLog(w_,X_, X2_, labels, sparam):
  w = np.array(w_)
#  X = np.array(X_)
  #cpal = ['skyblue', 'green', 'red', 'yellow', 'black', ']
  cpal = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'indigo', 'gray', 'darkorange']
  plt.subplot(2,1,1)
  plt.ylabel('{} |H|'.format(sparam[0]))
  for i, X in enumerate(X_):
    #magX = np.abs(X);
    magX = 20*np.log10(np.abs(X));
    #print (X)
    plt.plot(w,magX, marker='', color=cpal[i], label = labels[i], linewidth=1)
 #   plt.xlabel('frequency in GHZ units'); 
  plt.legend()
  plt.subplot(2,1,2)
  plt.xlabel('frequency in GHZ units')
  plt.ylabel('{} |H|'.format(sparam[1]))
  for i, X in enumerate(X2_):
    #magX = np.abs(X);
    magX = 20*np.log10(np.abs(X));
    #angX = np.angle(X);
    plt.plot(w,magX, marker='', color=cpal[i], linewidth=1)
    #plt.legend()
#    plt.title('Phase Response')
  #plt.legend()
  plt.show()
 
def plotMeasLabels(w_,X_, labels):
  w = np.array(w_)
#  X = np.array(X_)
  #cpal = ['skyblue', 'green', 'red', 'yellow', 'black', ']
  cpal = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'indigo', 'gray', 'darkorange']
  plt.subplot(2,1,1)
  for i, X in enumerate(X_):
    magX = np.abs(X);
    #print (X)
    plt.plot(w,magX, marker='', color=cpal[i], label = labels[i], linewidth=1)
 #   plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('|H|');
    plt.legend()
  plt.subplot(2,1,2)
  for i, X in enumerate(X_):
    magX = np.abs(X);
    angX = np.angle(X);
    plt.plot(w,angX, marker='', color=cpal[i], linewidth=1)
    plt.xlabel('frequency in GHZ units'); 
    plt.ylabel('Phase response');
    plt.legend()
#    plt.title('Phase Response')
  plt.show()
  

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
  plt.ylabel(title+':20 log |H|');
  plt.subplot(2,1,2)
  plt.plot(w,angX)
  plt.xlabel('frequency in GHZ units'); 
  plt.ylabel(title+': Phase response');
  #plt.title('Phase Response')
  plt.show()

def setEnaParams(paramItems):
  #TODO - Add number of scans
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



########################################################################
# decodeQueryDictR:
#   condDict - Dictionary of query conditions encoded.
#
# 
def decodeQueryDictR( item, name, leading = '( '):
    global hdStore
    global attr
    #print(leading + name + ":")
    res = leading
    for i, (key, valList) in enumerate(item.items()):
        print(leading + key + ":" + str(valList))
        #print(leading + "  {}: {}, {}".format(key, val, type(val)))
        if key[0] == '@':
          params = valList
          tsl = hdStore.parseTimeStamp(key[1:], params)  
          if len(tsl) > 1 :
             res += decodeQueryDictR( {'&': tsl},"")
          else:
             res += " ( {} )".format(tsl[0])
        else:
          for i ,valitem in enumerate(valList):
            if isinstance(valitem, dict):
              tempres = decodeQueryDictR(valitem, key)
            elif isinstance(valitem,str):
                tempres = valitem
            if i!= 0:
              res += " {} ( {} )".format(key, tempres)
            else:
              res += " ( {} ) ".format(tempres)
        #elif isinstance(val, str):
        #    print(leading + "  {}: {}".format(key, val ))
    return res + " )"


############################
# dbQueryExprTblByDict:  query function
# Input:
#        hdStore - Hd5 storage class
#        condDict - query conditions encoded in a dictionary format. 
def dbQueryExprTblByDict(hdStore_, condDict):
      global hdStore
      hdStore = hdStore_
      qstr = decodeQueryDictR( condDict, "ben")
      print (qstr)
      #if cmd[0]=='@':
      #    qstr = cmd[1:]
      #else:
      #    ts=hdStore.getTimeStamp(cmd, parami)  
      #    qstr = "unix_timestamp >= %d"%(ts)
      #    print ("Debug: using query"+ qstr)
      rows = hdStore.query('/lab0/exprTable',qstr)
      print (rows[:])
      print ("Found %d entries"%(len(rows)))
      return rows
############################
# query function
# Input:
#        hdStore - Hd5 storage class
#        cmd - query string in pyTables format (sql like)
#        parami - time index .
def dbQueryExprList(hdStore, cmd, parami ):
      if cmd[0]=='@':
          qstr = cmd[1:]
      else:
          ts=hdStore.getTimeStamp(cmd, parami)  
          qstr = "unix_timestamp >= %d"%(ts)
          print ("Debug: using query"+ qstr)
      rows = hdStore.query('/lab0/exprTable',qstr)
      print (rows[:])
      print ("Found %d entries"%(len(rows)))
      return rows

############################
# query function
# Input:
#        hdStore - Hd5 storage class
#        cmd - query string in pyTables format (sql like)
#        sp - Sparam to display
def dbQuery(hdStore, cmd, parami, sp):
      if cmd[0]=='@':
          qstr = cmd[1:]
      else:
          ts=hdStore.getTimeStamp(cmd, parami)  
          qstr = "unix_timestamp >= %d"%(ts)
          print ("Debug: using query"+ qstr)
      rows = hdStore.query('/lab0/exprTable',qstr)
      print (rows[:])
      print ("Found %d entries"%(len(rows)))
      grlen= min(3, len(rows))
      print ("Plotting %d entries"%(grlen))
      dL = []
      clist = []
      for i in range(grlen):
        datapath = rows.loc[i]['dataArrRef'].decode()
        print (datapath)
        darray = hdStore.getDataByRef(datapath)
        print (darray.shape, darray.dtype)
        print (darray.attrs.sparamOffset)
        freqL = darray.attrs.ff
        dL.append(darray)
      for data in dL:
        complex_sample = np.squeeze(data[0, :, sp]) #'sData']
        #print("Data type on query:", values.dtype) 
        #complex_sample[:] = values[sp,:] + 1j*values[sp+1,:]
        print(complex_sample.shape) 
        print(type(complex_sample[0]))
        clist.append(complex_sample)
      return ( freqL, clist)

def measureRemoteCall(rpcClient,  enaSetup, setUp, hdStore=None, plot=False):
      # ['Meas_id', 'ENADataMode', 'NPoints', 'fSTAR', 'fSTOP', 'fCENT', 'fSPAN',
      # 'dFormat', 'S11', 'S21', 'S12', 'S22' ]
        #enaP = setEnaParams( [0, 1, 801, 1e9, 2e9, 1.5e9, 1e9, 0, 1, 2, -1, -1])
        
        enaSetup['Meas_id'] =  enaSetup['Meas_id'] + 1
        print (enaSetup)
        dataSamps, ffs, sampsIDs = rpcClient.lab_start_sample(enaParams=enaSetup)

        numPoints = dataSamps[0].shape[0]//2
        print("ff len:",ffs[0].shape)
        print("numPoints: {}".format(numPoints))
        print (dataSamps[0].shape)
        print ("Reply Meas_id, S_type :{}".format(sampsIDs[0]))
        complexSamples11 = []
        complexSamples21 = []
        complexSamples12 = []
        complexSamples22 = []
        ######## TODO - checkmeasID and S_type match request ena  
       # setUp['concentrate'] = np.random.uniform()
        for samp, sampId in zip(dataSamps, sampsIDs):
          if sampId[1] == guiRpc_pb2.SampleArray.S11:
             complexSamples11.append( np.array((samp[0::2] + 1j*samp[1::2]),dtype=np.complex128) )
          if sampId[1] == guiRpc_pb2.SampleArray.S21:
             complexSamples21.append( np.array((samp[0::2] + 1j*samp[1::2]),dtype=np.complex128) )
          if sampId[1] == guiRpc_pb2.SampleArray.S12:
             complexSamples12.append( np.array((samp[0::2] + 1j*samp[1::2]),dtype=np.complex128) )
          if sampId[1] == guiRpc_pb2.SampleArray.S22:
             complexSamples22.append( np.array((samp[0::2] + 1j*samp[1::2]),dtype=np.complex128) )
        offsetS21 = 0 if len(complexSamples11)>0 else -1
        offSum = len(complexSamples11)
        offsetS11 = offSum if len(complexSamples21)>0 else -1
        offSum += len(complexSamples21)
        offsetS12 = offSum if len(complexSamples12)>0 else -1
        offSum += len(complexSamples12)
        offsetS22 = offSum if len(complexSamples22)>0 else -1
        offSum += len(complexSamples22)

        print ("samplesS11 #:{}".format( len(complexSamples11)))
        print ("samplesS21 #:{}".format( len(complexSamples21)))
        print ("samplesS12 #:{}".format( len(complexSamples12)))
        print ("samplesS22 #:{}".format( len(complexSamples22)))
        complexSamples = complexSamples11 +  complexSamples21 +  complexSamples12 +  complexSamples22
        samplesOffIndex = {"S11":  offsetS11, "S21": offsetS21, 
        "S12":  offsetS12, "S22": offsetS22 }
                         
        ndarry = {'raw': (np.vstack(complexSamples).transpose()), 'ff': ffs[0], 'offset':samplesOffIndex }
        print (ndarry['raw'].shape)
        ###### TODO - add connection to db
        if hdStore != None:
          hdStore.aggParams2TableWrite(setUp, ndarry, enaSetup, grp='/lab0') 

        #TODO - add this to the read fields
        #freqL = np.linspace(2e+9,3e+9,201)
        if plot == True:
            print ("Ploting: {}".format(plot))
            plotMeas2('S11', ffs[0], complexSamples[samplesOffIndex["S11"]])
            plotMeas2('S21', ffs[0], complexSamples[samplesOffIndex["S21"]])

#        plotMeas2('S21', ffs[0], complexSamples[1])


def measureRemoteCall_0(rpcClient):
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
  print ("3. VNA commad setup")
  print ("4. Start Sample")
  print ("5. Query & Plot Data")
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
  global gEna

  while (1):
    printUsageSelect()
    try:
      cmds = []
   
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
         filepath = input ("Enter Date Base name(Default=%s)"%(dataBaseName))
         if filepath == '':
            filepath = dataBaseName
         filters1=tables.Filters(complevel=0)
         hdStore = hdf5DataTable(filters=filters1, dataBase_=filepath, restore=True)
         #hdClient = hdf5Client(filepath, filters1)
      elif ( cmd[0] == '2'):
        showSampleParams()
      elif ( cmd[0] == '6'):
        filepath = input ("Enter Sample Parameters file name:")
        cmds = loadScript(filepath)
      elif ( cmd[0]=='3'):
        cmd = input ("Enter Command for Vna:")
        res = rpcClient.lab_send_cmd(cmd)
        print ("Result of command:" + res)

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

        # TODO - get S21/S11 measurments correct offsets
        plotMeas2('S11', ffs[0], complexSamples[0])
        plotMeas2('S21', ffs[0], complexSamples[1])

#        countItems += 1
#        writeOps += 1
      elif ( cmd[0] == '7'):
        test_db(hdStoreM, 100)
      
      elif ( cmd[0] == '5'):
        print ("Options: Today, LastHour, LastMinutes, Yesterday, All")
        cmd = input ("Enter query for DB items (for raw cmd use '@' prefix):")
        parami = 0
        if len(cmd)== 0:
          cmd='All'
        else:
          if 'Last' in cmd:
            param = input ("Enter how many:")
            parami = int(param)
        splot = input("Select 1- S11, 2- S21 :")
        try:
          sp = int(splot) -1
        except ValueError:
          print ("Wrong value -- using Option 1 ")
          sp = 0
        if (sp != 0 and sp !=1):
          print ("Wrong value -- using Option 1 ")
          sp = 0
        freqL, clist = dbQuery(hdStore, cmd, parami, sp)
        plotMeas(freqL, clist)
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
  
  
  if hasattr(__builtins__, 'raw_input'): 
   input = raw_input
  logging.basicConfig()
  gEna = setEnaParams( [0, 1, 801, 1e9, 2e9, 1.5e9, 1e9, 0, 1, 1,0,0])
  rpcClient = labDataToolClient.clientRpcAPI('192.168.1.102:50051')
  main(rpcClient)

#  condD = { "&" : ["unix_timestamp >= 100000", "unix_timestamp < 200000"]}
#  condD2 = { "|": ["P1 > 50", {"&" : ["unix_timestamp >= 100000", "unix_timestamp < 200000"]}, "component0='Nacl'"] }

