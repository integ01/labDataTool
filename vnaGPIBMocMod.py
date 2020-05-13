
import  sched,time
#import visa
#import matplotlib.pyplot as plt
import numpy as np


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



def orderValues(val):
 re = []
 im = []
 print (len(val)//2)
 for i in range(len(val)//2):
   re.append(val[i*2])
   im.append(val[i*2+1])
 return re, im

def orderValues2(val):
  re = [ val[i*2] for i in range(len(val)//2)  ]
  im = [ val[i*2+1] for i in range(len(val)//2)  ]
  return re, im

def plotMeas(w_,X_):
  w = np.array(w_)
  X = np.array(X_)
  magX = np.abs(X);
  angX = np.angle(X);
  plt.subplot(2,1,1)
  plt.plot(w,magX)
  plt.xlabel('frequency in GHZ units'); 
  plt.ylabel('|H|');
  plt.subplot(2,1,2)
  plt.plot(w,angX)
  plt.xlabel('frequency in GHZ units'); 
  plt.ylabel('Phase response');
  plt.title('Phase Response')
  plt.show()

class instMock:
   def __init__(self):
     self.cmd = ''
     self.nPoints = 201
     self.freqStart =  2000*1e+6
     self.freqStop =  3000*1e+6
   def query(self, cmd):
     return '' 
   def write(self, cmd):
     if 'STAR' in cmd:
       sublist = cmd[5:].split(".") 
       try:
          self.freqStart = int(sublist[0])*1e+6
          self.cmd = cmd
       except:
          print ("Couldn't Parse STAR command")
     if 'STOP' in cmd:
       sublist = cmd[5:].split(".") 
       try:
          self.freqStop = int(sublist[0])*1e+6
          self.cmd = cmd
       except:
          print ("Couldn't Parse STAR command")

     if 'FORM3' not in cmd:
       self.cmd = cmd
#       print ('Debug: write :' + cmd)
     return
 
   def read(self, d=''):
     if 'POIN?' in self.cmd:
        self.cmd = ''
        return str(self.nPoints)
     else: 
        self.cmd = ''
        return ''
 
   def read_raw(self, cmd=''):
     if 'OUTPLIML' in self.cmd:
        freqList = [ self.freqStart+k*(self.freqStop-self.freqStart)/(self.nPoints-1) for k in range(self.nPoints)]
        fstr = ''
        for it in freqList:
          fstr += str(it) +', 0, 0, 0 \n'
        #print("Debug:"+ fstr)
        return fstr

   def query_binary_values( self, cmd ,datatype='d', header_fmt='hp', is_big_endian=True):
        values = np.random.rand(self.nPoints) 
        exp = np.array([ 10**(np.random.randint(-2,8)) for i in range(self.nPoints)])
        values *= exp
        phi = (np.random.rand(self.nPoints) -0.5)* 6 *np.pi 
#        print (phi)
        finval = np.empty((self.nPoints*2))
        print (finval.shape)
        for i in range(len(values)):
          finval[i*2] = values[i] * np.cos(phi[i])
          finval[i*2+1] = values[i] * np.sin(phi[i])
        return finval

class vnaHP8753C_GpibMock:

  def __init__(self, Addr = 16):
       self.rm = None #visa.ResourceManager('@py')
       self.inst = instMock() #rm.open_resource('GPIB0::{}::INSTR'.format(Addr))
       self.setFreqList(201)

  def setFreqList(self, nPoints): 
       self.inst.write("POIN?;")
  #TODO-set points to 128
       pointStr = self.inst.read()#"POIN {0};".format(numpoints)
       print ("Number of Point to Read Per Sample: ", pointStr)
       print( "POIN {0};".format(self.inst.nPoints))

       # Get Frequency list
       self.inst.write("OUTPLIML;")
       self.inst.write('FORM3')
       freqStr = self.inst.read_raw()
       print (freqStr)
       freqStr = freqStr.replace('\n', ', ')
       freqLst = freqStr.split(",")
       freqLst = freqLst[:-1]
       #print (freqLst)
       self.freqL = [ float(freqLst[i*4]) for i in range(len(freqLst)//4)]
       self.complex_sample_list = None #np.array(None)
       print ("DEBUG start freq:{: .0f}".format(self.freqL[0]))

  def samplePoints(self, nPoints ):
    global complex_sample_list
    self.inst.query('OPC?;SING;')
    self.inst.write('FORM3')
    if nPoints > 0: 
      self.inst.nPoints = nPoints
    self.setFreqList(nPoints)
    values = self.inst.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
    values2 = self.inst.query_binary_values( 'OUTPDATA',datatype='d', header_fmt='hp', is_big_endian=True)
    #return np.vstack((values,values2))
#    complex_sample_list.append( np.array([ values[i*2]+ 1j*values[i*2+1] for i in range(len(values)//2)]) )
#    new = np.array([ values[i*2]+ 1j*values[i*2+1] for i in range(len(values)//2)])
#    return values
    ''' 
    if self.complex_sample_list == None:
      self.complex_sample_list = new
    else:
      self.complex_sample_list = np.vstack((self.complex_sample_list,new))
    '''
#    new2 = np.array([ values2[i*2]+ 1j*values2[i*2+1] for i in range(len(values2)//2)])
    new = np.array([ values[i*2] for i in range(len(values)//2)])
    new_ = np.array([ values[i*2+1] for i in range(len(values)//2)])
    new2 = np.array([ values2[i*2] for i in range(len(values2)//2)])
    new2_ = np.array([ values2[i*2+1] for i in range(len(values2)//2)])
#    print (new[:10])
    return [values, values2]


   
#########################
#   def startSample()
#
  def startSample(self,nPoints=201):

#    numSamples = 100
#    print ("Number of Samples to Read :", numSamples)
    return self.samplePoints(nPoints)
    '''
    s = sched.scheduler(time.time, time.sleep)
  
    for count in range(numSamples):
      s.enter(1, 1, instV.samplePoints, ())
    
    
    print ("Got samples: ", len(self.complex_sample_list))
    sampAvg = np.mean(complex_sample_list, axis=0)
    
    plotMeas(self.freqL, sampAvg)
    '''



'''
if __name__ == '__main__':  # You should keep this line for our auto-grading code.

  # Example setup
  #inst.write("CHAN1")
  #inst.write("AUXCOFF") ##<< Not working
  #inst.write('S11')
  #inst.write('LOGM')

  #inst.write('POIN 11;')
  #inst.write("STAR 50.E+6;")
  #inst.write("STOP 200.E+6;")
  #inst.write("LOGFREQ;")

  instV = vnaHP8753C_Gpib(Addr=16)

  instV.startSample()
'''

