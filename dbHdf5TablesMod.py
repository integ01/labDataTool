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
from typing import Any, Union
import pandas as pd
#SAMPLE_SHAPE = (2, 402)
MAX_SESS_SAMPLES = 100
dataBaseName = "dataFile0"
Filters = None

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
    P0_volume= tables.Float32Col(pos=18)
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

    def __init__(self, dataBase_=dataBaseName, filters=tables.Filters(complevel=0), restore=False):
        self.data_dir = "dataDir"
        self.Filters = filters
        if os.path.exists(self.data_dir):
            pass  # shutil.rmtree(data_dir)
        else:
            os.mkdir(self.data_dir)
        filename = self.get_filename(dataBase_, filters)
        filename = os.path.join(self.data_dir, filename)
        self.filename = filename
        if restore:
            self.printData('/lab0')
        else:
            print ("hdf5 init) Create data Base:" + filename)
            if os.path.exists(filename):
                #cmd = raw_input("File %s already exists, do you want to erase it and start new?" % (filename))
                cmd = input("File %s already exists, do you want to erase it and start new?" % (filename))
                if len(cmd)==0 or (len(cmd)> 0 and cmd[0] != 'y'):
                    #TODO - add exception here
                    return
            self.filename = self.createPandasH5Table(self.data_dir, filename, ['lab0'], filters)
        return

    def createPandasH5Table(self, data_dir, file_, locations, filters):
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
  #   ndarry - Dict with numpy arrays of sampled data - 'raw', 'ff'
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

      now = datetime.datetime.fromtimestamp(time.time())
      postfixDate = now.strftime("%Y%m%d")
      dataGrp = "data_" + postfixDate
      self.writeSamples('/lab0', setUp, dataGrp, nData, enaAttr)
      delta = 1



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
        now = int(time.time())
        
        # 
        # Copy SetUp fields to table items
        # 
        for k in setUp.keys():
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

        # Add attributes for the S11/S21/ parameters
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
        table_arr.attrs.sparam1 = 0
        if 'S11' in enaAttr.keys():
          table_arr.attrs.sparam1 += enaAttr['S11']
        if 'S21' in enaAttr.keys():
          table_arr.attrs.sparam1 += enaAttr['S21']*2
        if 'S12' in enaAttr.keys():
          table_arr.attrs.sparam1 += enaAttr['S12']*4
        if 'S22' in enaAttr.keys():
          table_arr.attrs.sparam1 += enaAttr['S22']*8


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

    def query(self, grp, qStr=''):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        tbl = f.get_node(grp)  # '/lab0')
        if qStr == '':
            return
        print ("Query String: " + qStr)
        rows = tbl.where(qStr)
        #self.printDat_It(iter(rows))
#        x =  next(iter(rows))
        print (tables.description.dtype_from_descr(ExperimentTable))
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
        print (res)
        print (len(res))
       #res.append(x['session'], x['material'], x['rho'], x['sData']))
       #res.append( {'session': x['session'], 'material':x['material1'], 'concentrate':x['rho'], 'sData':x['sData']})
        
        f.close()
         
        return res

    def getDataByRef(self, datapath):
        f = tables.open_file(self.filename, "a", filters=self.Filters)
        darray = f.get_node('/' + datapath)
#        dataRes.append(darray)
        return darray



    def getTimeStamp(self, cmd, param=1):
        if cmd == "All":
            startoftime = datetime.date.today() - datetime.timedelta(days=1000)
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
