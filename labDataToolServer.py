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

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

MOCK = True

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

#  def getDataPlot(self, request, context):
#    pass

   def startSample(self, request, context):
     dataSamp = self.vnaMach.startSample()
#     values = query_binary_values( 'OUTPDATA', datatype='d', header_fmt='hp', is_big_endian=True)
     
#     print ("First data value : %d"%(dataSamp[0,0]))
     print (dataSamp[0][0])
     sType = [guiRpc_pb2.SampleArray.S11, guiRpc_pb2.SampleArray.S21]
     for i, arr_i in enumerate(dataSamp):
       byt1 = bytearray([])
       for b in list(arr_i):
          byt1 +=  bytearray(struct.pack("d", b))

       sampleArr = guiRpc_pb2.SampleArray(
        Sparam = sType[i],
        data_length = len(arr_i),
        data_bytes = bytes(byt1)
   #     data_bytes = np.ndarray.tobytes(values)
       )
       print ("Got RPC request for Sample, return array len:%d"%(len(arr_i)))
       yield sampleArr

#  def labCmd(self, request, context):
#    return guiRpc_pb2.STATUS(ret = "Lab cmd: %d param:%s === OK."%(request.cmd, request.param1)



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

  hp8753Mock = vnaMod.vnaHP8753C_GpibMock(Addr=16)
  if MOCK:
      hp8753 = hp8753Mock 
 # else:
 #   hp8753 = vnaHP8753C_Gpib(Addr=16, numSamples_=10)

  logging.basicConfig()
  serve()




