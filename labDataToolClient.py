from concurrent import futures
import time
import math
import logging

import grpc

import guiRpc_pb2
import guiRpc_pb2_grpc
#import route_guide_resources


import struct
import numpy as np


class clientRpcAPI():
  def __init__(self, IP_PORT = 'localhost:50051'):
    try:
      
      self.channel  = grpc.insecure_channel(IP_PORT)
      self.stub = guiRpc_pb2_grpc.GuiRpcStub(self.channel)
      
    except:
      print("GRPC init exception has been caught.")
      #printUsageSelect()
      return

  def lab_start_sample(self):
    #with self.channel as channel:
      exprSetup = guiRpc_pb2.ExperimentSetup(operator="Ben", date="2019", freqLow=1e9, freqHigh=2e9)
      samples = self.stub.startSample(exprSetup)
      samplesNp = []
      ffsNp = []
      for sample in samples:
        print ("Stub returned sample type:%s"%(type(sample)) )
        print ("Stub returned ff type:%s"%(type(sample.ff.data_bytes)) )
        print ("Stub returned ff byte len:%d"%(len(sample.ff.data_bytes)) )
        print( "Sample SParam:%s data Len:%d"%( sample.Sparam,sample.data.data_length) )
        print( "Sample Freq:%s data Len:%d"%( sample.Sparam,sample.ff.data_length) )
        print( "Sample Data head:%f"%( struct.unpack('d', sample.data.data_bytes[:8]) ))
        sampleNp = np.empty((402),dtype=np.dtype('f8') )

        ffNp = np.frombuffer(sample.ff.data_bytes, dtype=np.float32)
        sampleNp = np.frombuffer(sample.data.data_bytes, dtype=np.float64)
#        ffNp = np.empty((201),dtype=np.dtype('f4') )
#        for i in range(201):
#          ffNp[i] = struct.unpack('f', sample.ff.data_bytes[i*4:i*4+4])[0]
#        for i in range(sample.Sparam,sample.data.data_length//8):
          #print (struct.unpack('d', sample.data.data_bytes[i*8:i*8+8]))
#          sampleNp[i] = struct.unpack('d', sample.data.data_bytes[i*8:i*8+8])[0]
          
        samplesNp.append(sampleNp)
        ffsNp.append(ffNp)
      return (samplesNp, ffsNp)


#def get_data_plot(stub):


#def lab_cmd(stub):


#def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
#    with grpc.insecure_channel('localhost:50051') as channel:
#        stub = guiRpc_pb2_grpc.GuiRpcStub(channel)
#        print("-------------- startSample --------------")
#        lab_start_sample(stub)
       # print("-------------- getDataPlot --------------")
       # get_data_plot(stub)
       # print("-------------- labCmd --------------")
       # lab_cmd(stub)

#if __name__ == '__main__':
#    logging.basicConfig()
#    run()





