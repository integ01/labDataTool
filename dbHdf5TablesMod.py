#http://mtweb.cs.ucl.ac.uk/mus/martha/PythonPackages/tables-3.0.0rc2/doc/html/usersguide/tutorials.html	
#https://www.pytables.org/usersguide/tutorials.html
# 19-Aug-2019 : TODO add test where file is remained open for the duration of the test
import h5py
import numpy as np
import tables
#import PyTables

import time
import datetime

import sys
import os
import shutil

SAMPLE_SHAPE = (4,201)
MAX_SESS_SAMPLES = 100
dataBaseName = "dataFile0"
Filters = None

setUpP = {
  'time' : None,
  'freqSt': '2GHZ',
  'freqEn': '3GHZ',
  'material' : 'water',
#  'concentrate' : 0.8
}



def unixTimePostfix(time):
  now = datetime.datetime.fromtimestamp(time)
  postfix = now.strftime("%Y/%m/%d_%H:%M:%S")
  return postfix


class sampleTable(tables.IsDescription):
   unix_timestamp = tables.Int64Col(pos=0)
   session = tables.Int32Col(pos=0)
#   unix_timestamp = tables.Time64Col(pos=0)
   material1 = tables.StringCol(20, pos=1)
   material2 = tables.StringCol(20, pos=1)
   rho = tables.Float32Col(pos=2)
   notes = tables.StringCol(50, pos=3)
   sData = tables.Float64Col(shape=(SAMPLE_SHAPE), dflt=0.0)
   #at =  tables.ComplexAtom(itemsize=8) 
   #sData = tables.AtomCol( at, shape=(SAMPLE_SHAPE), dflt=0.0)
   #class arrs(tables.IsDescription):
    
   #dtypeData = tables.Atom.from_dtype(np.dtype((np.float64, SAMPLE_SHAPE)))
   #atom = tables.Atom.from_dtype(np.array(SAMPLE_SHAPE).dtype)
#Atom.from_dtype(numpy.dtype('float64'))
#   class numpyData(tables.IsDescription):
#    data = np.dtype(np.array([SAMPLE_SHAPE[0], SAMPLE_SHAPE[1]]))



class hdf5DataTable:

  def __init__(self, dataBase_= dataBaseName, filters=tables.Filters(complevel=0), restore=False):
    self.data_dir = "dataDir"
    self.Filters = filters
    if os.path.exists(self.data_dir):
      pass#shutil.rmtree(data_dir)
    else:
      os.mkdir(self.data_dir)
    filename = self.get_filename(dataBase_,filters)
    filename = os.path.join(self.data_dir, filename)
    self.filename = filename
    if restore:
      self.printData('/lab0',setUpP)
    else:
     if os.path.exists(filename):
       cmd = raw_input("File %s already exists, do you want to erase it and start new?"%(filename))
       if (cmd[0]=='y'):
           self.filename = self.createPandasH5Table(self.data_dir, filename, ['lab0'],filters)
#           self.filename = self.createPandasH5Table(self.data_dir, dataBaseName, ['lab0'],filters)
    return  


  def createPandasH5Table(self, data_dir, file_, locations,filters):
#    filename = self.get_filename(file_,filters)
#    filename = os.path.join(data_dir, filename)
#   hdstore = pd.HDFStore(FILENAME, "w")
    print("Creating file:", file_)
    loc = locations[0]
    print("H5 path :%s"%(loc))
    with tables.open_file(file_, "w", filters=filters) as f:
      table_lens = f.create_table(f.root, loc, sampleTable)#, maxshape=(10000,))
      print ('Created table:' )
      print ( loc)
    
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




  def printData(self, grp, setUp):
    print ("print table:%s"%(self.filename))
    f = tables.open_file(self.filename, "r", filters=self.Filters)
    print(list(f))
    tbl = f.get_node(grp) 
    print( "Table %s, len:%d"%(grp, len(tbl)))
#    print( tbl.dtype.nbytes)
    ndt = np.dtype(tbl.dtype)
    print(ndt.itemsize)
    i=0
    print( "unix_timestamp,    session       , Material , Rho , Notes, Data ")
    print( "=====================================================")
    for x in tbl.iterrows():
#    print(x[tbl[:])
       print( "%-16s, %d, %10s, %0.4f, %-10s, %f"%( unixTimePostfix(x['unix_timestamp']), x['session'], x['material1'], x['rho'], "notes...", x['sData'][0,0] ) )
       i +=1
       if i > 100: 
         break
    print( "Table %s, len:%d"%(grp, len(tbl)))
    f.close()

  def writeSamples(self, nData, grp, setUp):

    f = tables.open_file(self.filename, "a", filters=self.Filters)
    tbl = f.get_node(grp) #'/lab0')
    item = tbl.row
    #now = int(time.time())
    now = int(time.time())
 
    item['unix_timestamp']= now
    item['session'] =  setUp['session']
    item['material1']= setUp['material']
    item['material2']=''
    item['rho']= 0.0 #setUp['concentrate']
    item['notes']= "Notes-Nothing"
    item['sData']= nData
    print("Wrote sample to table:{}, type:{}".format( nData.shape, type(nData)))
    item.append()
    tbl.flush()
    f.close()
    return 

  def removeSamples(self, grp, qStr=''):
    f = tables.open_file(self.filename, "a", filters=self.Filters)
    tbl = f.get_node(grp) #'/lab0')
    if qStr == '':
      tbl.remove_rows(len(tbl)-1, len(tbl) )
    else:
      print ("Query String: " + qstr)
      rows = tbl.where(qstr) 
      for it in rows:
         print("Removing Row: %s"%(it))
         tbl.remove_rows(it)

    tbl.flush()
    f.close()
    return

  def query(self, grp, qStr=''):
    f = tables.open_file(self.filename, "a", filters=self.Filters)
    tbl = f.get_node(grp) #'/lab0')
    if qStr == '':
       return
    print ("Query String: " + qStr)
    #rows = tbl.where(qStr) 
    res = []
    print( "unix_timestamp                , Material , Rho , Notes, Data ")
    print( "=====================================================")
    for x in tbl.where(qStr): 
#    print(x[tbl[:])
       print( "%-16s, %d,  %10s, %0.4f, %-10s, %f"%( unixTimePostfix(x['unix_timestamp']), x['session'], x['material1'], x['rho'], "notes...", x['sData'][0,0] ) )
       #res.append(x['session'], x['material'], x['rho'], x['sData']))
       res.append( {'session': x['session'], 'material':x['material1'], 'concentrate':x['rho'], 'sData':x['sData']})
    f.close()
    return res

  def getTimeStamp(self, cmd, param=1):
    if cmd == "All":
      startoftime = datetime.date.today () - datetime.timedelta (days=1000)
      t = datetime.time(hour=6, minute=00)
      res = datetime.datetime.combine(startoftime, t)
    if cmd == "Today":
      today = datetime.date.today()
      t = datetime.time(hour=6, minute=00)
      res = datetime.datetime.combine(today, t)
    elif cmd == "LastHour":
      res = datetime.datetime.now() - datetime.timedelta (hours=param)
    elif cmd == "LastMinutes":
      res = datetime.datetime.now() - datetime.timedelta (minutes=param)
    elif cmd == "Yesterday":
      yesterday = datetime.date.today () - datetime.timedelta (days=1)
      t = datetime.time(hour=6, minute=00)
      res = datetime.datetime.combine(yesterday, t)
    return int(res.strftime("%s"))


def testQuery(filename, grp):
    global Filters
    print ("print table:%s"%(filename))
    f = tables.open_file(filename, "r", filters=Filters)
    print(list(f))
    tbl = f.get_node(grp) #('/lab0')
    
    #ts = getTimeStamp("Today")
    ts = getTimeStamp("LastMinutes", 1)
    #ts = getTimeStamp("Yesterday")
    now = time.time()
    qstr = "unix_timestamp >= %d"%(ts)
    print ("Query String: " + qstr)
    rows = tbl.where(qstr) 
    print(sum(1 for it in rows))
       



if __name__ == '__main__':  # You should keep this line for our auto-grading code.
  filters1 = tables.Filters(complevel=0)
#  filters2 = tables.Filters(complevel=8, complib='bzip2', shuffle=False)
  filters2 = tables.Filters(complevel=8, complib='blosc:lz4', shuffle=True)
#filters = tables.Filters(complevel=0)

  print ('Number of arguments:', len(sys.argv), 'arguments.')
  print ('Argument List:', str(sys.argv))

  if len(sys.argv) > 1:
      dbName = sys.argv[1]  #Use existing Db
      test_db(filters1,1000, dbName)
  else:  
     dbName = test_db(filters1,1000)  
  testQuery(dbName,'/lab0')


#  hdfstore.put('my_table', df[:5], format='table')
#  for loc in locations:
#    grp = f.create_group(loc)

#complib, codec = 'blosc', 'zstd'
#complevel = 6
#filename = "%s/pokemons-%s-%s-%d.h5" % (data_dir, complib, codec, complevel)
#with pd.HDFStore(filename, mode='w') as hdf:
# We only index the columns needed
#    hdf.put(key='pokemons', value=df, data_columns=['target', 'latitude', 'longitude'],
#            format='table', complevel=complevel, complib="%s:%s" % (complib, codec))
  
