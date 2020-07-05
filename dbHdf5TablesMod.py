# http://mtweb.cs.ucl.ac.uk/mus/martha/PythonPackages/tables-3.0.0rc2/doc/html/usersguide/tutorials.html
# https://www.pytables.org/usersguide/tutorials.html
# 19-Aug-2019 : TODO add test where file is remained open for the duration of the test
import h5py
import numpy as np
import tables
# import PyTables
import time
import datetime

import sys
import os
import shutil

from tables.group import RootGroup
#from typing import Any, Union
import pandas as pd
from pathlib import Path

#SAMPLE_SHAPE = (2, 402)
MAX_SESS_SAMPLES = 100
defaultPath = "dataDir"
dataBaseName = "dataFile0"
Filters = None

paramV0_0 = { "Major":0, "Minor":0, "Date":"1-Dec-2019", "Notes": "Used for old data -for testing software only", "sparamKeys": ["S21Mean", "S21Var"]  }
paramV0_1 = { "Major":0, "Minor":1, "Date":"1-June-2020", "Notes": "Used for new data - first version", "sparamKeys": ["S11", "S21"]  }


h5VersionArr = { "v0.0": paramV0_0, "v0.1": paramV0_1}

setUpP = {
    'time': None,
    'freqSt': '2GHZ',
    'freqEn': '3GHZ',
    'material': 'water',
    #  'concentrate' : 0.8
}


def unixTimePostfix(time):
    now = datetime.datetime.fromtimestamp(time)
    postfix = now.strftime("%Y/%m/%d_%H:%M:%S")
    return postfix

def extractLabelFromPath ( path):
       if path == None or len(path)==0:
         return "NA"
       print ("path" + path)
       if len(path)> 0 :
         l = len(path)-1
         print (l)
        # ridx = path[-1:0:-1].find['\\']
         while path[l] != '\\' and l>0: l -=1
       return path[l:]


class ExperimentTable(tables.IsDescription):
    #   unix_timestamp = tables.Time64Col(pos=0)
    unix_timestamp = tables.Int64Col(pos=0)
    session = tables.Int32Col(pos=1)
    author = tables.StringCol(20, pos=2)
    title = tables.StringCol(20, pos=3)
    experimentOK= tables.Int8Col( pos=4)
    volume= tables.Float32Col( pos=5)
    numberOfMeasurements = tables.Int16Col(pos=6)
    measurmentNumber = tables.Int16Col(pos=7)
    experimentOK = tables.BoolCol(pos=8)
    comment = tables.StringCol(50, pos=9)
    misc = tables.StringCol(50, pos=10)
    numberOfComponents= tables.Int16Col(pos=11)
    component0= tables.StringCol(20, pos=12)
    component1= tables.StringCol(20, pos=13)
    component2= tables.StringCol(20, pos=14)
    component3= tables.StringCol(20, pos=15)
    component4= tables.StringCol(20, pos=16)
    component5= tables.StringCol(20, pos=17)
    P0_volume= tables.StringCol(20, pos=18)
    P1= tables.Float32Col(pos=19)
    P2= tables.Float32Col(pos=20)
    P3= tables.Float32Col(pos=21)
    P4= tables.Float32Col(pos=22)
    P5= tables.Float32Col(pos=23)
    '''
    class Materials(tables.IsDescription):
      baseComponent: tables.StringCol(20)
      component1: tables.StringCol(20)
      component2: tables.StringCol(20)
      component3: tables.StringCol(20)
      component4: tables.StringCol(20)
      component5: tables.StringCol(20)
      P0: tables.Float32Col()
      P1: tables.Float32Col()
      P2: tables.Float32Col()
      P3: tables.Float32Col()
      P4: tables.Float32Col()
      P5: tables.Float32Col()
    ''' 
    dataArrRef = tables.StringCol(50, pos=24)
#TODO - add to attributes
#MagnitudePhase, <class 'str'>
#        NumberOfPoints: 801, <class 'numpy.uint16'>
#        STAR: 600000000, <class 'numpy.int32'>
#        STOP: 5400000000.0, <class 'numpy.float64'>
#        CENT: 3000000000.0, <class 'numpy.float64'>
#        SPAN: 4800000000.0, <class 'numpy.float64'>
#        dataFormat: ndarry shape: (1, 2), type:object
#        ff: ndarry shape: (801, 1), type:float64

 #numberOfMeasurements: tables.Int16Col()
#PauseBetweenMeasurements
#MeasurementNumber

#   sData = tables.Float64Col(shape=(SAMPLE_SHAPE), dflt=0.0)
# at =  tables.ComplexAtom(itemsize=8)
# sData = tables.AtomCol( at, shape=(SAMPLE_SHAPE), dflt=0.0)
# class arrs(tables.IsDescription):

# dtypeData = tables.Atom.from_dtype(np.dtype((np.float64, SAMPLE_SHAPE)))
# atom = tables.Atom.from_dtype(np.array(SAMPLE_SHAPE).dtype)
# Atom.from_dtype(numpy.dtype('float64'))
#   class numpyData(tables.IsDescription):
#    data = np.dtype(np.array([SAMPLE_SHAPE[0], SAMPLE_SHAPE[1]]))


class hdf5DataTable:

    def __init__(self, path = defaultPath, dataBase_=dataBaseName, filters=tables.Filters(complevel=0), restore=False, console=True, guidlg = None, version = "v0.1" ):
        self.data_dir = path
        self.Filters = filters
        self.f = None
        if os.path.exists(self.data_dir):
            pass  # shutil.rmtree(data_dir)
        else:
            os.mkdir(self.data_dir)
        filename = self.get_filename(dataBase_, filters)
        filename = os.path.join(self.data_dir, filename)
        self.filename = filename
        self.sparamSel =  h5VersionArr["v0.1"]["sparamKeys"]
        try:
          self.spramSel = h5VersionArr[version]["sparamKeys"]
        except:
          print("HDF5 Data : Error in Version Array")
          pass 
        if console and restore:
            self.printData('/lab0')
        else:
            import wx
            print ("hdf5 init) Create data Base:" + filename)
            if os.path.exists(filename):
                if console:
                  cmd = input("File %s already exists, do you want to erase it and start new?" % (filename))
                  if len(cmd)==0 or (len(cmd)> 0 and cmd[0] != 'y'):
                      #TODO - add exception here
                      return
                elif guidlg != None:
                   #Ex = ValueError("FileExistError")
                   #raise Ex
                  result = guidlg.ShowModal()
                  if result != wx.ID_YES:
                    return 
            self.filename = self.createPandasH5Table(self.data_dir, filename, ['lab0'], filters, version= h5VersionArr[version] )
       
        return
  

  #############################################################
  #
  # func createPandasH5Table
  # In:
  #   data_dir - hdf5 directory path base
  #   file_ - 
  #   locations - Experiment Table group path 
  #   filters - hdf5 file filter settings.
  #   version - Internal version of the dataBase .
  #
  # Create new Hdf5 data base file and its internal index table.
  #############################################################
    def createPandasH5Table(self, data_dir, file_, locations, filters, version = None):
        #    filename = self.get_filename(file_,filters)
        #    filename = os.path.join(data_dir, filename)
        #   hdstore = pd.HDFStore(FILENAME, "w")
        print("Creating file:", file_)
        loc = locations[0]
        print("H5 path :%s" % (loc))
        with tables.open_file(file_, "w", filters=filters) as f:
            flocate = f.create_group(f.root, loc)
            #table_lens = f.create_table(flocate, "exprTable", ExperimentTable())  # , maxshape=(10000,))
            table_lens = f.create_table(flocate, "exprTable", ExperimentTable)
            print ('Created table:')
            print (loc)
            if (version != None):
               table_lens.attrs.version = version
        #    table_lens.append([lens[col].values for col in table_lens.dtype.names])
        return file_

    def get_filename(self, file_, filters):
        if filters.complevel != 0:
            complib = filters.complib if ":" not in filters.complib else filters.complib.replace(":", "-")
            shuffle = "shuffle" if filters.shuffle else "noshuffle"
            filename = "%s_%s-%d-%s.h5" % (file_, complib, filters.complevel, shuffle)
        else:
            filename = file_ + ".h5"
        return filename

    def createEArrayTable(self, data_dir, filters, loc="dataArr"):
        global Filters
        if os.path.exists(data_dir):
            pass  # shutil.rmtree(data_dir)
        else:
            os.mkdir(data_dir)
        filename = self.get_filename(dataBaseName, filters)
        filename = os.path.join(data_dir, filename)
        # shape = (2, 802)
        # atom = tables.Atom.from_dtype(numpy.dtype((numpy.complex128, shape)))
        atom = tables.Atom.from_dtype(np.dtype(np.complex128))
        with tables.open_file(filename, "w", filters=filters) as f:

            table_lens = f.create_earray(f.root, loc, atom, (0, 802), "S1", filters)
            print ('Created table:')
            print (loc)
        Filters = filters
        return filename

    def printDat_It(self, rowit):
            i = 0
            print("unix_timestamp,    session       , Material , P__ , Notes, Data ")
            print("=====================================================")
            for x in rowit:  # tbl.iterrows():
                #      print(x[tbl[:])
                print("%-16s, %d, %10s, %0.4f, %-10s, %-20s" % (
                unixTimePostfix(x['unix_timestamp']), x['session'], x['component0'], x['P1'], "notes...",
                x['dataArrRef']))
                i += 1
                if i > 100:
                    break

    def printData(self, grp):
            print ("print table:%s" % (self.filename))
            f = tables.open_file(self.filename, "r", filters=self.Filters)
            print(list(f))
            #tbl = f.get_node(grp)  # type: Union[Union[RootGroup, object], Any]
            tbl = f.get_node(grp + "/exprTable")  # '/lab0')
            #print (type(tbl))
            print("Table %s" % (grp))
            #print( tbl.dtype.nbytes)
            ndt = np.dtype(tbl)
            print(ndt.itemsize)
            self.printDat_It(tbl.iterrows())
            #print("Table %s, len:%d" % (grp, len(tbl)))
            f.close()

    def getTblType(self, grp='/lab0'):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp + "/exprTable")  # '/lab0')
        ret = tbl.dtype
        f.close()
        return ret
  #############################################################
  #
  # func aggParams2TableWrite:
  # In:
  #   dbHdf - instance of class Hdf5TablesMod
  #   setUp - Dict with class 'ExperimentTable' fields and their values
  #   ndarry - Dict with numpy arrays of sampled data - 'raw', 'ff',  
  #            'offset'- dictionary offsets of Sparameters.
  #   enaAttr - vna machine setup attribures
  #   grp - hdf5 directory path base
  # global session
  #
  # Writes to HDF5 Tables all of the experiment fields
  # Adds to data coloumns - 'Mean', 'Std' 
  #
  #############################################################
    def aggParams2TableWrite(self, setUp, ndarry, enaAttr, grp='/lab0' ):
      global session


    # np.random.randn(dbHdf.SAMPLE_SHAPE[0],dbHdf.SAMPLE_SHAPE[1])
    # it = iter ([setUp]),
    # table_to_store = np.fromiter( dtype=dbHdf.experimentTable.dtype)
    # tODO 
    #nData = np.concatenate((ndarry['Mean'], ndarry['Std'], ndarry['raw']), axis=1)
      nData = ndarry['raw']
      print(nData.dtype, nData.shape)
      enaAttr['ff'] = ndarry['ff']
      enaAttr['offset'] = ndarry['offset']
      #now = datetime.datetime.fromtimestamp(time.time())
      now = datetime.datetime.fromtimestamp(setUp['unix_timestamp'])
      postfixDate = now.strftime("%Y%m%d")
      dataGrp = "data_" + postfixDate
      self.writeSamples('/lab0', setUp, dataGrp, nData, enaAttr)
      delta = 1


  #############################################################
  #
  # func importMergeHdf5
  # In:
  #   filenameNew - name of hdf5 file to merge with
  #   grp - hdf5 directory path base
  #   subgrp - (Not used) option for sub groups to merge with.
  # global session
  #
  # Merge to all HDF5 data into tables of the experiment fields 
  #  and reference data arrays
  #############################################################
    def importMergeHdf5(self, filenameNew, grp, subgrp):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp + "/exprTable")  # '/lab0')

        f2 = tables.open_file(filenameNew, "r", filters=self.Filters)
        tbl2 = f2.get_node(grp + "/exprTable")  # '/lab0')

        for row2 in tbl2.iterrows():
          #grpDataRaw =  row2['dataArrRef']
          rec = row2.fetch_all_fields()
          #print (rec)
          #print (rec.dtype) 
          newitem = tbl.row
           
          for k in rec.dtype.names:
            #print(rec[k])
            newitem[k] = rec[k]
          newitem.append()

          grpDataRaw =  row2['dataArrRef'].decode()
          grpData2 = Path(grpDataRaw)
          print ("H5PAth Link:" + grpDataRaw)
          if '/'+ grpDataRaw in f2:
            fdata2 = f2.get_node('/' + grpDataRaw)
            tblData2 = fdata2.read()
            #darray = f2.get_node('/' + datapath)
          
          print (grpData2.name)
          print (grpData2.parts)
          if "/" + grpData2.parts[0] not in f:
            print ("Create Data Group:" + grpData2.parts[0])
            fdataNew = f.create_group(f.root, grpData2.parts[0])
          else:
            fdataNew = f.get_node(f.root, grpData2.parts[0])
  
          newArrName = grpData2.name #TODO - should be the postfix of grpData withoht /datexxxx/
          print ("Create earray:" + newArrName)
          if "/" + grpDataRaw not in f:
            table_arr = f.create_earray(fdataNew, newArrName, obj=tblData2, filters=self.Filters)
            #newitem
            #newitem.append()
            print ("Copy data earray at:" + grpDataRaw)

            tbl.flush()
            table_arr.flush()
        f.close()
        f2.close()
        return


  #############################################################
  #
  # func writeSamples
  # In:
  #   grp - hdf5 directory path base
  #   grpData - Data Table group name
  #   setUp - Dict with class 'ExperimentTable' fields and their values
  #   nData - numpy arrays of sampled data - 'Mean' 1 (col), 'Std' 1 (col), 'raw'
  #   enaAttr - Dict vna machine setup attribures, 'ff'
  # global session
  #
  # Writes to HDF5 Tables all of the experiment fields
  #############################################################
    def writeSamples(self, grp, setUp, grpData, nData, enaAttr):

        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp + "/exprTable")  # '/lab0')
        item = tbl.row

        #tbl.append(np.fromiter((setUp), dtype=tbl.dtype ))
        # now = int(time.time())
        #now = int(time.time())
        #now = datetime.datetime.fromtimestamp(time.time())
        now = setUp['unix_timestamp']
        # 
        # Copy SetUp fields to table items
        # 
        for k in setUp.keys():
          if k[0] != '_':  # Filter out non setup fields TODO
            item[k] = setUp[k]

        print(item)
        print(setUp)

        item['unix_timestamp'] = now
        print(item)
        newArrName = "s" + str(item['session']) + "_" + str(now)
        item['dataArrRef'] = grpData + "/" + newArrName

        print ("=^^^^^^^^^==")
        print ("Create Data Group:" + grpData)
        if "/" + grpData not in f:
            fdata = f.create_group(f.root, grpData)
        else:
            fdata = f.get_node('/' + grpData)
        atom = tables.Atom.from_dtype(np.dtype(np.complex128))
        # TODO add attributes for the S11/S21/ parameters

        table_arr = f.create_earray(fdata, newArrName, atom, (0,) + nData.shape, "S1", self.Filters)
        print ("Create data earray at:" + str(item['dataArrRef']))
        nDataE = nData[None, :]
        table_arr.append(nDataE)
 
        # 
        # Set ENA Paramers as attribute fields
        # 
        if 'ENADataMode' in enaAttr.keys():
          table_arr.attrs.enaDataMode = enaAttr['ENADataMode']
        if 'NumberOfPoints' in enaAttr.keys():
          table_arr.attrs.numberOfPoints = enaAttr['NumberOfPoints']
        if 'STAR' in enaAttr.keys():
          table_arr.attrs.startFreq =  enaAttr['STAR']
        if 'STOP' in enaAttr.keys():
          table_arr.attrs.endFreq = enaAttr['STOP']
        if 'CENT' in enaAttr.keys():
          table_arr.attrs.centerFreq = enaAttr['CENT']
        if 'SPAN' in enaAttr.keys():
          table_arr.attrs.spanFreq = enaAttr['SPAN']
        if 'ff' in enaAttr.keys():
          table_arr.attrs.ff = enaAttr['ff']
          print ("Write Attribus ff: {}-{}".format(enaAttr['ff'][0], enaAttr['ff'][-1]))
        if 'offset' in enaAttr.keys():
          table_arr.attrs.sparamOffset = enaAttr['offset']
          print ("Write Attribus sparamOffsets: {}".format(enaAttr['offset']))


#        if 'S11' in enaAttr.keys():
#          table_arr.attrs.sparam1 += enaAttr['S11']
#        if 'S21' in enaAttr.keys():
#          table_arr.attrs.sparam1 += enaAttr['S21']*2
#        if 'S12' in enaAttr.keys():
#          table_arr.attrs.sparam1 += enaAttr['S12']*4
#        if 'S22' in enaAttr.keys():
#          table_arr.attrs.sparam1 += enaAttr['S22']*8


        print("Wrote sample to table:{}, type:{}".format(nData.shape, type(nData)))
        print ("wrote to index table:" + grp)
        item.append()
        print (tbl.dtype)
        tbl.flush()
        table_arr.flush()
        f.close()
        return

    def removeSamples(self, grp, qStr=''):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp)  # '/lab0')
        if qStr == '':
            tbl.remove_rows(len(tbl) - 1, len(tbl))
        else:
            print ("Query String: " + qstr)
            rows = tbl.where(qstr)
            for it in rows:
                print("Removing Row: %s" % (it))
                tbl.remove_rows(it)

        tbl.flush()
        f.close()
        return
  #---------------------------------------------------------
  # queryDataTimeCond:
  # Input:
  #     qList - list of query strings
  #     pStart, pEnd : datetime format
  # Output:
  #    rows in pandas dataframe format.
    def queryDataTimeCond(self, qList, pStart = None, pEnd = None):

     qFinal = ""
     for i, qstr in enumerate(qList):
        if qstr[0] =='@':
          params = [0,0]
          if pStart == None:
            pStart = datetime.datetime.now()
          params[0] =int(time.mktime(pStart.timetuple()))
          if pEnd == None: 
             pEnd = pStart  ##TODO - check that only day is used (not hours)
          params[1] = int(time.mktime(pEnd.timetuple()))
          print (params)
          tsl = self.parseTimeStamp(qstr[1:], params)
          if len(tsl) == 2:
             qres = "( {} ) & ( {} ) ".format(tsl[0],tsl[1])
          elif len(tsl) == 1:
             qres = "( {} ) ".format(tsl[0])
        else:
          qres = qstr
        if (i==0): 
           qFinal = qres
        else:
           qFinal = "( {} ) & {} ".format(qFinal, qres)
     print (qFinal)
     rows = self.query('/lab0/exprTable',qFinal)
     return rows

    def query(self, grp, qStr=''):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp)  # '/lab0')
        if qStr == '':
            return
        print ("Query String: " + qStr)
        rows = tbl.where(qStr)
        #self.printDat_It(iter(rows))
#        x =  next(iter(rows))
        #print (tables.description.dtype_from_descr(ExperimentTable))
        t = tables.description.dtype_from_descr(ExperimentTable)
        npt =  np.empty((0,24), t )
        res = pd.DataFrame.from_records(npt[:])
        #print ("========")
        #res.set_index("unix_timestamp")
        #print (res)
        #print ("========")
        dataRes = []
        for i,x in enumerate(iter(rows)): #it:  # tbl.iterrows():
                #      print(x[tbl[:])
          res.loc[i] = list(x[:])
        #print (res)
        print ("Number of results: {}".format( len(res)))
       #res.append(x['session'], x['material'], x['rho'], x['sData']))
       #res.append( {'session': x['session'], 'material':x['material1'], 'concentrate':x['rho'], 'sData':x['sData']})
        
        f.close()
         
        return res

#####################################################
# getRowsFreqData : Get Data referenced by the table entries  
# Input : 
#     hdStore - h5 database instance
#     rows - pd data frame with experiment table entries (as rows)
#     rangeList - index of entries to retreive data from.
#     sparam - Type of data to retrieve (e.g "S11" or "S21" or "S21Mean"
#
# Output: (freqL, clist)
#     freqL - list of the ENA sample frequencies. (only last data array used)
#     clist - list of numpy array's with data. 
#
#####################################################

    def getRowsFreqData( self, rows, rangeList, sparam):
      dL = []
      clist = []
      for i in rangeList:
        datapath = rows.loc[i]['dataArrRef'].decode()
        print (datapath)
        darray = self.getDataByRef(datapath)
        #print (darray.shape, darray.dtype)
        #print (darray.dtype)
        #print (darray.attrs.sparamOffset)
        if sparam in  darray.attrs.sparamOffset.keys():
          off = darray.attrs.sparamOffset[sparam]
        else: 
          print("Debug, dbHdf5: Sparam not found, " + str(sparam))
          off = 0
        freqL = darray.attrs.ff
        dL.append(darray)
      for data in dL:
        complex_sample = np.squeeze(data[0, :, off]) #'sData'] #TODO fix offset
        #print("Data type on query:", values.dtype) 
        #complex_sample[:] = values[sp,:] + 1j*values[sp+1,:]
        #print(complex_sample.shape) 
        #print(type(complex_sample[0]))
        clist.append(complex_sample)
      if self.f != None:
            self.f.close()
      return ( freqL, clist)


    def getDataByRef(self, datapath):
        self.f = tables.open_file(self.filename, "a", filters=self.Filters)
        darray = self.f.get_node('/' + datapath)
#        dataRes.append(darray)
#        f.close()
        return darray


    def parseTimeStamp0(self, cmd):

#        prefix = "unix_timestamp >= "
#        if cmd in "Before":
#          prefix = "unix_timestamp < "
        

        if cmd in "All":
            startoftime = datetime.date.today() - datetime.timedelta(days=10000)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(startoftime, t)
        elif cmd in "Today":
            today = datetime.date.today()
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(today, t)
        elif cmd in "LastHour" or cmd in "LastMinutes" or cmd in "Before":
            try:
              param = int(str.split(cmd)[1])
            except:
              print ("Error parse time stamp")
            finally:
              if cmd in "LastHour":
                 res = datetime.datetime.now() - datetime.timedelta(hours=param)
              elif cmd in "LastMinutes":
                 res = datetime.datetime.now() - datetime.timedelta(minutes=param)
        elif cmd == "Yesterday":
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(yesterday, t)
        return int(res.strftime("%s"))

 
    #def getTimeStamp2(self, cmd, params=[1,0]):
###########################################################
# parseTimeStamp
# Input:
#      cmd : Time command one of All, Today, LastHour, 
#            LastMinutes, Yesterday, Range
#      params: In case of :
#           LastHour, LastMinutes - params[0] is used for number
#           Range: params[0], params[1] - unix timestamp for start and end times
#
# Ouput: Array of query strings for time 
#
    def parseTimeStamp(self, cmd,params=[1,0]):

        if cmd == "Range":
             qstr1 = "unix_timestamp >= {}".format(params[0])
             qstr2 = "unix_timestamp <= {}".format(params[1])
             return [qstr1, qstr2] 
        if cmd == "All":
            startoftime = datetime.date.today() - datetime.timedelta(days=10000)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(startoftime, t)
        if cmd == "Today":
            today = datetime.date.today()
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(today, t)
        elif cmd == "LastHour":
            res = datetime.datetime.now() - datetime.timedelta(hours=param[0])
        elif cmd == "LastMinutes":
            res = datetime.datetime.now() - datetime.timedelta(minutes=param[0])
        elif cmd == "Yesterday":
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(yesterday, t)
            
#        return int(res.strftime("%s"))
        return ["unix_timestamp >= {}".format(int(res.strftime("%s")))]




    def getTimeStamp(self, cmd, param=1):
        if cmd == "All":
            startoftime = datetime.date.today() - datetime.timedelta(days=10000)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(startoftime, t)
        if cmd == "Today":
            today = datetime.date.today()
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(today, t)
        elif cmd == "LastHour":
            res = datetime.datetime.now() - datetime.timedelta(hours=param)
        elif cmd == "LastMinutes":
            res = datetime.datetime.now() - datetime.timedelta(minutes=param)
        elif cmd == "Yesterday":
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            t = datetime.time(hour=6, minute=00)
            res = datetime.datetime.combine(yesterday, t)
        return int(res.strftime("%s"))


################################ End of Class #########################################

'''
def testQuery(filename, grp):
    global Filters
    print ("print table:%s" % (filename))
    f = tables.open_file(filename, "r", filters=Filters)
    print(list(f))
    tbl = f.get_node(grp)  # ('/lab0')

    # ts = getTimeStamp("Today")
    ts = getTimeStamp("LastMinutes", 1)
    # ts = getTimeStamp("Yesterday")
    now = time.time()
    qstr = "unix_timestamp >= %d" % (ts)
    print ("Query String: " + qstr)
    rows = tbl.where(qstr)
    print(sum(1 for it in rows))


if __name__ == '__main__':  # You should keep this line for our auto-grading code.
    filters1 = tables.Filters(complevel=0)
    #  filters2 = tables.Filters(complevel=8, complib='bzip2', shuffle=False)
    filters2 = tables.Filters(complevel=8, complib='blosc:lz4', shuffle=True)
    # filters = tables.Filters(complevel=0)

    print ('Number of arguments:', len(sys.argv), 'arguments.')
    print ('Argument List:', str(sys.argv))

    if len(sys.argv) > 1:
        dbName = sys.argv[1]  # Use existing Db
        test_db(filters1, 1000, dbName)
    else:
        dbName = test_db(filters1, 1000)
    testQuery(dbName, "/exprTable")  # '/lab0')
'''
#  hdfstore.put('my_table', df[:5], format='table')
#  for loc in locations:
#    grp = f.create_group(loc)

# complib, codec = 'blosc', 'zstd'
# complevel = 6
# filename = "%s/pokemons-%s-%s-%d.h5" % (data_dir, complib, codec, complevel)
# with pd.HDFStore(filename, mode='w') as hdf:
# We only index the columns needed
#    hdf.put(key='pokemons', value=df, data_columns=['target', 'latitude', 'longitude'],
#            format='table', complevel=complevel, complib="%s:%s" % (complib, codec))
