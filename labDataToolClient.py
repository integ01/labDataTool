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
      print ("Connect to: "+ str(self.channel))

    except:
      #print("GRPC init exception has been caught.")
      #printUsageSelect()
      raise ValueError("GRPC init exception has been caught ")

  def lab_start_sample(self, enaParams= {}):
    #with self.channel as channel:
      if len(enaParams) >0:
         exprSetup = guiRpc_pb2.ExperimentSetup(Meas_id = enaParams['Meas_id'], 
             ENADataMode =  enaParams['ENADataMode'], 
             NumberOfPoints =  enaParams['NumOfPoints'], 
             freq_STAR= enaParams['freq_STAR'], 
             freq_STOP= enaParams['freq_STOP'], 
             freq_CENT= enaParams['freq_CENT'], 
             freq_SPAN= enaParams['freq_SPAN'], 
             dataFormat=enaParams['dataFormat'], 
             Sparam1=  (enaParams['S11'] +  enaParams['S21'] +  enaParams['S12'] + enaParams['S22']), 
             Sparam2 = 0,
             Sparam3 = 0,
             Sparam4 = 0
           )   
      else:    
         #TODO 
         exprSetup = guiRpc_pb2.ExperimentSetup(Meas_id = 0, ENADataMode = 1, 
             NomberOfPoints = 402, freq_STAR=1e9, freq_STOP=2e9, freq_CENT=0, freq_SPAN=0,
             dataFormat=0, 
             Sparam1= SParamType.S11+ SParamType.S21,
             Sparam2= SParamType.Nop,                       
             Sparam3= SParamType.Nop,                       
             Sparam4= SParamType.Nop )                       
#         exprSetup = guiRpc_pb2.ExperimentSetup(operator="Ben", date="2019", freqLow=1e9, freqHigh=2e9)
      samples = self.stub.startSample(exprSetup)
      samplesNp = []
      samplesId = []
      ffsNp = []
      for sample in samples:
        print ("Stub returned sample type:%s"%(type(sample)) )
        print ("Stub returned data type:%s"%(type(sample.data.data_bytes)) )
        print( "Sample data Len:%d"%( sample.data.data_length) )
        print ("Stub returned ff byte len:%d"%(len(sample.ff.data_bytes)) )
        print( "Meas_id:%d, Sample SParam Type:%s, "%( sample.Meas_id, sample.Sparam) )
        print( "Data Len:%d"%( sample.data.data_length) )
        print( "Sample Data head:%f"%( struct.unpack('d', sample.data.data_bytes[:8]) ))
#        sampleNp = np.empty((402),dtype=np.dtype('f8') )

        ffNp = np.frombuffer(sample.ff.data_bytes, dtype=np.float32)
        sampleNp = np.frombuffer(sample.data.data_bytes, dtype=np.float64)
        samplesNp.append(sampleNp)
        samplesId.append((sample.Meas_id, sample.Sparam))
        if len(ffsNp) == 0:
          ffsNp.append(ffNp)
      return (samplesNp, ffsNp, samplesId)

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





