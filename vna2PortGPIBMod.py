
#import  sched,time
#import  schedule
#from timeloop import Timeloop
from datetime import timedelta
import threading, time 
import visa
import numpy as np
#import pdb

TIMEOUT = 3.0#0.8805
valuesList1 = []
valuesList2 = []
SAMPLES = 10
count = 0
#tl = Timeloop()
INST = None

def measureSweepAscii():
  inst.write('FORM4')
  st=time.time()
  inst.query('OPC?;SING;')
  inst.write('OUTPFORM')
  values = inst.read_bytes(2048)
  en=time.time()
  print ("Number of values read:{0}".format( len(values)) )
  return (en-st)

def measureSweepBinary():
  inst.write('FORM3')
  st=time.time()
  inst.query('OPC?;SING;')
  inst.write('OUTPFORM')
  values = inst.query_binary_values( 'OUTPFORM',datatype='d', header_fmt='hp', is_big_endian=True)
  en=time.time()
  print ("Number of values read:{0}".format( len(values)) )
  return (en-st)

#@tl.job(interval=timedelta(seconds=TIMEOUT))
def samplePoints():
  global TIMEOUT
  global count

  count -=1
  # Sample data
  inst.query('OPC?;SING;')
  values = inst.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  valuesList1.append(values)
  print ("{0}: Add Sample, time {1}".format(numSamples-count, time.time()) )
 

#@tl.job(interval=timedelta(seconds=TIMEOUT))
def twoPortSample():
  global valuesList1
  global valuesList2
  global count
  global INST
  
  # Sample data
  INST.query('OPC?;SING;')
  count -=1
  values2 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  INST.write('CHAN1')
  values1 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  INST.write('CHAN2')

  valuesList1.append(values1)
  valuesList2.append(values2)
  print ("{0}: Add Sample, time {1:f}".format(SAMPLES-count, time.time()) )

 
def onePortMultiSample():
  global valuesList1
  global valuesList2
  global count
  global INST
  
  # Sample data
  INST.query('OPC?;SING;')
  count -=1
  values2 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  #INST.write('CHAN1')
  time.sleep(0.1) #TODO - is this needed?
  INST.write("CHAN2")
  INST.write('S11')
  INST.query('OPC?;SING;')
  values1 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  INST.write("CHAN2")
  INST.write('S21')


  valuesList1.append(values1)
  valuesList2.append(values2)
  print ("{0}: Add Sample, time {1:f}".format(SAMPLES-count, time.time()) )


def orderValues2(val):
  re = [ val[i*2] for i in range(len(val)//2)  ]
  im = [ val[i*2+1] for i in range(len(val)//2)  ]
  return re, im


class vnaHP8753C_Gpib:
  global count

  def __init__(self, Addr = 16, numSamples_= SAMPLES):
       global INST
       try:
         self.rm = visa.ResourceManager('@py')
         self.inst = self.rm.open_resource('GPIB0::{}::INSTR'.format(Addr))
       except:
         print ("Error - Failed to open GPIB Interface")
         raise AssertionError
       INST = self.inst
       idStr = self.inst.query("*IDN?")
       print ("Open Device : " + idStr)
       self.inst.write("POIN?;")
  #TODO-set points to 128
       pointStr = self.inst.read() #"POIN {0};".format(numpoints)
       print ("Number of Point to Read Per Sample: ", pointStr)
       try:
        self.nPoints =  float(pointStr)
       except:
          print ("Points string conversion error")
       # Get Frequency list
       self.inst.write("OUTPLIML;")
       self.inst.write('FORM3')
       freqStr = self.inst.read_raw()
       freqStr = freqStr.replace('\n', ', ')
       freqLst = freqStr.split(",")
       freqLst = freqLst[:-1]
       #print (freqLst)
       self.freqL = [ float(freqLst[i*4]) for i in range(len(freqLst)//4)]
#       self.count = numSamples_
       self.numSamples = numSamples_

#       self.twoPortSetup()
       self.onePortMultiSetup()

  def twoPortSetup(self):
    self.inst.write("CHAN1")
    self.inst.write('S11')
    self.inst.write("CHAN2")
    self.inst.write('S21')
    self.inst.write('FORM3')
    self.inst.write('STAR2GHZ')

  def onePortMultiSetup(self):
   # self.inst.write("CHAN1")
   # self.inst.write('S11')
    self.inst.write("CHAN2")
    self.inst.write('S21')
    self.inst.write('FORM3')
    self.inst.write('STAR2GHZ')

  def setFreqList(self, nPoints):

    print ("Set FreqList")
#    pdb.set_trace()
    self.inst.write("POIN?;")
  #TODO-set points 
    pointStr = self.inst.read()#"POIN {0};".format(numpoints)
    print ("Number of Point to Read Per Sample: ", pointStr)

  # Get Frequency list
    self.inst.write("OUTPLIML;")
    self.inst.write('FORM3')
    time.sleep(1)
    freqStr = self.inst.read_raw()
    freqStr = freqStr.replace('\n', ', ')
    freqLst = freqStr.split(",")

    self.freqL = [ float(freqLst[i*4]) for i in range(len(freqLst)/4)]
    print ("Freq start:{}, end:{}".format(freqLst[0], freqLst[-1]))
    return self.freqL


  #print("FreqL",len(compVal2))
  #plotMeas2('S21', freqL, compVal2)
  #plotMeas2('S11', freqL, compVal1)


#########################
#   def startSample()
#
  def startSample(self, nPoints=201):
    global count
    global valuesList1
    global valuesList2
    
    if self.nPoints != nPoints: 
      self.setFreqList(nPoints)
      self.nPoints = nPoints
    count = self.numSamples
    valuesList1 = []
    valuesList2 = []

    print ("Number of Samples to Read :", self.numSamples)
    '''
    tl.start(block=False)
    while (count>0):
      time.sleep(0.5) 
    tl.stop()
    '''
    tick = threading.Event()
    while not tick.wait(TIMEOUT):
       if count > 0:
          #twoPortSample()
          onePortMultiSample()
       else: break

    print("\nStop Scheduler --> Going to average data")
    if len(valuesList1)  == 0:
      print ("Error - No samples collected")
      return None
    else: 
      print ("Got samples {0}, array size: {0}".format( len(valuesList1), 
       len(valuesList1[0]) ) )
#      print ("Got samples array shape: {0}".format(valueist2[0].shape))
     
      print ("Done\n-----")
      #cmd = raw_input ("<< Press Enter to continue to plot graph >> ")
      valarr1 = [ np.array((valItem)) for valItem in valuesList1]
      valarr2 = [ np.array((valItem)) for valItem in valuesList2]
      print ("Got samples value array shape: {0}".format(valarr1[0].shape))
  
      return valarr1 + valarr2
#      return np.vstack((sampAvg, sampAvgj, sampAvg2, sampAvg2j))
 #     plotMeas2('S21', freqL, sampAvg)
 #     plotMeas2('S11', freqL, sampAvg2)


