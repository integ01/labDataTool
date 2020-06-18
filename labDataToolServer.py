from concurrent import futures
import time
import math
import logging

import grpc

import guiRpc_pb2
import guiRpc_pb2_grpc
#import route_guide_resources

import numpy as np
import struct

import vnaGPIBMocMod as vnaMod
#import vna2PortGPIBMod as vnaMod2
import sys
#import pdb

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

MOCK = False

hdStore = None
hp8753 = None
hp8753Mock = None

def query_binary_values(  cmd ,datatype='d', header_fmt='hp', is_big_endian=True):
   values = np.random.rand(201) 
   exp = np.array([ 10**(np.random.randint(-2,8)) for i in range(201)])
   values *= exp
   phi = (np.random.rand(201) -0.5)* 6 *np.pi 
#        print (phi)
   finval = np.empty((402))
   print (finval.shape)
   for i in range(len(values)):
     finval[i*2] = values[i] * np.cos(phi[i])
     finval[i*2+1] = values[i] * np.sin(phi[i])
   return finval

class GuiRpcServicer(guiRpc_pb2_grpc.GuiRpcServicer):
#"""Provides methods that implement functionality of route guide server."""

   def __init__(self, vna):
      self.vnaMach = vna
      return

   def labCmd(self, request, context):

     print ("Got command : {}".format(request.command ) )
#     reply = self.vnaMach.inst.write(request.command)
#     reply = self.vnaMach.inst.read(request.command)
     reply = self.vnaMach.inst.query(request.command)
     print ("Reply:" + reply)
     return guiRpc_pb2.CmdReply(cmdReply = reply, cmdType = 1) 
      #"Lab cmd: %d param:%s === OK."%(request.cmd, request.param1)

   #################################################################
   # startSample()
   # 
   # Input: request:
   # Output: Sample Data ... TODO
   #
   def startSample(self, request, context):
     print ("Get request parameters: id:{}, Points:{}, freqStart:{}, freqEnd:{}".format(request.Meas_id, request.NumberOfPoints, request.freq_STAR, request.freq_STOP))
     print ("Get request Sparams : {}".format(request.Sparam1 ) )
     print ("Set Start End Freqs")

     cmdStart = "STAR {}.E+6;".format(int(request.freq_STAR))
     cmdStop = "STOP {}.E+6;".format(int(request.freq_STOP))
     print(cmdStart,cmdStop)
     self.vnaMach.inst.write("STAR {}.E+6;".format(int(request.freq_STAR)))
     time.sleep(0.5)
     self.vnaMach.inst.write("STOP {}.E+6;".format(int(request.freq_STOP)))
     time.sleep(0.5)
     #pdb.set_trace()
     self.vnaMach.setFreqList(201)
     ###### 
     # Get sampls from vna 
     dataSamp = self.vnaMach.startSample(nPoints = request.NumberOfPoints)
#     values = query_binary_values( 'OUTPDATA', datatype='d', header_fmt='hp', is_big_endian=True)
     
#     print ("First data value : %d"%(dataSamp[0,0]))
     ##TODO - check this more 
     # request.Sparam1 should be 2
     sparamCount = 0
     sType = []
     if (guiRpc_pb2.SampleArray.S11 & request.Sparam1):
       sType.append(guiRpc_pb2.SampleArray.S11)
       sparamCount += 1
     if (guiRpc_pb2.SampleArray.S21 & request.Sparam1):
       sType.append(guiRpc_pb2.SampleArray.S21)
       sparamCount += 1
     if (guiRpc_pb2.SampleArray.S12 & request.Sparam1):
       sType.append(guiRpc_pb2.SampleArray.S12)
       sparamCount += 1
     if (guiRpc_pb2.SampleArray.S22 & request.Sparam1):
       sType.append(guiRpc_pb2.SampleArray.S22)
       sparamCount += 1

#       sType.append([guiRpc_pb2.SampleArray.S11])
     print ("SparamCount: ",sparamCount)
     print ("Num of Sample Vecs: {}".format(len(dataSamp)))
     sparamCount = 2
     numSamps = len(dataSamp)//sparamCount
     sTypeAll = []
     # TODO - Assuming that S21 measured first and then S11
     for sp in sType[::-1]:
         sTypeAll += [sp]*numSamps
     ####
     print (dataSamp[0].shape)
     print (dataSamp[0].dtype)

     for i, arr_i in enumerate(dataSamp):
        byt1 = bytearray([])
        for b in list(arr_i):
           byt1 +=  bytearray(struct.pack("d", b))
        ffbyt = bytearray([])
        for b in self.vnaMach.freqL:
          ffbyt +=  bytearray(struct.pack("f", b))
#        np.frombuffer(message_image, dtype=np.uint8)

        dataB = guiRpc_pb2.ByteBlock( 
             data_length =  len(arr_i),
             data_bytes = bytes(byt1)
         )
        ffB = guiRpc_pb2.ByteBlock( 
             data_length = len(self.vnaMach.freqL),
             data_bytes = bytes(ffbyt)
         )

        sampleArr = guiRpc_pb2.SampleArray(
         Meas_id = request.Meas_id,
         Sparam = sTypeAll[i],
         data = dataB,
         ff = ffB 
   #     data_bytes = np.ndarray.tobytes(values)
        )
        print ("Got RPC request for Sample, Sample return array len:%d, Freq return len:%d"%(dataB.data_length, ffB.data_length ))
        yield sampleArr




def serve():
    global hp8753
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    guiRpc_pb2_grpc.add_GuiRpcServicer_to_server(
        GuiRpcServicer(hp8753), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)



if __name__ == '__main__':
 # global MOCK
 # global hp8753Mock
 # global hp8753

  if hasattr(__builtins__, 'raw_input'): 
   input = raw_input
  
  MOCK = False
  if len(sys.argv)>1:
    if 'M' in sys.argv[1]: 
      MOCK=True

  if not MOCK:
    import vna2PortGPIBMod as vnaMod2
    try:
      hp8753 = vnaMod2.vnaHP8753C_Gpib(Addr=16, numSamples_=10)
    except:
      print ("Unexpected error:", sys.exc_info()[0])
      print ("Probably your Network Analyzer is not powered up or initialized")
      
      sel = input("Do you want to work in Mocked mode?[Y/n]")
      if sel == '' or sel == 'Y':
         MOCK = True
      else:
         exit()
  if MOCK:
      hp8753Mock = vnaMod.vnaHP8753C_GpibMock(Addr=16)
      hp8753 = hp8753Mock 


  logging.basicConfig()
  serve()




