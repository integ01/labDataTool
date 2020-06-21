#############################################################
# Useful links:
# https://dzone.com/articles/wxpython-get-selected-cells-grid
#
# check box on grid table:
# https://wiki.wxpython.org/Change%20wxGrid%20CheckBox%20with%20one%20click
#
import wx
import wx.adv
import wx.grid
from wx import xrc


import h5py
import numpy as np
import tables
import time
import datetime
import os
import sys

sys.path.append("../")
import matplotlib.pyplot as plt
import dbHdf5TablesMod as hd5Mod
import messages

import logging
import labDataToolClient
import rfSampleClientConsole as samplePlot
#import matplotlib.pyplot as plt

from pathlib import Path
import pdb
from enum import Enum

import scipy.io as sio

MaxTblRows = 50
gridFrame = None

extraRows = []
version = "v0.1"

versionParams = hd5Mod.h5VersionArr[version] 
sparamSel = versionParams["sparamKeys"] #TODO - this should be 0 for S21
#sparamArr =  [ ["S11", "S21"], ["S21Mean", "S21Mean"]]
#sparamSel = sparamArr[0]

class StateO(Enum):
     IDLE = 0
     MEAS_WAIT_CONT = 2
     START = 1

     
def _pydate2wxdate(date):
     import datetime
     assert isinstance(date, (datetime.datetime, datetime.date))
     tt = date.timetuple()
     dmy = (tt[2], tt[1]-1, tt[0])
     return wx.DateTimeFromDMY(*dmy)

def _wxdate2pydate(date):
     import datetime
     assert isinstance(date, wx.DateTime)
     if date.IsValid():
          ymd = map(int, date.FormatISODate().split('-'))
          return datetime.date(*ymd)
     else:
          return None

class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Grid", size=(950,1250))
        self.grid = wx.grid.Grid(self)
#        self.grid.CreateGrid(20, 20)
 #       self.but = Button(None, self)
        self.grid.CreateGrid( MaxTblRows, 10 )
        self.grid.EnableEditing( True )
        self.grid.EnableGridLines( True )
        self.grid.EnableDragGridSize( False )
        self.grid.SetMargins( 0, 10 )
        self.grid.MakeCellVisible(20,10)
  

	# Columns
        self.grid.EnableDragColMove( False )
        self.grid.EnableDragColSize( True )
        self.grid.SetColLabelSize( 30 )
        self.grid.SetColLabelValue( 0, u"Sel" )
        self.grid.SetColLabelValue( 1, u"Date" )
        self.grid.SetColLabelValue( 2, u"Session" )
        self.grid.SetColLabelValue( 3, u"Author" )
        self.grid.SetColLabelValue( 4, u"Base" )
        self.grid.SetColLabelValue( 5, u"Comp 1/P1" )
        self.grid.SetColLabelValue( 6, u"Comp 2/P2" )
        self.grid.SetColLabelValue( 7, u"Comp 3/P3" )
        self.grid.SetColLabelValue( 8, u"Comp 4/P4" )
        self.grid.SetColLabelValue( 9, u"H5Path" )
        self.grid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )


    # Grid CheckBox        
        self.gridattr = wx.grid.GridCellAttr()
        self.gridattr.SetEditor(wx.grid.GridCellBoolEditor())
        #self.gridattr = wx.grid.GridCellAttr()
        #self.gridattr.SetEditor(wx.grid.GridCellBoolEditor())
        self.gridattr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.grid.SetColAttr(0,self.gridattr)
        self.grid.SetColSize(0,40)

	# Rows
        self.grid.EnableDragRowSize( True )
        self.grid.SetRowLabelSize( 80 )
        self.grid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )
        self.gridDict = { u"Date": 'unix_timestamp' , u"Session": 'session' , 
                u"Author": 'author' , u"Base": 'component0'
                , u"Comp 1/P1":  'component1' , u"Comp 2/P2": 'component2'
                , u"Comp 3/P3": 'component3' 
                , u"Comp 4/P4": 'component4', u"H5Path":'dataArrRef' }
   #def OnInit(self):
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK,self.onMouse)
        self.grid.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)

        self.rowChecked = set([])
 #----------------------------------------------------------------------
    def onSingleSelect(self, event):
        """
        Get the selection of a single cell by clicking or 
        moving the selection with the arrow keys
        """
        global extraRows
        print ("You selected Row %s, Col %s" % (event.GetRow(),
                                               event.GetCol()))
        self.currentlySelectedCell = (event.GetRow(),
                                      event.GetCol())
        if event.GetCol() == 0:
        #if True:
               extraRows = []
               wx.CallAfter(self.grid.EnableCellEditControl)
               #wx.CallAfter(wx.grid.Grid.EnableCellEditControl)
               #wx.CallLater(100,self.toggleCheckBox)
        event.Skip()
    #------------------------------------------------------------
    #def onDragSelection(self, event):
    #    """
    #    Gets the cells that are selected by holding the left
    #    mouse button down and dragging
    #    """
    #    if self.myGrid.GetSelectionBlockTopLeft():
    #        top_left = self.myGrid.GetSelectionBlockTopLeft()[0]
    #        bottom_right = self.myGrid.GetSelectionBlockBottomRight()[0]
    #        self.printSelectedCells(top_left, bottom_right)
    # 
    #----------------------------------------------------------------------
            # TODO - Get selection by checkbox on the grid rows

    def onMouse(self,evt):
           print ("Event : Mouse ")
           if evt.Col == 0:
               wx.CallLater(250,self.toggleCheckBox)
           evt.Skip()
   
    def toggleCheckBox(self):
        #   if self.cb != None:
             self.cb.Value = not self.cb.Value
             print ("Toggle check box")
             self.afterCheckBox(self.cb.Value)
   
    #def onCellSelected(self,evt):
    #       if evt.Col == 1:
    #           wx.CallAfter(self.EnableCellEditControl)
    #       evt.Skip()
   
    def onEditorCreated(self,evt):
           print ("Event : onEditorCreated", evt.Col)
           if evt.Col == 0:
#               self.m_gridDataTable.EnableEditing(True)
               self.cb = evt.Control
               self.cb.WindowStyle |= wx.WANTS_CHARS
               self.cb.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
               self.cb.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
           evt.Skip()
   
    def onKeyDown(self,evt):
           if evt.KeyCode == wx.WXK_UP:
               if self.grid.GridCursorRow > 0:
                   self.grid.DisableCellEditControl()
                   self.grid.MoveCursorUp(False)
           elif evt.KeyCode == wx.WXK_DOWN:
               if self.grid.GridCursorRow < (self.NumberRows-1):
                   self.grid.DisableCellEditControl()
                   self.grid.MoveCursorDown(False)
           elif evt.KeyCode == wx.WXK_LEFT:
               if self.grid.GridCursorCol > 0:
                   self.grid.DisableCellEditControl()
                   self.grid.MoveCursorLeft(False)
           elif evt.KeyCode == wx.WXK_RIGHT:
               if self.grid.GridCursorCol < (self.NumberCols-1):
                   self.grid.DisableCellEditControl()
                   self.grid.MoveCursorRight(False)
           else:
               evt.Skip()
   
    def onCheckBox(self,evt):
          self.afterCheckBox(evt.IsChecked())
   
    def afterCheckBox(self,isChecked):
           global extraRows
           print ('afterCheckBox',self.grid.GridCursorRow,isChecked)
           key = self.grid.GridCursorRow
           extraRows = []
           if isChecked and key not in self.rowChecked:
              self.rowChecked.add(key) 
           elif key in self.rowChecked:
              self.rowChecked.remove(key) 

#           self.grid.EnableEditing(False)

    #-------------------------------------

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

        self.sel_date = None
        self.sel_date2 = None

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
        self.db_radioBtnDate = xrc.XRCCTRL(self.panelDB, 'm_radioBtnDate')
        self.db_dateStart = xrc.XRCCTRL(self.panelDB, 'm_datePickerStart')
        print(self.db_dateStart)
        self.db_dateEnd = xrc.XRCCTRL(self.panelDB, 'm_datePickerEnd')
        print(self.db_dateEnd)
        self.m_gridDataTable = xrc.XRCCTRL(self.panelDBTbl, "m_gridDataTable")
        self.dbt_buttonPlot = xrc.XRCCTRL(self.panelDBTbl, "dbt_buttonPlot")
        self.dbt_buttonExport = xrc.XRCCTRL(self.panelDBTbl, "dbt_buttonExport")
        self.dbt_buttonPrev = xrc.XRCCTRL(self.panelDBTbl, "m_buttonPrev")
        self.dbt_buttonNext = xrc.XRCCTRL(self.panelDBTbl, "m_buttonNext")
        self.dbt_checkBoxS11 = xrc.XRCCTRL(self.panelDBTbl, 'm_checkBoxS11P')
        self.dbt_checkBoxS21 = xrc.XRCCTRL(self.panelDBTbl, 'm_checkBoxS21P')
        self.dbt_checkBoxS12 = xrc.XRCCTRL(self.panelDBTbl, 'm_checkBoxS12P')
        self.dbt_checkBoxS22 = xrc.XRCCTRL(self.panelDBTbl, 'm_checkBoxS22P')

        self.db_buttonPlot2 = xrc.XRCCTRL(self.panelDB, "m_buttonPlot2")
        self.db_buttonExport2 = xrc.XRCCTRL(self.panelDB, "m_buttonExport2")
	# Grid
        self.myGrid = self.m_gridDataTable
        print (type(self.m_gridDataTable ))
        self.m_gridDataTable.CreateGrid( 20, 10 )
        self.m_gridDataTable.EnableEditing( True )
        self.m_gridDataTable.EnableGridLines( True )
        self.m_gridDataTable.EnableDragGridSize( False )
        self.m_gridDataTable.SetMargins( 0, 10 )
        self.m_gridDataTable.MakeCellVisible(11,10)
  

	# Columns
        self.m_gridDataTable.EnableDragColMove( False )
        self.m_gridDataTable.EnableDragColSize( True )
        self.m_gridDataTable.SetColLabelSize( 30 )
        self.m_gridDataTable.SetColLabelValue( 0, u"Sel" )
        self.m_gridDataTable.SetColLabelValue( 1, u"Date" )
        self.m_gridDataTable.SetColLabelValue( 2, u"Session" )
        self.m_gridDataTable.SetColLabelValue( 3, u"Author" )
        self.m_gridDataTable.SetColLabelValue( 4, u"Base" )
        self.m_gridDataTable.SetColLabelValue( 5, u"Comp 1/P1" )
        self.m_gridDataTable.SetColLabelValue( 6, u"Comp 2/P2" )
        self.m_gridDataTable.SetColLabelValue( 7, u"Comp 3/P3" )
        self.m_gridDataTable.SetColLabelValue( 8, u"Comp 4/P4" )
        self.m_gridDataTable.SetColLabelValue( 9, u"H5Path" )
        self.m_gridDataTable.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )


    # Grid CheckBox        
        self.gridattr = wx.grid.GridCellAttr()
        self.gridattr.SetEditor(wx.grid.GridCellBoolEditor())
        #self.gridattr = wx.grid.GridCellAttr()
        #self.gridattr.SetEditor(wx.grid.GridCellBoolEditor())
        self.gridattr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.m_gridDataTable.SetColAttr(0,self.gridattr)
        self.m_gridDataTable.SetColSize(0,40)

	# Rows
        self.m_gridDataTable.EnableDragRowSize( True )
        self.m_gridDataTable.SetRowLabelSize( 80 )
        self.m_gridDataTable.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )
        self.gridDict = { u"Date": 'unix_timestamp' , u"Session": 'session' , 
                u"Author": 'author' , u"Base": 'component0'
                , u"Comp 1/P1":  'component1' , u"Comp 2/P2": 'component2'
                , u"Comp 3/P3": 'component3' 
                , u"Comp 4/P4": 'component4', u"H5Path":'dataArrRef' }

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
         
        try:
          home = str(Path.home())
        except:
          home = "C:\Work"
        self.dataBaseName = "ExperData_Aaron" #"dataFile0"
        self.dataBasePath = home + "/Desktop/Data/Materials" #"../dataDir"

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

        self.db_buttonPlot2.Bind( wx.EVT_BUTTON, self.dbt_buttonPlotClick )
        self.dbt_buttonPlot.Bind( wx.EVT_BUTTON, self.dbt_buttonPlotClick )
        self.dbt_buttonExport.Bind( wx.EVT_BUTTON, self.dbt_buttonExportClick)

        self.dbt_buttonNext.Bind( wx.EVT_BUTTON, self.dbt_buttonNextClick )
        self.dbt_buttonPrev.Bind( wx.EVT_BUTTON, self.dbt_buttonPrevClick )

        self.vna_buttonVNATest.Bind( wx.EVT_BUTTON, self.vna_buttonVNATestOnButtonClick)

        ###### Grid selection events
        self.m_gridDataTable.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
#        self.m_gridDataTable.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.onCellSelected)
#        self.m_gridDataTable.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.onDragSelection) 
        self.m_gridDataTable.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK,self.onMouse)
        self.m_gridDataTable.Bind(wx.grid.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)
        # Setup first call
        #wx.CallAfter(self.m_gridDataTable.EnableCellEditControl)


        #dpc1 = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        #sizer.Add(dpc1, 0, wx.ALL, 50)
        self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChangedStart, self.db_dateStart)
        self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChangedEnd, self.db_dateEnd)

        self.rowChecked = set([])
        self.cb = None
        self.frameMain.Show(True)
        self.state  = StateO(StateO.IDLE)
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

        self.expr_BaseComment.WriteText("Non Ionized")
        self.expr_volume.WriteText("70")
        #self.m_gridDataTable.AppendRows(1)
        self.rows = None      
        return True
 #----------------------------------------------------------------------
    
    def onSingleSelect(self, event):
        """
        Get the selection of a single cell by clicking or 
        moving the selection with the arrow keys
        """
        print ("You selected Row %s, Col %s" % (event.GetRow(),
                                               event.GetCol()))
        self.currentlySelectedCell = (event.GetRow(),
                                      event.GetCol())
        if event.GetCol() == 0:
        #if True:
               wx.CallAfter(self.m_gridDataTable.EnableCellEditControl)
               #wx.CallAfter(wx.grid.Grid.EnableCellEditControl)
               #wx.CallLater(100,self.toggleCheckBox)
        event.Skip()
    #------------------------------------------------------------
    #def onDragSelection(self, event):
    #    """
    #    Gets the cells that are selected by holding the left
    #    mouse button down and dragging
    #    """
    #    if self.myGrid.GetSelectionBlockTopLeft():
    #        top_left = self.myGrid.GetSelectionBlockTopLeft()[0]
    #        bottom_right = self.myGrid.GetSelectionBlockBottomRight()[0]
    #        self.printSelectedCells(top_left, bottom_right)
    # 
    #----------------------------------------------------------------------
            # TODO - Get selection by checkbox on the grid rows

    def onMouse(self,evt):
           print ("Event : Mouse ")
           if evt.Col == 0:
               wx.CallLater(250,self.toggleCheckBox)
           evt.Skip()
   
    def toggleCheckBox(self):
        #   if self.cb != None:
             self.cb.Value = not self.cb.Value
             print ("Toggle check box")
             self.afterCheckBox(self.cb.Value)
   
    #def onCellSelected(self,evt):
    #       if evt.Col == 1:
    #           wx.CallAfter(self.EnableCellEditControl)
    #       evt.Skip()
   
    def onEditorCreated(self,evt):
           print ("Event : onEditorCreated", evt.Col)
           if evt.Col == 0:
#               self.m_gridDataTable.EnableEditing(True)
               self.cb = evt.Control
               self.cb.WindowStyle |= wx.WANTS_CHARS
               self.cb.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
               self.cb.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
           evt.Skip()
   
    def onKeyDown(self,evt):
           if evt.KeyCode == wx.WXK_UP:
               if self.m_gridDataTable.GridCursorRow > 0:
                   self.m_gridDataTable.DisableCellEditControl()
                   self.m_gridDataTable.MoveCursorUp(False)
           elif evt.KeyCode == wx.WXK_DOWN:
               if self.m_gridDataTable.GridCursorRow < (self.NumberRows-1):
                   self.m_gridDataTable.DisableCellEditControl()
                   self.m_gridDataTable.MoveCursorDown(False)
           elif evt.KeyCode == wx.WXK_LEFT:
               if self.m_gridDataTable.GridCursorCol > 0:
                   self.m_gridDataTable.DisableCellEditControl()
                   self.m_gridDataTable.MoveCursorLeft(False)
           elif evt.KeyCode == wx.WXK_RIGHT:
               if self.m_gridDataTable.GridCursorCol < (self.NumberCols-1):
                   self.m_gridDataTable.DisableCellEditControl()
                   self.m_gridDataTable.MoveCursorRight(False)
           else:
               evt.Skip()
   
    def onCheckBox(self,evt):
          self.afterCheckBox(evt.IsChecked())
   
    def afterCheckBox(self,isChecked):
           print ('afterCheckBox',self.m_gridDataTable.GridCursorRow,isChecked)
           key = self.m_gridDataTable.GridCursorRow

           if isChecked and key not in self.rowChecked:
              self.rowChecked.add(key) 
           elif key in self.rowChecked:
              self.rowChecked.remove(key) 

#           self.m_gridDataTable.EnableEditing(False)
    

    #----------------------------------------------------------------------
    def getGridSelectedRows(self, extra =[], maxRows =10, sparam="S21"):
        """
        Get whatever cells are currently selected
        """
        global gridFrame
        if gridFrame != None:
           print("Selected cells:{}".format(gridFrame.rowChecked))
           self.rowChecked = gridFrame.rowChecked
        else:
           print("Selected cells:{}".format(self.rowChecked))
           
        rowCList = list(self.rowChecked) + extra
        rowCList.sort()
        if len(rowCList) > maxRows:
           rowsCList = rowsCList[-maxRows:]

        rowCList.append(-1)
        print("Selected sort cells:{}".format(rowCList))
        rows_start = -1
        rows_end = -1
        freqL = []
        clist = []
        labels = []
        for rowIdx in rowCList:
          print (rowIdx, rows_start, rows_end)
          if rows_start == -1:
            rows_start = rowIdx
            rows_end = rowIdx + 1
          elif rows_end < rowIdx or rowIdx == -1: 
#              if rowsIdx == -1: rows_end +=1
              print (rows_start, rows_end)
              freqL, clist_ = self.hdStore.getRowsFreqData( self.rows, range(rows_start, rows_end), sparam)
              for rowidx in range(rows_start, rows_end):
                st = self.rows.loc[rowidx]['misc'].decode('utf-8')
                print (st, type(st))
                labels.append(hd5Mod.extractLabelFromPath( st) )

              clist = clist + clist_
              rows_start = rowIdx 
              rows_end = rowIdx + 1
          else:
              rows_end = rowIdx + 1
        return freqL, clist, labels

    def dbt_buttonNextClick(self, event):
       #TODO
       pass 

    def dbt_buttonPrevClick(self, event):
       #TODO
       pass

  #############################################################
  #
  # func dbt_buttonExportClick
  # In: data Tab - Export Button Event 
  #
  #############################################################
    def dbt_buttonExportClick(self, event):
        print("Press Export")
        print ("Doing import test")
        self.hdStore.importMergeHdf5("/home/samplab/Desktop/Data/Materials/test1.h5", "/lab0","")
        '''
        freqL, clist, labels = self.getGridSelectedRows()
        print("number of pLots:{}".format(len(clist)))
        print(labels) 
        dictSave = {}
        for data, label in zip (clist, labels): 
           dictSave[label] = data
        dictSave['freq'] = freqL
        fileName = "experData_" + samplePlot.fullTimeLogPostfix() + ".mat"
        sio.savemat(fileName, dictSave)
        '''

    def dbt_buttonPlotClick(self, event):
        global sparamSel


        clist = []
        if int(self.dbt_checkBoxS11.GetValue()) == 1:
           sparamS = sparamSel[0]
           freqL, clist, labels = self.getGridSelectedRows(sparam=sparamSel[0])

        if int(self.dbt_checkBoxS21.GetValue()) == 1:
           sparamS = sparamSel[1]
           freqL, clist, labels = self.getGridSelectedRows(sparam=sparamSel[1])

        if len(clist)>0:
          print("number of pLots {}:{}".format(sparamSel[0], len(clist)))
          print(labels) 
          samplePlot.plotMeasLabels(freqL, clist, labels, sparamS) 

     #----------------------------------------------------------------------
        


    def printSelectedCells(self, top_left, bottom_right):
        """
        Based on code from http://ginstrom.com/scribbles/2008/09/07/getting-the-selected-cells-from-a-wxpython-grid/
        """
        cells = []
 
        rows_start = top_left[0]
        rows_end = bottom_right[0]
 
        cols_start = top_left[1]
        cols_end = bottom_right[1]
 
        rows = range(rows_start, rows_end+1)
        cols = range(cols_start, cols_end+1)
 
        cells.extend([(row, col)
            for row in rows
            for col in cols])
 
        print ("You selected the following cells: ", cells)
 
        for cell in cells:
            row, col = cell
            print (self.myGrid.GetCellValue(row, col))



     #----------------------------------------------------------------------
    def msgLabStep(self, i, msg=''):
      res = False
      if msg == '':
        if i==1:
          self.m_listBox1.Clear()
        #self.m_listBox1.Append(messages.fixedVolMsgStep[i].format(self.expr['material1'], self.expr['volumeExchange'] ))
          msg = messages.fixedVolMsgStep[i].format(self.expr['component1'], self.expr['_volumeExchange'] )
          
        else:
          self.m_listBox1.Clear()
          #self.m_listBox1.Append( messages.fixedVolMsgStep[i])
          msg =  messages.fixedVolMsgStep[i]

      self.m_listBox1.Append( msg) 
      if i == 0 and "Measurment Do" in msg:
        res = self.msgLabExperResultYN()
      else:
        wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)
      return res

    def msgLabExperResultYN(self):
         dlg = wx.MessageDialog(None, "Save Experiment Results (OK)?",'Result OK', 
                 wx.YES_NO | wx.NO_DEFAULT|wx.ICON_QUESTION)
         if dlg.ShowModal() == wx.ID_YES:
            return True
         else:
            return False
  

# Virtual event handlers, overide them in your derived class
     #----------------------------------------------------------------------
    def OnDateChangedStart(self, evt):
        self.sel_date = evt.GetDate()
        self.sel_date2 = evt.GetDate()
        self.db_dateEnd.SetValue(self.sel_date)
        print (self.sel_date.Format("%d-%m-%Y"))

    def OnDateChangedEnd(self, evt):
        self.sel_date2 = evt.GetDate()
        print (self.sel_date2.Format("%d-%m-%Y"))

     #----------------------------------------------------------------------


  #############################################################
  #
  # func db_buttonSearchOnButtonClick
  # In: data Tab - Search Button Event 
  #
  #############################################################

    def db_buttonSearchOnButtonClick(self, event):
        # TODO - add table presentation option
        param = 0
        param2 = 0
        sp = 0   # TODO Add sparam selection
        cmd = '@All'
        if (self.db_radioTime_Today.GetValue()):
            cmd = '@Today'
        elif (self.db_radioBtnTimeLastHour.GetValue()):
            cmd = '@LastHour'
            param = 1
        elif (self.db_radioBtnTime_All.GetValue()):
            cmd = '@All'
        elif (self.db_radioBtnTime_Min.GetValue()):
            cmd = '@LastMinutes'
            try:
              paramS = self.db_textCtrlDBNumMinutes.GetValue()
              param = int(paramS)
            except ValueError:
              print ("Wrong value in Minuts text")
        elif (self.db_radioBtnDate.GetValue()):
            print(self.db_dateStart.GetValue()) #Format("%d-%m-%Y"))
            dateStart = self.db_dateStart.GetValue()
            dateEnd = self.db_dateEnd.GetValue()
            print(type(dateStart))
            if dateStart == dateEnd:
               date_object = _wxdate2pydate(dateStart)
               print(date_object)
               t = datetime.time(hour=0, minute=00)
               dateStart = datetime.datetime.combine(date_object, t)
#               t2 = datetime.time(hour=23, minute=59)
#               dateEnd = datetime.datetime.combine(date_object, t2)
               dateDelta = datetime.timedelta(days=1)
               dateEnd = dateStart + dateDelta
               self.sel_date = _pydate2wxdate(dateStart)
               self.sel_date2 = _pydate2wxdate(dateEnd)
            cmd = '@Range'
            try:
              print (self.sel_date.Format("%s"))
              print (self.sel_date2.Format("%s"))
              param = int(self.sel_date.Format("%s")) 
              param2 = int(self.sel_date2.Format("%s")) 
              tDict = { cmd  : [param, param2]}
              if self.hdStore != None:
                self.rows = samplePlot.dbQueryExprTblByDict(self.hdStore, tDict)
              else: 
                pass # TODO - add error condition.
              #self.rows = samplePlot.dbQueryExprTblByDict(self.hdStore, cmd, parami)
            except ValueError:
              print ("Wrong value in Dates")
        
        

        
        nrows = min(MaxTblRows-1, len(self.rows))
        # TODO 0 check this for out of bound        
        self.dispOnGrid(self.rows, nrows)
        
        #self.dispOnFrameGrid(self.rows, nrows)

    def dispOnFrameGrid(self, rows, nrows):
        global gridFrame
        gridFrame = Frame(None)

        gridFrame.grid.EnableEditing(True)
        #nrows = min( gridFrame.GetNumRows(), len(self.rows))
        print (nrows)
        for i in range(nrows):
            dateStr = datetime.datetime.fromtimestamp(rows.loc[i]['unix_timestamp'])
            dataStr = dateStr.strftime("%d/%m/%y")
            gridFrame.grid.SetCellValue(i,1,str(dateStr))
            cell=rows.loc[i]
            print (cell.dtypes)
            print ("----------")
            for j in range(2,10):
                print (gridFrame.grid.GetColLabelValue( j))
                label = self.gridDict[gridFrame.grid.GetColLabelValue( j)]
                print (label, type(cell[label]))
                if  isinstance(cell[label], type(bytes())):
                  if "component" in label and label[-1] != '0':
                    compStr = cell[label].decode('utf-8')
                    idx = label[-1]
                    if len(compStr)>0:
                      field = compStr + '/' + str(cell['P'+idx])
                    else: field = ""
                  else:
                    field = cell[label].decode('utf-8')
                  print(field)
                  gridFrame.grid.SetCellValue(i,j,field)
                #if  cell[label].dtype in 'int' or  cell[label].dtype in 'float':
                else:
                  print(cell[label])
                  gridFrame.grid.SetCellValue(i,j,str(cell[label]))
#        self.m_gridDataTable.EnableEditing(False)
        gridFrame.Show()

    def dispOnGrid(self, rows, nrows):
        self.m_gridDataTable.EnableEditing(True)
        #nrows = min( self.m_gridDataTable.GetNumRows(), len(self.rows))
        print (nrows)
        for i in range(nrows):
            self.m_gridDataTable.MakeCellVisible(11,10)
            dateStr = datetime.datetime.fromtimestamp(rows.loc[i]['unix_timestamp'])
            dataStr = dateStr.strftime("%d/%m/%y")
            self.m_gridDataTable.SetCellValue(i,1,str(dateStr))
            cell=rows.loc[i]
            print (cell.dtypes)
            print ("----------")
            for j in range(2,10):
                print (self.m_gridDataTable.GetColLabelValue( j))
                label = self.gridDict[self.m_gridDataTable.GetColLabelValue( j)]
                print (label, type(cell[label]))
                if  isinstance(cell[label], type(bytes())):
                  if "component" in label and label[-1] != '0':
                    compStr = cell[label].decode('utf-8')
                    idx = label[-1]
                    if len(compStr)>0:
                      field = compStr + '/' + str(cell['P'+idx])
                    else: field = ""
                  else:
                    field = cell[label].decode('utf-8')
                  print(field)
                  self.m_gridDataTable.SetCellValue(i,j,field)
                #if  cell[label].dtype in 'int' or  cell[label].dtype in 'float':
                else:
                  print(cell[label])
                  self.m_gridDataTable.SetCellValue(i,j,str(cell[label]))
#        self.m_gridDataTable.EnableEditing(False)

     #----------------------------------------------------------------------
    def getVNAFields(self):    
      try:
        self.nPoints = int(self.vna_textNumSamplePoints.GetValue())
        self.nScans = int(self.vna_textCtrlNumScans.GetValue())
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


     #----------------------------------------------------------------------
    def getExperFields(self):  
      print ("DBG: start of get Fields") 
      print ( int(time.time()))
      self.expr['unix_timestamp'] = int(time.time())
      self.expr['author'] = self.m_textTester.GetValue()
      self.expr['misc'] = self.m_textNotes.GetValue()
      self.session = self.m_textSession.GetValue()
      self.expr['session'] = int(self.m_textSession.GetValue())

      print ("Tester Name:"+self.expr['author'])
      print ("Test Notes:"+ self.expr['misc'])
      print ("Session:" + self.session)

      self.expr['volume'] = self.expr_volume.GetValue()

      print ("volume:" + self.expr['volume'])
      self.expr['component0'] = self.expr_testBase.GetSelection()
      self.expr['component1'] = self.expr_comp1.GetValue()
      self.expr['component2'] = self.expr_comp2.GetValue()
      self.expr['component3'] = self.expr_comp3.GetValue()
      self.expr['component4'] = self.expr_comp4.GetValue()
      self.expr['component5'] = "" #TODO update

      self.expr['component0'] = 'Water' #TODO
      print("Test Base:" + str(self.expr['component0']))
      if len(self.expr['author']) == 0:
         self.expr['author'] = 'NA'

      self.expr['title'] = str(self.expr['component0']) + self.expr['volume'] +self.expr['author'] 

      print("Title:" + str(self.expr['title']))

      self.expr['P0_volume'] = self.expr_BaseComment.GetValue()
      if len(self.expr_P1.GetValue()) >0:
         self.expr['P1'] = int(self.expr_P1.GetValue())
      if len(self.expr_P2.GetValue()) >0:
         self.expr['P2'] = int(self.expr_P2.GetValue())
      if len(self.expr_P3.GetValue()) >0:
         self.expr['P3'] = int(self.expr_P3.GetValue())
      if len(self.expr_P4.GetValue()) >0:
         self.expr['P4'] = int(self.expr_P4.GetValue())
      self.expr['P5'] = "0"#TODO update

      self.expr['numberOfComponents'] = 1 #TODO comp_sum(self.expr)

      self.expr['_stepUpDn'] = self.m_choiceStep.GetSelection()
      print("step:" + str(self.expr['_stepUpDn']))
      self.expr['_Procedure'] = self.m_choiceProcedure.GetSelection()
      print("Test Procedure:" + str(self.expr['_Procedure']))

      self.expr['_InitVolume'] =  self.m_textInitialVol.GetValue()
      print ("initialVol:" + self.expr['_InitVolume'])
      self.expr['numberOfMeasurements'] = self.m_textNumMeasures.GetValue()
      print (self.expr['numberOfMeasurements'])
      self.expr['_concenDelta'] = self.m_textConcenDelta.GetValue() 
      print (self.expr['_concenDelta'])
      self.expr['_initConcentrate'] = "0.1" # TODO -checkthis
#      print (w.Text_InitConcen.get("1.0","end-1c"))
      self.expr['_volumeExchange'] = self.m_textPepetoVolEx.GetValue()
      print (self.expr['_volumeExchange'])

     #----------------------------------------------------------------------
    def openFileClickCommon(self, filepath):

      filename = os.path.basename(filepath)
      filepath = filepath[:-len(filename)-1]
      if filepath == '':
            filename = self.dataBaseName
            filepath = self.dataBasePath
#      if filename == "ExperData_Aaron": #"dataFile0"
#        sparamSel = sparamArr[1]
#      else:      
      #sparamSel = vesionParams["sparamKeys"][1] #TODO - this should be 0 for S21

      print ("DB Open file event:" + filepath + "~~" + filename)
      
      filters1=tables.Filters(complevel=0)
      restore = True
      try:
          dlg = wx.MessageDialog(None, "File already exists, do you want to overwrite it?",'Overwrite', wx.YES_NO | wx.NO_DEFAULT|wx.ICON_QUESTION)
          self.hdStore = hd5Mod.hdf5DataTable(filters=filters1, path=filepath, dataBase_=filename, restore=restore, console=False,guidlg=dlg)
      except Exception as e:
          print(e, str(e))
          print("DB Exception" )
          self.db_button6DBFileOpen.SetBackgroundColour('gray')
          self.vna_button6DBFileOpen.SetBackgroundColour('gray')
          return  
      # End of While 
      self.db_button6DBFileOpen.SetBackgroundColour('blue')
      self.vna_button6DBFileOpen.SetBackgroundColour('blue')
  #############################################################
  #
  # func vna_buttonDBFileOpenClick
  # In: VNA Tab - Open data base file event 
  #
  #############################################################
  
    def vna_buttonDBFileOpenClick(self, event):
      filepath = self.vna_textCtrlDBFile.GetValue()
      self.db_textCtrlDBFile.SetValue(filepath)
      self.openFileClickCommon(filepath)


  #############################################################
  #
  # func db_buttonDBFileOpenClick
  # In: DataBase Tab - Open data base file event 
  #
  #############################################################

    def db_buttonDBFileOpenClick(self, event):
      filepath = self.db_textCtrlDBFile.GetValue()
      self.vna_textCtrlDBFile.SetValue(filepath)
      self.openFileClickCommon(filepath)

  #############################################################
  #
  # func m_buttonConnectOnButtonClick
  # In: VNA Tab - Connect to VNA Button Event 
  #
  #############################################################

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
          print ("Raw:", res)
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


  #############################################################
  #
  # func m_buttonStopOnButtonClick
  # In: ExperimentTab - Stop Button Event 
  #
  #############################################################

    def m_buttonStopOnButtonClick( self, event ):
       global extraRows

       extraRows = []
       print ("End of Test")
#      event.Skip()
       print('LabExper0_support.btnDonePress')
       sys.stdout.flush()
       self.state  = self.state.IDLE
       #currSess = rfSystem.maxsess
       #rfSystem.maxsess += 1
       #w.Text_Session.delete(1.0, tk.END)
       #w.Text_Session.insert(1.0, str(rfSystem.maxsess))
       #w.btnStart.configure(background=orig_color)


       #self.m_listBox1.Clear()
       #self.m_listBox1.Append("Test Session End\n==========")

       self.msgLabStep(0, msg="Test Session End\n==========")

       #rfSystem.getDataPlot('Session', currSess)



  #############################################################
  #
  # func m_buttonContOnButtonClick
  # In: ExperimentTab - Continue Button Event 
  #
  #############################################################

    def m_buttonContOnButtonClick( self, event ):
      if self.state == self.state.IDLE:
         print("Error - Need to start session first")
         return
      print('LabExper0_support.btnContinuePress')
#      if self.state != 2:
      if self.state != self.state.MEAS_WAIT_CONT:
       print ("Wrong state")
       return
      self.msgLabStep(1)
      self.state = self.state.START
      sys.stdout.flush()
      self.expr['_testNumber'] -= 1
      tidx = -self.expr['_testNumber'] + self.numM + 1
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




  #############################################################
  #
  # func vna_buttonVNATestOnButtonClick
  # In: vna tab - Test VNA Button Event - to test VNA operation
  #
  #############################################################
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
         enaSetup, ndarry = samplePlot.measureRemoteCall(self.rpcClient, gEna, plot=True)
 

   
 
  #############################################################
  #
  # func m_buttonMeasureOnButtonClick
  # In: ExperimentTab - Measurement Button Event 
  #
  #############################################################

    def m_buttonMeasureOnButtonClick( self, event ):
      global gEna
      global extraRows
      global sparamSel
      print ("Measure Button Presses")
      #event.Skip()
      print('LabExper0_support.btnMeasurePress')
      sys.stdout.flush()
      if self.state != self.state.START:
        print("Error - Need to start session first")
        return
      ############################3
      #TODO - update setup fields
      #############################3
      self.getExperFields()
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
         enaSetupRes, ndarryRes = samplePlot.measureRemoteCall(self.rpcClient, gEna )
         ##
         #TODO - change from gui search to db search??
         self.db_buttonSearchOnButtonClick(None)
         print("Try to select")
         #self.currentlySelectedCell = ( len(self.rows)-1 , 0)
         #wx.CallAfter(self.grid.EnableCellEditControl)

         #wx.PostEvent(self.GetEventHandler(), wx.PyCommandEvent(wx.EVT_GRID_LEFT_CLICKBUTTON.typeId, self.GetId()))
         #wx.CallAfter(self.m_gridDataTable.EnableCellEditControl)

         #key = self.m_gridDataTable.GridCursorRow
         lastRowSel = len(self.rows)-1
         print ("last Row added:" , lastRowSel)
         extraRows.append(lastRowSel)


         freqL, clist, labels = self.getGridSelectedRows(extra=extraRows, sparam=sparamSel[0])
         #pdb.set_trace()
         if len(freqL) == 0:
           freqL = ndarryRes['ff']
         arrOffsetStart = ndarryRes['offset'][sparamSel[0]]
         arrOffsetEnd = arrOffsetStart + ndarryRes['offset']['Step']

         clist.append(ndarryRes['raw'][:,arrOffsetStart:arrOffsetEnd ])
        
         labels.append(self.expr['misc'])
         _, clist2, _ = self.getGridSelectedRows(extra=extraRows, sparam=sparamSel[1])
         arrOffsetStart = ndarryRes['offset'][sparamSel[1]]
         arrOffsetEnd = arrOffsetStart + ndarryRes['offset']['Step']

         clist2.append(ndarryRes['raw'][:,arrOffsetStart:arrOffsetEnd ])


         
         print("Measure: number of pLots:{}".format(len(clist)))
         print(labels) 
         if len(clist)>0:
           samplePlot.plotMeasLabelsLog(freqL, clist, clist2, labels, sparamSel) 


      res = False
      if self.state == self.state.START:
        res = self.msgLabStep(0)
      if res:
         #
         ##### Store results 
         #
         self.hdStore.aggParams2TableWrite(self.expr, ndarryRes, enaSetupRes, grp='/lab0')

      self.state = self.state.MEAS_WAIT_CONT




  #############################################################
  #
  # func m_buttonStartOnButtonClick
  # In: ExperimentTab - Start Button Event 
  #
  #############################################################

    def m_buttonStartOnButtonClick( self, event ):

      global extraRows

      extraRows = []
      print ("Start Button Press")
      #event.Skip()
      if self.state != self.state.IDLE:
        print ("Wrong State Error")
        return
      print('LabExper0_support. Start the Experiment')
      try:
        self.getExperFields()
        #self.session = self.m_textSession.GetValue()
        print(self.session)
        self.maxsess = int(self.session)
        self.expr['numberOfMeasurements'] = int(self.m_textNumMeasures.GetValue())
        print (self.expr['numberOfMeasurements'])
         #TODO check this
        self.expr['_testNumber'] = int(self.expr['numberOfMeasurements'])
        self.numM = self.expr['_testNumber']
        self.m_gauge1.SetRange(self.numM)
      except:
        print ("Exception in number parse")
        pass
      tidx = - self.expr['_testNumber'] + self.numM+1
      self.m_gauge1.SetValue(tidx)
#      w.TextTestNum.insert("1.0",str(tidx)+"/"+str(expr['numM']))
      for k, i in self.expr.items():
          if (type(i) == type(str)) and len(i) == 0:
              print ("Illegal parameter: " + k)
          else:
            if k=='numberOfMeasurements' or k=='initialVol':
              try:
                self.expr[k]= float(i)
              except ValueError:
                print ("Wrong value in {}-- Please Correct ".format(k))
                return
      self.state = self.state.START
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
    #gridFrame = Frame(None)
    #gridFrame.Show()
    appframe.MainLoop()

