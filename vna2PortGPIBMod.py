
#import  sched,time
#import  schedule
#from timeloop import Timeloop
from datetime import timedelta
import threading, time 
import visa
import numpy as np


TIMEOUT = 3.0#0.8805
complex_sample_list = []
complex_sample_listj = []
complex_sample_list2 = []
complex_sample_list2j = []
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
  global complex_sample_list
  global TIMEOUT
  global count

  count -=1
  # Sample data
  inst.query('OPC?;SING;')
  values = inst.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  #complex_sample_list.append( np.array([ values[i*2]+ 1j*values[i*2+1] for i in range(len(values)/2)]) )
  complex_sample_list.append([ values[i*2]+ 1j*values[i*2+1] for i in range(len(values)/2)])
  print ("{0}: Add Sample, time {1}".format(numSamples-count, time.time()) )
 

#@tl.job(interval=timedelta(seconds=TIMEOUT))
def twoPortSample():
  global complex_sample_list
  global complex_sample_listj
  global complex_sample_list2
  global complex_sample_list2j
  global count
  global INST
  
  # Sample data
  INST.query('OPC?;SING;')
  count -=1
  values2 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  INST.write('CHAN1')
  values1 = INST.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
  INST.write('CHAN2')

  complex_sample_list.append([ values1[i*2] for i in range(len(values1)/2)])
  complex_sample_listj.append([ values1[i*2+1] for i in range(len(values1)/2)])
  complex_sample_list2.append([ values2[i*2] for i in range(len(values2)/2)])
  complex_sample_list2j.append([ values2[i*2+1] for i in range(len(values2)/2)])
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
 
       # Get Frequency list
       self.inst.write("OUTPLIML;")
       self.inst.write('FORM3')
       freqStr = self.inst.read_raw()
       freqStr = freqStr.replace('\n', ', ')
       freqLst = freqStr.split(",")
       freqLst = freqLst[:-1]
       #print (freqLst)
       self.freqL = [ float(freqLst[i*4]) for i in range(len(freqLst)//4)]
       self.complex_sample_list = None #np.array(None)
#       self.count = numSamples_
       self.numSamples = numSamples_
       self.twoPortSetup()

  def twoPortSetup(self):
    self.inst.write("CHAN1")
    self.inst.write('S11')
    self.inst.write("CHAN2")
    self.inst.write('S21')
    self.inst.write('FORM3')
    self.inst.write('STAR2GHZ')

  def getFreqList(self):
  # Get Frequency list
    self.inst.write("OUTPLIML;")
    self.inst.write('FORM3')
    freqStr = inst.read_raw()
    freqStr = freqStr.replace('\n', ', ')
    freqLst = freqStr.split(",")

    freqL = [ float(freqLst[i*4]) for i in range(len(freqLst)/4)]
    return freqL


  #print("FreqL",len(compVal2))
  #plotMeas2('S21', freqL, compVal2)
  #plotMeas2('S11', freqL, compVal1)


#########################
#   def startSample()
#
  def startSample(self):
    global count
    global complex_sample_list
    global complex_sample_listj
    global complex_sample_list2
    global complex_sample_list2j

    count = self.numSamples
    complex_sample_list = []
    complex_sample_listj = []
    complex_sample_list2 = []
    complex_sample_list2j = []

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
          twoPortSample()
       else: break

    print("\nStop Scheduler --> Going to average data")
    if len(complex_sample_list)  == 0:
      print "Error - No samples collected"
      return None
    else: 
      sample_arr =  np.array(complex_sample_list)
      print ("Got samples array shape: {0}".format(sample_arr.shape))
      sampAvg = np.mean(sample_arr, axis=0)
      sample_arrj =  np.array(complex_sample_listj)
      sampAvgj = np.mean(sample_arrj, axis=0)
      
      sample_arr2 =  np.array(complex_sample_list2)
      print ("Got samples array shape: {0}".format(sample_arr2.shape))
      sampAvg2 = np.mean(sample_arr2, axis=0)
      sample_arr2j =  np.array(complex_sample_list2j)
      sampAvg2j = np.mean(sample_arr2j, axis=0)
     
      print ("Done\n-----")
      cmd = raw_input ("<< Press Enter to continue to plot graph >> ")
   
      return np.vstack((sampAvg, sampAvgj, sampAvg2, sampAvg2j))
 #     plotMeas2('S21', freqL, sampAvg)
 #     plotMeas2('S11', freqL, sampAvg2)


