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

   def labCmd(self, request, context):

     print ("Got command : {}".format(request.command ) )
     reply = self.vnaMach.inst.write(request.command)
     reply = self.vnaMach.inst.read(request.command)
     print ("Reply:" + reply)
     return guiRpc_pb2.CmdReply(cmdReply = reply, cmdType = 1) 
      #"Lab cmd: %d param:%s === OK."%(request.cmd, request.param1)

   def startSample(self, request, context):
     print ("Get request parameters: id:{}, Points:{}, freqStart:{}, freqEnd:{}".format(request.Meas_id, request.NumberOfPoints, request.freq_STAR, request.freq_STOP))
     print ("Get request Sparams : {}".format(request.Sparam1 ) )
     dataSamp = self.vnaMach.startSample(nPoints = request.NumberOfPoints)
#     values = query_binary_values( 'OUTPDATA', datatype='d', header_fmt='hp', is_big_endian=True)
     
#     print ("First data value : %d"%(dataSamp[0,0]))
     print (dataSamp[0][0])
     sType = [guiRpc_pb2.SampleArray.S11, guiRpc_pb2.SampleArray.S21]
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
         Sparam = sType[i],
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

  hp8753Mock = vnaMod.vnaHP8753C_GpibMock(Addr=16)
  if MOCK:
      hp8753 = hp8753Mock 
 # else:
 #   hp8753 = vnaHP8753C_Gpib(Addr=16, numSamples_=10)

  logging.basicConfig()
  serve()




