
import wx
import wx.grid
from wx import xrc


import h5py
import numpy as np
import tables
import time
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
        self.hdStore = None
        self.rpcClient = None
        self.nPoints = 0
        self.nScans = 10
        self.freqStart =0
        self.freqStop =0
        self.freqCent=0
        self.freqSpan=0
        self.S11 = 0
        self.S21 = 0
        self.S12 = 0
        self.S22 = 0

        self.res = xrc.XmlResource("mna2.xrc")
        self.frameMain = self.res.LoadFrame(None, "FrameMain")
        self.notebook = xrc.XRCCTRL(self.frameMain, "m_notebook1")
        self.panelMain = xrc.XRCCTRL(self.notebook, "m_panelExperiment")
        self.panelVNA = xrc.XRCCTRL(self.notebook, "m_panelVNA")
        self.panelDB = xrc.XRCCTRL(self.notebook, "m_panelDB")
        self.panelDBTbl = xrc.XRCCTRL(self.notebook, "m_panelDBTable")
        self.m_buttonConnect = xrc.XRCCTRL(self.panelVNA, "m_buttonConnect")
        self.m_buttonMeasure = xrc.XRCCTRL(self.panelMain, "m_buttonMeasure")
        self.m_buttonStop = xrc.XRCCTRL(self.panelMain, "m_buttonStop")
        self.m_buttonStart = xrc.XRCCTRL(self.panelMain, "m_buttonStart")
        self.m_buttonCont = xrc.XRCCTRL(self.panelMain, "m_buttonCont")


        self.m_textIp1 = xrc.XRCCTRL(self.panelVNA, "m_textIp1")
        self.m_textIp2 = xrc.XRCCTRL(self.panelVNA, "m_textIp2")
        self.m_textIp3 = xrc.XRCCTRL(self.panelVNA, "m_textIp3")
        self.m_textIp4 = xrc.XRCCTRL(self.panelVNA, "m_textIp4")
        

        self.vna_textNumSamplePoints = xrc.XRCCTRL(self.panelVNA, "m_textCtrlNumSamplePoints")
        self.vna_textCtrlNumScans = xrc.XRCCTRL(self.panelVNA, 'm_textCtrlNumScans')
        self.vna_checkBoxS11 = xrc.XRCCTRL(self.panelVNA, 'm_checkBoxS11')
        self.vna_checkBoxS21 = xrc.XRCCTRL(self.panelVNA, 'm_checkBoxS21')
        self.vna_checkBoxS12 = xrc.XRCCTRL(self.panelVNA, 'm_checkBoxS12')
        self.vna_checkBoxS22 = xrc.XRCCTRL(self.panelVNA, 'm_checkBoxS22')

        self.vna_textCtrlFreqStart = xrc.XRCCTRL(self.panelVNA, 'm_textCtrlFreqStart')
        self.vna_textCtrlFreqEnd = xrc.XRCCTRL(self.panelVNA, 'm_textCtrlFreqEnd')
        self.vna_textCtrlFreqCenter = xrc.XRCCTRL(self.panelVNA, 'm_textCtrlFreqCenter')
        self.vna_textCtrlFreqSpan = xrc.XRCCTRL(self.panelVNA, 'm_textCtrlFreqSpan')
        self.vna_radioBtnSelStartEnd = xrc.XRCCTRL(self.panelVNA, 'm_radioBtnSelStartEnd')
        self.vna_radioBtnSelCentSpan = xrc.XRCCTRL(self.panelVNA, 'm_radioBtnSelCentSpan')
        self.vna_buttonVNATest = xrc.XRCCTRL(self.panelVNA, 'm_buttonVNATest')

        self.vna_textCtrlDBFile =  xrc.XRCCTRL(self.panelVNA, 'm_textCtrlDBFile1')
        self.vna_button6DBFileOpen = xrc.XRCCTRL(self.panelVNA, 'm_button6DBFileOpen1')

        self.db_textCtrlDBFile =  xrc.XRCCTRL(self.panelDB, 'm_textCtrlDBFile')
        self.db_button6DBFileOpen = xrc.XRCCTRL(self.panelDB, 'm_button6DBFileOpen')
        self.db_radioTime_Today = xrc.XRCCTRL(self.panelDB, 'm_radioTime_Today')
        self.db_radioBtnTimeLastHour = xrc.XRCCTRL(self.panelDB, 'm_radioBtnTimeLastHour')
        self.db_radioBtnTime_All = xrc.XRCCTRL(self.panelDB, 'm_radioBtnTime_All')
        self.db_radioBtnTime_Min = xrc.XRCCTRL(self.panelDB, 'm_radioBtnTime_Min')
        self.db_textCtrlDBNumMinutes = xrc.XRCCTRL(self.panelDB, 'm_textCtrlDBNumMinutes')
        self.db_buttonSearch= xrc.XRCCTRL(self.panelDB, 'm_buttonSearch')

        self.m_gridDataTable = xrc.XRCCTRL(self.panelDBTbl, "m_gridDataTable")
	# Grid
        print (type(self.m_gridDataTable ))
        self.m_gridDataTable.CreateGrid( 28, 11 )
        self.m_gridDataTable.EnableEditing( True )
        self.m_gridDataTable.EnableGridLines( True )
        self.m_gridDataTable.EnableDragGridSize( False )
        self.m_gridDataTable.SetMargins( 0, 0 )
 
	# Columns
        self.m_gridDataTable.EnableDragColMove( False )
        self.m_gridDataTable.EnableDragColSize( True )
        self.m_gridDataTable.SetColLabelSize( 30 )
        self.m_gridDataTable.SetColLabelValue( 0, u"Date" )
        self.m_gridDataTable.SetColLabelValue( 1, u"Session" )
        self.m_gridDataTable.SetColLabelValue( 2, u"Author" )
        self.m_gridDataTable.SetColLabelValue( 3, u"Base" )
        self.m_gridDataTable.SetColLabelValue( 4, u"Comp 1" )
        self.m_gridDataTable.SetColLabelValue( 5, u"Comp 2" )
        self.m_gridDataTable.SetColLabelValue( 6, u"Comp 3" )
        self.m_gridDataTable.SetColLabelValue( 7, u"P1" )
        self.m_gridDataTable.SetColLabelValue( 8, u"P2" )
        self.m_gridDataTable.SetColLabelValue( 9, u"P3" )
        self.m_gridDataTable.SetColLabelValue( 10, u"H5Path" )
        self.m_gridDataTable.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

	# Rows
        self.m_gridDataTable.EnableDragRowSize( True )
        self.m_gridDataTable.SetRowLabelSize( 80 )
        self.m_gridDataTable.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )


        self.m_textTester = xrc.XRCCTRL(self.panelMain, "m_textTester")
        self.m_textNotes = xrc.XRCCTRL(self.panelMain, "m_textNotes")
        self.m_textSession = xrc.XRCCTRL(self.panelMain, "m_textSession")
        self.m_choiceProcedure = xrc.XRCCTRL(self.panelMain, "m_choiceProcedure")
        self.m_textInitialVol = xrc.XRCCTRL(self.panelMain, "m_textInitialVol")
        self.m_textNumMeasures =  xrc.XRCCTRL(self.panelMain, "m_textNumMeasures")
        self.m_textConcenDelta = xrc.XRCCTRL(self.panelMain, "m_textCtrl7")
        self.m_textPepetoVolEx = xrc.XRCCTRL(self.panelMain, "m_textPepetoVolEx")
        self.m_choiceStep = xrc.XRCCTRL(self.panelMain, "m_choiceStep")
        
        self.expr_testBase = xrc.XRCCTRL(self.panelMain, "m_choiceBase")
        self.expr_BaseComment =  xrc.XRCCTRL(self.panelMain, "m_textBaseComment")
        self.expr_volume = xrc.XRCCTRL(self.panelMain, "m_textVolume")
        self.expr_comp1 = xrc.XRCCTRL(self.panelMain, "m_textComp1")
        self.expr_comp2 = xrc.XRCCTRL(self.panelMain, "m_textComp2")
        self.expr_comp3 = xrc.XRCCTRL(self.panelMain, "m_textComp3")
        self.expr_comp4 = xrc.XRCCTRL(self.panelMain, "m_textComp4")
        self.expr_P1 = xrc.XRCCTRL(self.panelMain, "m_textP1")
        self.expr_P2 = xrc.XRCCTRL(self.panelMain, "m_textP2")
        self.expr_P3 = xrc.XRCCTRL(self.panelMain, "m_textP3")
        self.expr_P4 = xrc.XRCCTRL(self.panelMain, "m_textP4")


        self.m_gauge1 = xrc.XRCCTRL(self.panelMain, "m_gauge1")
        self.m_listBox1 = xrc.XRCCTRL(self.panelMain, "m_listBox1")
        
         
        self.dataBaseName = "dataFile0"
        self.dataBasePath = "../dataDir"
        self.expr = {}

    def OnInit(self):
        self.frame_init_()
        #mainFrame = frameMain(self)
        #mainFrame.show(True)
        self.m_buttonStart.Bind( wx.EVT_BUTTON, self.m_buttonStartOnButtonClick )
        self.m_buttonMeasure.Bind( wx.EVT_BUTTON, self.m_buttonMeasureOnButtonClick )
        self.m_buttonStop.Bind( wx.EVT_BUTTON, self.m_buttonStopOnButtonClick )
        self.m_buttonCont.Bind( wx.EVT_BUTTON, self.m_buttonContOnButtonClick )
        self.m_buttonConnect.Bind( wx.EVT_BUTTON, self.m_buttonConnectOnButtonClick )
        self.db_button6DBFileOpen.Bind(  wx.EVT_BUTTON, self.db_buttonDBFileOpenClick )
        self.vna_button6DBFileOpen.Bind(  wx.EVT_BUTTON, self.vna_buttonDBFileOpenClick )
        
        self.db_buttonSearch.Bind( wx.EVT_BUTTON, self.db_buttonSearchOnButtonClick )
        self.vna_buttonVNATest.Bind( wx.EVT_BUTTON, self.vna_buttonVNATestOnButtonClick)



        self.frameMain.Show(True)
        self.state  = 0
        self.connectUrl = "127.0.0.1"
        self.connectState = 0
        #dateStr= datetime.datetime.now().strftime("%d/%m/%y")
        #print (dateStr)
        self.m_textSession.WriteText("1")
        self.m_textInitialVol.WriteText("100")
        self.m_textNumMeasures.WriteText("10")
        self.vna_textCtrlFreqStart.WriteText("500")
        self.vna_textCtrlFreqEnd.WriteText("3000")

        # Set default IP address

        self.m_textIp1.WriteText("127")
        self.m_textIp2.WriteText("0")
        self.m_textIp3.WriteText("0")
        self.m_textIp4.WriteText("1")
        self.db_textCtrlDBFile.WriteText(self.dataBasePath + "/" + self.dataBaseName)
        self.vna_textCtrlDBFile.WriteText(self.dataBasePath + "/" + self.dataBaseName)
        self.vna_textCtrlNumScans.WriteText(str(self.nScans))
        self.vna_checkBoxS11.SetValue(True)
        self.vna_checkBoxS21.SetValue(True)

        #self.m_gridDataTable.AppendRows(1)
      
        return True


    def msgLabStep(self, i, msg=''):
      if msg == '':
        if i==1:
          self.m_listBox1.Clear()
        #self.m_listBox1.Append(messages.fixedVolMsgStep[i].format(self.expr['material1'], self.expr['volumeExchange'] ))
          msg = messages.fixedVolMsgStep[i].format(self.expr['material1'], self.expr['volumeExchange'] )
        else:
          self.m_listBox1.Clear()
          #self.m_listBox1.Append( messages.fixedVolMsgStep[i])
          msg =  messages.fixedVolMsgStep[i]

      self.m_listBox1.Append( msg) 
      wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)

# Virtual event handlers, overide them in your derived class

    def db_buttonSearchOnButtonClick(self, event):
        # TODO - add table presentation option
        parami = 0
        sp = 0   # TODO Add sparam selection
        cmd = 'All'
        if (self.db_radioTime_Today.GetValue()):
            cmd = 'Today'
        elif (self.db_radioBtnTimeLastHour.GetValue()):
            cmd = 'LastHour'
        elif (self.db_radioBtnTime_All.GetValue()):
            cmd = 'All'
        elif (self.db_radioBtnTime_Min.GetValue()):
            cmd = 'LastMinutes'
            try:
              param = self.db_textCtrlDBNumMinutes.GetValue()
              parami = int(param)
            except ValueError:
              print ("Wrong value in Minuts text") 
        freqL, clist = samplePlot.dbQuery(self.hdStore, cmd, parami, sp)
        samplePlot.plotMeas(freqL, clist) 

        
    def getVNAFields(self):    
      try:
#        self.nPoints = int(self.vna_textNumSamplePoints.GetValue())
#        self.nScans = int(self.vna_textCtrlNumScans.GetValue())
#        print(str(self.vna_radioBtnSelStartEnd.GetSelection()))
        print ("Start getVNAFields")
        print(self.vna_radioBtnSelStartEnd.GetValue())
        if self.vna_radioBtnSelStartEnd.GetValue():
          print ("VNA fields select freqStart/Stop") 
          print(self.vna_textCtrlFreqStart.GetValue())
          print(self.vna_textCtrlFreqEnd.GetValue())
          self.freqStart = int(self.vna_textCtrlFreqStart.GetValue())
          self.freqStop = int(self.vna_textCtrlFreqEnd.GetValue())
          self.freqCent = 0
          self.freqSpan = 0

        else:
          print ("VNA fields select freqCent/Span") 
          self.freqStart = 0
          self.freqStop = 0
          self.freqCent = int(self.vna_textCtrlFreqCenter.GetValue())
          self.freqSpan = int(self.vna_textCtrlFreqSpan.GetValue())

        self.S11 = self.vna_checkBoxS11.GetValue()
        self.S21 = self.vna_checkBoxS21.GetValue()
        self.S12 = self.vna_checkBoxS12.GetValue()
        self.S22 = self.vna_checkBoxS22.GetValue()
      except:
        print ("GUI Error in VNA fields values")


    def getExperFields(self):  
      print ("DBG: start of get Fields") 
      print ( int(time.time()))
      self.expr['unix_timestamp'] = int(time.time())
      self.expr['author'] = self.m_textTester.GetValue()
      self.expr['misc'] = self.m_textNotes.GetValue()
      self.session = self.m_textSession.GetValue()
      self.expr['session'] = self.m_textSession.GetValue()

      print ("Tester Name:"+self.expr['author'])
      print ("Test Notes:"+ self.expr['misc'])
      print ("Session:" + self.session)

      self.expr['volume'] = self.expr_volume.GetValue()

      self.expr['component0'] = self.expr_testBase.GetSelection()
      self.expr['component1'] = self.expr_comp1.GetValue()
      self.expr['component2'] = self.expr_comp2.GetValue()
      self.expr['component3'] = self.expr_comp3.GetValue()
      self.expr['component4'] = self.expr_comp4.GetValue()
      self.expr['component5'] = "" #TODO update

      print("Test Base:" + str(self.expr['component0']))
      self.expr['title'] = str(self.expr['component0']) + self.expr['volume'] +self.expr['author'] 

      self.expr['P0_volume'] = self.expr_BaseComment.GetValue()
      self.expr['P1'] = self.expr_P1.GetValue()
      self.expr['P2'] = self.expr_P2.GetValue()
      self.expr['P3'] = self.expr_P3.GetValue()
      self.expr['P4'] = self.expr_P4.GetValue()
      self.expr['P5'] = "0"#TODO update

      self.expr['numberOfComponents'] = 1 #TODO comp_sum(self.expr)

      self.expr['stepUpDn'] = self.m_choiceStep.GetSelection()
      print("step:" + str(self.expr['stepUpDn']))
      self.expr['Procedure'] = self.m_choiceProcedure.GetSelection()
      print("Test Procedure:" + str(self.expr['Procedure']))

      self.expr['InitVolume'] =  self.m_textInitialVol.GetValue()
      print ("initialVol:" + self.expr['InitVolume'])
      self.expr['numMeasures'] = self.m_textNumMeasures.GetValue()
      print (self.expr['numMeasures'])
      self.expr['concenDelta'] = self.m_textConcenDelta.GetValue() 
      print (self.expr['concenDelta'])
      self.expr['initConcentrate'] = "0.1" # TODO -checkthis
#      print (w.Text_InitConcen.get("1.0","end-1c"))
      self.expr['volumeExchange'] = self.m_textPepetoVolEx.GetValue()
      print (self.expr['volumeExchange'])

    def openFileClickCommon(self, filepath):
      filename = os.path.basename(filepath)
      filepath = filepath[:-len(filename)-1]
      if filepath == '':
            filename = self.dataBaseName
            filepath = self.dataBasePath
      print ("DB Open file event:" + filepath + "~~" + filename)
      filters1=tables.Filters(complevel=0)
      restore = True
      try:
          dlg = wx.MessageDialog(None, "File already exists, do you want to overwrite it?",'Overwrite', wx.YES_NO | wx.NO_DEFAULT|wx.ICON_QUESTION)
          self.hdStore = hdf5DataTable(filters=filters1, path=filepath, dataBase_=filename, restore=restore, console=False,guidlg=dlg)
      except Exception as e:
          print(e, str(e))
          print("DB Exception" )
          self.db_button6DBFileOpen.SetBackgroundColour('gray')
          self.vna_button6DBFileOpen.SetBackgroundColour('gray')
          return  
      # End of While 
      self.db_button6DBFileOpen.SetBackgroundColour('blue')
      self.vna_button6DBFileOpen.SetBackgroundColour('blue')

    def vna_buttonDBFileOpenClick(self, event):
      filepath = self.vna_textCtrlDBFile.GetValue()
      self.db_textCtrlDBFile.SetValue(filepath)
      self.openFileClickCommon(filepath)

    def db_buttonDBFileOpenClick(self, event):
      filepath = self.db_textCtrlDBFile.GetValue()
      self.vna_textCtrlDBFile.SetValue(filepath)
      self.openFileClickCommon(filepath)

     
    def m_buttonConnectOnButtonClick( self, event ):
             
      ip1 = self.m_textIp1.GetValue()
      ip2 = self.m_textIp2.GetValue()
      ip3 = self.m_textIp3.GetValue()
      ip4 = self.m_textIp4.GetValue()
      ip = ip1 + "." + ip2 + "." + ip3 + "." + ip4 + ":50051"
      print ("connect Button action")
      if (self.connectState != 0):
           self.connectState = 0
           self.m_buttonConnect.SetBackgroundColour('gray')
           del self.rpcClient
      else:
        try:
          print ("VNA Connect event, trying to connect to IP:" + ip)
          self.rpcClient = labDataToolClient.clientRpcAPI(IP_PORT = ip)
          self.connectState = 1
          # Test connection
          res = self.rpcClient.lab_send_cmd("POIN?")
          try:
            self.nPoints = int(float(res))
          except:
            print ("Result of command:" + res + ", cannot convert to int")
          self.vna_textNumSamplePoints.Clear()
          self.vna_textNumSamplePoints.WriteText(str(self.nPoints))
          print ("Result of command:" + res)
          
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


       #self.m_listBox1.Clear()
       #self.m_listBox1.Append("Test Session End\n==========")

       self.msgLabStep(0, msg="Test Session End\n==========")

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

    def vna_buttonVNATestOnButtonClick(self, event):
      global gEna
      print ("Test VNA Measure Button Pressed")
      #event.Skip()
      sys.stdout.flush()
      if self.connectState != 1:
        print("Error - Need to connect to VNA server first")
        return
      ############################3
      #TODO - update setup fields
      #############################3
      setUp = samplePlot.setUp
      setUp['session'] =  1 #rfSystem.maxsess
      setUp['component0'] = 'water'
      setUp['P1'] = 0.1 
      setUp['misc'] = 'Notes here'
      setUp['author'] = 'Test author here'
#      rfSystem.startSample(setUp)
      self.getVNAFields()
      gEna['NumOfPoints'] = self.nPoints
      gEna['NumOfScans'] = self.nScans
      gEna['freq_STAR'] = self.freqStart
      gEna['freq_STOP'] = self.freqStop
      gEna['freq_CENT'] = self.freqCent
      gEna['freq_SPAN'] = self.freqSpan
      gEna['S11'] = int(self.S11)
      gEna['S21'] = int(self.S21)*2
      gEna['S12'] = int(self.S12)*4
      gEna['S22'] = int(self.S22)*8

 
      if self.rpcClient != None:
         samplePlot.measureRemoteCall(self.rpcClient, gEna, setUp, hdStore=None)
 

    def m_buttonMeasureOnButtonClick( self, event ):
      global gEna
      print ("Measure Button Presses")
      #event.Skip()
      print('LabExper0_support.btnMeasurePress')
      sys.stdout.flush()
      if self.state == 0 or self.state == 2:
        print("Error - Need to start session first")
        return
      ############################3
      #TODO - update setup fields
      #############################3
      self.getExperFields()
    
      if self.rpcClient != None:
         samplePlot.measureRemoteCall(self.rpcClient, gEna, self.expr, hdStore=self.hdStore)
 
      if self.state == 1:
        self.msgLabStep(0)
      self.state = 2





    def m_buttonStartOnButtonClick( self, event ):
      print ("Start Button Presses")
      #event.Skip()
      if self.state != 0:
        print ("Wrong State Error")
        return
      print('LabExper0_support. Start the Experiment')
      try:
        self.getExperFields()
        #self.session = self.m_textSession.GetValue()
        print(self.session)
        self.maxsess = int(self.session)
        self.expr['numMeasures'] = self.m_textNumMeasures.GetValue()
        print (self.expr['numMeasures'])
         #TODO check this
        self.expr['testNumber'] = int(self.expr['numMeasures'])
        self.numM = self.expr['testNumber']
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
#      self.m_listBox1.Clear()
#      self.m_listBox1.Append(messages.fixedVolMsgStart[0].format(self.session, self.expr['material1']) )
      self.msgLabStep(0, msg= messages.fixedVolMsgStart[0].format(self.session, self.expr['component1']) )
      #w.btnStart.configure(background="green")
 #    print (w.Checkbutton_DBOK.get("1.0","end-1c"))





if __name__ == '__main__':

   # Adding RPC client    
    #logging.basicConfig()
    #rpcClient = labDataToolClient.clientRpcAPI() #IP_PORT = 'localhost:50051'
    #main(rpcClient)

    gEna = samplePlot.setEnaParams( [0, 1, 801, 1e9, 2e9, 1.5e9, 1e9, 0, 1, 1,0,0])
    appframe = MainApp(False)
    appframe.MainLoop()

