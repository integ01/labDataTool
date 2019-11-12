
import wx
from wx import xrc


import h5py
import numpy as np
import tables
import os
import sys

sys.path.append("../")
import matplotlib.pyplot as plt
from dbHdf5TablesMod import hdf5DataTable
import messages

import logging
import labDataToolClient
import rfSampleClientConsole as samplePlot
#import matplotlib.pyplot as plt

class MainApp(wx.App):
    def frame_init_(self):
#        self.res = xrc.XmlResource("dt/mna.xrc")
        self.rpcClient = None
        self.res = xrc.XmlResource("mna2.xrc")
        self.frameMain = self.res.LoadFrame(None, "FrameMain")
        self.notebook = xrc.XRCCTRL(self.frameMain, "m_notebook1")
        self.panelMain = xrc.XRCCTRL(self.notebook, "m_panelExperiment")
        self.panelVNA = xrc.XRCCTRL(self.notebook, "m_panelVNA")
        self.panelDB = xrc.XRCCTRL(self.notebook, "m_panelDB")

        self.m_buttonConnect = xrc.XRCCTRL(self.panelVNA, "m_buttonConnect")
        self.m_buttonStart = xrc.XRCCTRL(self.panelMain, "m_buttonStart")
        self.m_buttonMeasure = xrc.XRCCTRL(self.panelMain, "m_buttonMeasure")
        self.m_buttonStop = xrc.XRCCTRL(self.panelMain, "m_buttonStop")
        self.m_buttonCont = xrc.XRCCTRL(self.panelMain, "m_buttonCont")


        self.m_textIp1 = xrc.XRCCTRL(self.panelVNA, "m_textIp1")
        self.m_textIp2 = xrc.XRCCTRL(self.panelVNA, "m_textIp2")
        self.m_textIp3 = xrc.XRCCTRL(self.panelVNA, "m_textIp3")
        self.m_textIp4 = xrc.XRCCTRL(self.panelVNA, "m_textIp4")



        self.m_textTester = xrc.XRCCTRL(self.panelMain, "m_textTester")
        self.m_textNotes = xrc.XRCCTRL(self.panelMain, "m_textNotes")
        self.m_textSession = xrc.XRCCTRL(self.panelMain, "m_textSession")
        self.m_textInitialVol = xrc.XRCCTRL(self.panelMain, "m_textInitialVol")
        self.m_textNumMeasures =  xrc.XRCCTRL(self.panelMain, "m_textNumMeasures")
        self.m_textInitialVol = xrc.XRCCTRL(self.panelMain, "m_textInitialVol")
        self.m_textConcenDelta = xrc.XRCCTRL(self.panelMain, "m_textCtrl7")
        self.m_textPepetoVolEx = xrc.XRCCTRL(self.panelMain, "m_textPepetoVolEx")
        self.m_choiceStep = xrc.XRCCTRL(self.panelMain, "m_choiceStep")
        self.m_choiceTestType = xrc.XRCCTRL(self.panelMain, "m_choice1")
        self.m_choiceProcedure = xrc.XRCCTRL(self.panelMain, "m_choiceProcedure")
        self.m_gauge1 = xrc.XRCCTRL(self.panelMain, "m_gauge1")
        self.m_listBox1 = xrc.XRCCTRL(self.panelMain, "m_listBox1")
    def OnInit(self):
        self.frame_init_()
        #mainFrame = frameMain(self)
        #mainFrame.show(True)
        self.m_buttonStart.Bind( wx.EVT_BUTTON, self.m_buttonStartOnButtonClick )
        self.m_buttonMeasure.Bind( wx.EVT_BUTTON, self.m_buttonMeasureOnButtonClick )
	self.m_buttonStop.Bind( wx.EVT_BUTTON, self.m_buttonStopOnButtonClick )
	self.m_buttonCont.Bind( wx.EVT_BUTTON, self.m_buttonContOnButtonClick )
        self.m_buttonConnect.Bind( wx.EVT_BUTTON, self.m_buttonConnectOnButtonClick )

        self.frameMain.Show(True)
        self.state  = 0
        self.expr = {}
        self.connectUrl = "127.0.0.1"
        self.connectState = 0
        #dateStr= datetime.datetime.now().strftime("%d/%m/%y")
        #print (dateStr)
        self.m_textSession.WriteText("1")
        self.m_textInitialVol.WriteText("100")
        self.m_textNumMeasures.WriteText("10")

        # Set default IP address
#        self.m_textIp1.WriteText("127")
#        self.m_textIp2.WriteText("0")
        self.m_textIp3.WriteText("0")
        self.m_textIp4.WriteText("1")
        return True


    def msgLabStep(self, i):
      if i==1:
        self.m_listBox1.Clear()
        self.m_listBox1.Append(messages.fixedVolMsgStep[i].format(self.expr['material1'], self.expr['volumeExchange'] ))
      else:
        self.m_listBox1.Clear()
        self.m_listBox1.Append( messages.fixedVolMsgStep[i])


# Virtual event handlers, overide them in your derived class

    def m_buttonConnectOnButtonClick( self, event ):
             
      ip1 = self.m_textIp1.GetValue()
      ip2 = self.m_textIp2.GetValue()
      ip3 = self.m_textIp3.GetValue()
      ip4 = self.m_textIp4.GetValue()
      ip = ip1 + "." + ip2 + "." + ip3 + "." + ip4 + ":50051"
      print ("VNA Connect event, trying to connect to IP:" + ip)
      try:
        self.rpcClient = labDataToolClient.clientRpcAPI(IP_PORT = ip)
        self.connectState = 1
        self.m_buttonConnect.SetBackgroundColour('green')

      except ValueError as err:
        print(err.args)
        self.connectState = 0
        self.m_buttonConnect.SetBackgroundColour('gray')

    def m_buttonStopOnButtonClick( self, event ):
       print ("End of Test")
#      event.Skip()
       print('LabExper0_support.btnDonePress')
       sys.stdout.flush()
       self.state = 0
       #currSess = rfSystem.maxsess
       #rfSystem.maxsess += 1
       #w.Text_Session.delete(1.0, tk.END)
       #w.Text_Session.insert(1.0, str(rfSystem.maxsess))
       #w.btnStart.configure(background=orig_color)


       self.m_listBox1.Clear()
       self.m_listBox1.Append("Test Session End\n==========")

       #rfSystem.getDataPlot('Session', currSess)

    def m_buttonContOnButtonClick( self, event ):
      if self.state == 0:
         print("Error - Need to start session first")
         return
      print('LabExper0_support.btnContinuePress')
      if self.state != 2:
       print ("Wrong state")
       return
      self.msgLabStep(1)
      self.state = 1
      sys.stdout.flush()
      self.expr['testNumber'] -= 1
      tidx = -self.expr['testNumber'] + self.numM + 1
      if tidx > self.numM:
       #Done
        self.m_buttonStopOnButtonClick(event)
        return
      self.m_gauge1.SetValue(tidx)


      #try:
       # mat1Concen = float(expr['mat1Concen']) + 0.1
      #except:
      #  print ("Wrong value in Material 1 concentration")
      #  mat1Concen = 0.0
    
#      expr['mat1Concen']= str(mat1Concen)
#    w.Text_Mat1Concen.delete(1.0, tk.END)
      # TODO - add concentration increment
      # w.TextCurrentConc1.insert(1.0, str(expr['mat1Concen']))



    def m_buttonMeasureOnButtonClick( self, event ):
      print ("Measure Button Presses")
      #event.Skip()
      print('LabExper0_support.btnMeasurePress')
      sys.stdout.flush()
      if self.state == 0 or self.state == 2:
        print("Error - Need to start session first")
        return
      setUp = {}
      setUp['session'] =  self.maxsess +1 #rfSystem.maxsess
      setUp['material'] = self.expr['material1']
      setUp['concentrate'] = self.expr['initConcentrate']
      setUp['notes'] = self.expr['testNotes']
#      rfSystem.startSample(setUp)
    
      samplePlot.measureRemoteCall(self.rpcClient)

      if self.state == 1:
        self.msgLabStep(0)
      self.state = 2





    def m_buttonStartOnButtonClick( self, event ):
      print ("Start Button Presses")
      #event.Skip()
      if self.state != 0:
        print ("Wrong State Error")
        return
      #expr = {}
      print('LabExper0_support. Start the Experiment')
      #sys.stdout.flush()
      self.expr['testerName'] = self.m_textTester.GetValue()
      print ("Tester Name:"+self.expr['testerName'])
      self.expr['testNotes'] = self.m_textNotes.GetValue()
      print ("Test Notes:"+ self.expr['testNotes'])
      self.expr['stepUpDn'] = self.m_choiceStep.GetSelection()
      print("step:" + str(self.expr['stepUpDn']))
      self.expr['testType'] = self.m_choiceTestType.GetSelection()
      print("Test Type:" + str(self.expr['testType']))
      self.expr['Procedure'] = self.m_choiceProcedure.GetSelection()
      print("Test Procedure:" + str(self.expr['Procedure']))
      self.session = self.m_textSession.GetValue()
      print ("Session:" + self.session)
      self.expr['InitVolume'] =  self.m_textInitialVol.GetValue()
      print ("initialVol:" + self.expr['InitVolume'])
      self.expr['numMeasures'] = self.m_textNumMeasures.GetValue()
      print (self.expr['numMeasures'])
      self.expr['concenDelta'] = self.m_textConcenDelta.GetValue() 
      print (self.expr['concenDelta'])
      self.expr['initConcentrate'] = "0.1"
#      print (w.Text_InitConcen.get("1.0","end-1c"))
      self.expr['volumeExchange'] = self.m_textPepetoVolEx.GetValue()
      print (self.expr['volumeExchange'])
      self.expr['material1'] = "NaCl" #TODO update
#      self.expr['material1'] = w.Text_Mat1.get("1.0","end-1c")
#      print ("Material 1:"+expr['material1'])
#      #expr['material2'] = w.Text_Mat2.get("1.0","end-1c")
#      self.expr['mat1Concen'] = w.Text_Mat1Concen.get("1.0", "end-1c")
      try:
        self.maxsess = int(self.session)
        self.expr['testNumber'] = int(self.expr['numMeasures'])
        self.numM = int(self.expr['numMeasures'])
        self.m_gauge1.SetRange(self.numM)
      except:
        print ("Exception in number parse")
        pass
      tidx = - self.expr['testNumber'] + self.numM+1
      self.m_gauge1.SetValue(tidx)
#      w.TextTestNum.insert("1.0",str(tidx)+"/"+str(expr['numM']))
      for k, i in self.expr.items():
          if (type(i) == type(str)) and len(i) == 0:
              print ("Illegal parameter: " + k)
          else:
            if k=='numMeasures' or k=='initialVol':
              try:
                self.expr[k]= float(i)
              except ValueError:
                print ("Wrong value in {}-- Please Correct ".format(k))
                return
      self.state = 1
      self.m_listBox1.Clear()
      self.m_listBox1.Append(messages.fixedVolMsgStart[0].format(self.session, self.expr['material1']) )
   
      #w.btnStart.configure(background="green")
 #    print (w.Checkbutton_DBOK.get("1.0","end-1c"))





if __name__ == '__main__':

   # Adding RPC client    
#    logging.basicConfig()
#    rpcClient = labDataToolClient.clientRpcAPI() #IP_PORT = 'localhost:50051'
    #main(rpcClient)

    appframe = MainApp(False)
    appframe.MainLoop()

