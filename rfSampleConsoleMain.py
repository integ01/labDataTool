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
### Unix time : time.time()
### Unix to regular : datetime.datetime.fromtimestamp(1172969203.1)
#### datetime.datetime(2007, 3, 4, 2, 46, 43, 100000)

setUp = {
  'time' : None,
  'freqSt': '2GHZ',
  'freqEn': '3GHZ',
  'material' : 'water',
  'concentrate' : 0.8
}

logBaseName = "sampleData"
LOCATIONS = ['lab0']
MATERIALS = ['H2O', 'Air']
SAMPLE_SHAPE = (2,100)
MAX_SESS_SAMPLES = 100
MOCK = True

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



#complib, codec = 'blosc', 'zstd'
#complevel = 6
#filename = "%s/pokemons-%s-%s-%d.h5" % (data_dir, complib, codec, complevel)
#with pd.HDFStore(filename, mode='w') as hdf:
# We only index the columns needed
#    hdf.put(key='pokemons', value=df, data_columns=['target', 'latitude', 'longitude'],
#            format='table', complevel=complevel, complib="%s:%s" % (complib, codec))
  

#def sampleData(grp, setUp):
#    global logBaseName
#    
#    paramDict = setUp
#    paramDict['Date'] = int(time.time())
#    grp2 = grp.create_group('Sess'+   unixTimePostfix(paramDict['Date']) )
#    grp2.attrs.update(paramDict)
#
#    storeData = grp2.create_dataset('sampleSet', (SAMPLE_SHAPE[0], SAMPLE_SHAPE[1], 1),  maxshape=(SAMPLE_SHAPE[0], SAMPLE_SHAPE[1], MAX_SESS_SAMPLES ))
    # Mock Storing of data
#    storeData[:,:,0] = np.random.randn(2,100)
#    for i in range(random.random(10)):
#       storeData[:,:,i+1] = np.random.randn(2,100)
#   
#    return

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

def main():

  global MOCK
  global hdStore
  global hp8753
  global hp8753Mock

  hp8753Mock = vnaHP8753C_GpibMock(Addr=16)
  if MOCK:
    hp8753 = hp8753Mock 
  else:
    hp8753 = vnaHP8753C_Gpib(Addr=16, numSamples_=10)

  while (1):
    printUsageSelect()
    try:
      cmds = []
      cmd = raw_input ("term>")
      if len(cmd) == 0:
         continue
#      cmd = input ("term>")
      if ( cmd[0] == '8'):
         filepath = raw_input ("Enter New Date Base name(Default=%s)"%(dataBaseName))
         if filepath == '':
            filepath = dataBaseName
         filters1 = tables.Filters(complevel=0)
         hdStore = hdf5DataTable(filters=filters1, dataBase_=filepath)
         #hdStore.createH5DataBase(filepath, LOCATIONS) 
      elif ( cmd[0] == '1'):
         filepath = raw_input ("Enter Date Base name(Default=%s)"%(dataBaseName))
         if filepath == '':
            filepath = dataBaseName
         filters1=tables.Filters(complevel=0)
         hdStore = hdf5DataTable(filters=filters1, dataBase_=filepath, restore=True)
      elif ( cmd[0] == '2'):
        showSampleParams()
      elif ( cmd[0] == '6' or cmd[0]=='3'):
        filepath = raw_input ("Enter Sample Parameters file name:")
        cmds = loadScript(filepath)
      elif ( cmd[0] == '4'):
        dataSamp = hp8753.startSample()
        setUp['concentrate'] = np.random.uniform()
        hdStore.writeSamples(dataSamp,'/lab0', setUp) 
        complex_sample21 = np.empty((201),dtype=complex)
        complex_sample11 = np.empty((201),dtype=complex)
        complex_sample21[:] = dataSamp[0,:] + 1j*dataSamp[1,:]
        complex_sample11[:] = dataSamp[2,:] + 1j*dataSamp[3,:]
        plotMeas2('S11', hp8753.freqL, complex_sample21)
        plotMeas2('S21', hp8753.freqL, complex_sample11)

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
  main()

