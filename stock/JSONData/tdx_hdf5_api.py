# -*- encoding: utf-8 -*-
# !/usr/bin/python
# from __future__ import division

import os
import sys
import time
import pandas as pd
from pandas import HDFStore
sys.path.append("..")
from JohhnsonUtil import LoggerFactory
from JohhnsonUtil import commonTips as cct
from JohhnsonUtil import johnson_cons as ct
import random
import numpy as np
import subprocess
log = LoggerFactory.log
import gc
global RAMDISK_KEY, INIT_LOG_Error
RAMDISK_KEY = 0
INIT_LOG_Error = 0
BaseDir = cct.get_ramdisk_dir()


class SafeHDFStore(HDFStore):
    # def __init__(self, *args, **kwargs):

    def __init__(self, *args, **kwargs):
        self.probe_interval = kwargs.pop("probe_interval", 2)
        lock = cct.get_ramdisk_path(args[0], lock=True)
        baseDir = BaseDir
        self.fname = cct.get_ramdisk_path(args[0])
        self._lock = lock
        self.countlock = 0
        self.write_status = False
        self.complevel = 9
        self.complib = 'zlib'
        self.ptrepack_cmds = "ptrepack --chunkshape=auto --propindexes --complevel=9 --complib=blosc %s %s"
        self.big_H5_Size = ct.big_H5_Size
        global RAMDISK_KEY
        if not os.path.exists(baseDir):
            if RAMDISK_KEY < 1:
                log.error("NO RamDisk Root:%s" % (baseDir))
                RAMDISK_KEY += 1
        else:
            self.temp_file = self.fname + '_tmp'
            self.write_status = True
            self.run(self.fname)
        # ptrepack --chunkshape=auto --propindexes --complevel=9 --complib=blosc in.h5 out.h5
        # subprocess.call(["ptrepack", "-o", "--chunkshape=auto", "--propindexes", --complevel=9,", ",--complib=blosc,infilename, outfilename])
        # os.system()

    def run(self, fname, *args, **kwargs):
        while True:
            try:
                self._flock = os.open(
                    self._lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                log.info("SafeHDF:%s lock:%s" % (self._lock, self._flock))
                break
            # except FileExistsError:
#            except FileExistsError as e:
            # except (IOError, EOFError, Exception) as e:
            except (IOError, OSError) as e:
                # time.sleep(probe_interval)
                log.error("IOError Error:%s" % (e))
                if self.countlock <= 10:
                    time.sleep(random.randint(1, 3))
                    # time.sleep(random.randint(0,5))
                    self.countlock += 1
                else:
                    os.remove(self._lock)
                    # time.sleep(random.randint(15, 30))
                    log.error("count10 remove lock")
#            except (Exception) as e:
#                print ("Exception Error:%s"%(e))
#                log.info("safeHDF Except:%s"%(e))
#                time.sleep(probe_interval)
#                return None
        # HDFStore.__init__(self, fname, *args, **kwargs)
        HDFStore.__init__(self, fname, *args, **kwargs)
        
        # HDFStore.__init__(self,fname,complevel=self.complevel,complib=self.complib, **kwargs)
        # HDFStore.__init__(self,fname,format="table",complevel=self.complevel,complib=self.complib, **kwargs)
        # ptrepack --complib=zlib --complevel 9 --overwrite sina_data.h5 out.h5

    def __enter__(self):
        if self.write_status:
            return self

    def __exit__(self, *args, **kwargs):
        if self.write_status:
            HDFStore.__exit__(self, *args, **kwargs)
            os.close(self._flock)
            h5_size = os.path.getsize(self.fname) / 1000 / 1000
            if h5_size > self.big_H5_Size:
                log.info("h5_size:%sM" % (h5_size))
                os.rename(self.fname, self.temp_file)
                p = subprocess.Popen(self.ptrepack_cmds % (
                    self.temp_file, self.fname), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
                if p.returncode != 0:
                    log.error("ptrepack hdf Error.:%s" % (self.fname))
                    # return -1
                else:
                    os.remove(self.temp_file)
            os.remove(self._lock)
            gc.collect()

def clean_cols_for_hdf(data):
    types = data.apply(lambda x: pd.lib.infer_dtype(x.values))
    for col in types[types=='mixed'].index:
        data[col] = data[col].astype(str)
    # data[<your appropriate columns here>].fillna(0,inplace=True)
    return data

def write_hdf(f, key, df, complib):
    """Append pandas dataframe to hdf5.

    Args:
    f       -- File path
    key     -- Store key
    df      -- Pandas dataframe
    complib -- Compress lib 

    NOTE: We use maximum compression w/ zlib.
    """

    with SafeHDF5Store(f, complevel=9, complib=complib) as store:
        df.to_hdf(store, key, format='table', append=True)
# with SafeHDFStore('example.hdf') as store:
#     # Only put inside this block the code which operates on the store
#     store['result'] = result

# def write_lock(fname):
#     fpath = cct.get_ramdisk_path(fname,lock=True)


def get_hdf5_file(fpath, wr_mode='r', complevel=9, complib='zlib', mutiindx=False):
    '''old outdata'''
    # store=pd.HDFStore(fpath,wr_mode, complevel=complevel, complib=complib)
    fpath = cct.get_ramdisk_path(fpath)
    if fpath is None:
        log.info("don't exists %s" % (fpath))
        return None

    if os.path.exists(fpath):
        if wr_mode == 'w':
            # store=pd.HDFStore(fpath,complevel=None, complib=None, fletcher32=False)
            store = pd.HDFStore(fpath)
        else:
            lock = cct.get_ramdisk_path(fpath, lock=True)
            while True:
                try:
                    #                    lock_s = os.open(lock, os.O_CREAT |os.O_EXCL |os.O_WRONLY)
                    lock_s = os.open(lock, os.O_CREAT | os.O_EXCL)
                    log.info("SafeHDF:%s read lock:%s" % (lock_s, lock))
                    break
                # except FileExistsError:
    #            except FileExistsError as e:
                except (IOError, EOFError, Exception) as e:
                    # time.sleep(probe_interval)
                    log.error("IOError READ ERROR:%s" % (e))
                    time.sleep(random.random())

            store = pd.HDFStore(fpath, mode=wr_mode)
            # store=pd.HDFStore(fpath, mode=wr_mode, complevel=None, complib=None, fletcher32=False)
            os.remove(lock)
#            store = SafeHDFStore(fpath)
    else:
        if mutiindx:
            store = pd.HDFStore(fpath)
            # store = pd.HDFStore(fpath,complevel=9,complib='zlib')
        else:
            return None
        # store = pd.HDFStore(fpath, mode=wr_mode,complevel=9,complib='zlib')
    # store.put("Year2015", dfMinutes, format="table", append=True, data_columns=['dt','code'])
    return store
    # fp='/Volumes/RamDisk/top_now.h5'
    # get_hdf5_file(fp)
    # def hdf5_read_file(file):
    # store.select("Year2015", where=['dt<Timestamp("2015-01-07")','code=="000570"'])
    # return store


def write_hdf_db(fname, df, table='all', index=False, baseCount=500, append=True, MultiIndex=False):
    if 'code' in df.columns:
        df = df.set_index('code')
#    write_status = False
    time_t = time.time()
#    if not os.path.exists(cct.get_ramdisk_dir()):
#        log.info("NO RamDisk")
#        return False
    code_subdf = df.index.tolist()
    global RAMDISK_KEY
    if not RAMDISK_KEY < 1:
        return df
#    if df is not None and not df.empty and len(df) > 0:
#        dd = df.dtypes.to_frame()
#        if 'object' in dd.values:
#            dd = dd[dd == 'object'].dropna()
#            col = dd.index.tolist()
#            log.info("col:%s"%(col))
#            df[col] = df[col].astype(str)
#        df.index = df.index.astype(str)
    df['timel'] = time.time()
    if df is not None and not df.empty and table is not None:
        # h5 = get_hdf5_file(fname,wr_mode='r')
        tmpdf = []
        with SafeHDFStore(fname) as store:
            if store is not None:
                if '/' + table in store.keys():
                    tmpdf = store[table]
        if not MultiIndex:
            if index:
                # log.error("debug index:%s %s %s"%(df,index,len(df)))
                df.index = map((lambda x: str(1000000 - int(x))
                                if x.startswith('0') else x), df.index)
            if tmpdf is not None and len(tmpdf) > 0:
                if 'code' in tmpdf.columns:
                    tmpdf = tmpdf.set_index('code')
                if 'code' in df.columns:
                    df = df.set_index('code')
                diff_columns = set(df.columns) - set(tmpdf.columns)
                if len(diff_columns) <> 0:
                    log.error("columns diff:%s" % (diff_columns))

                limit_t = time.time()
                df['timel'] = limit_t
                # df_code = df.index.tolist()

                df = cct.combine_dataFrame(tmpdf, df, col=None, append=append)


                if not append:
                    df['timel'] = time.time()
                elif fname == 'powerCompute':
                    o_time = df[df.timel < limit_t].timel.tolist()
                    o_time = sorted(set(o_time), reverse=False)
                    if len(o_time) > ct.h5_time_l_count:
                        o_time = [time.time() - t_x for t_x in o_time]
                        o_timel = len(o_time)
                        o_time = np.mean(o_time)
                        if o_time > ct.h5_power_limit_time * 1.5:
                            df['timel'] = time.time()
                            log.error("%s %s o_time:%.1f timel:%s" % (fname, table, o_time,o_timel))

    #            df=cct.combine_dataFrame(tmpdf, df, col=None,append=False)
                log.info("read hdf time:%0.2f" % (time.time() - time_t))
            else:
                # if index:
                    # df.index = map((lambda x:str(1000000-int(x)) if x.startswith('0') else x),df.index)
                log.info("h5 None hdf reindex time:%0.2f" %
                         (time.time() - time_t))
        else:
            # df.loc[(df.index.get_level_values('code')== 600004)]
            # df.loc[(600004,20170414),:]
            # df.xs(20170425,level='date')
            # df.index.get_level_values('code').unique()
            # df.index.get_loc(600006)
            # slice(58, 87, None)
            # df.index.get_loc_level(600006)
            # da.swaplevel(0, 1, axis=0).loc['2017-05-25']
            # da.reorder_levels([1,0], axis=0)
            # da.sort_index(level=0, axis=0,ascending=False
            # setting: dfm.index.is_lexsorted() dfm = dfm.sort_index()  da.loc[('000001','2017-05-12'):('000005','2017-05-25')]
            # da.groupby(level=1).mean()
            # da.index.get_loc('000005')     da.iloc[slice(22,33,None)]
            # mask = totals['dirty']+totals['swap'] > 1e7     result =
            # mask.loc[mask]
            # store.remove('key_name', where='<where clause>')
            multi_code = tmpdf.index.get_level_values('code').unique().tolist()
            df_code = df.index.tolist()
            diff_code = set(df_code) - set(multi_code)
            # da.drop(('000001','2017-05-11'))
            pass

    time_t = time.time()
    if df is not None and not df.empty and table is not None:
        #        df['timel'] =  time.time()
        if df is not None and not df.empty and len(df) > 0:
            dd = df.dtypes.to_frame()

        if not MultiIndex:
            if 'object' in dd.values:
                dd = dd[dd == 'object'].dropna()
                col = dd.index.tolist()
                log.info("col:%s" % (col))
                df[col] = df[col].astype(str)
            df.index = df.index.astype(str)
            df = df.fillna(0)
        with SafeHDFStore(fname) as h5:
            df = df.fillna(0)
            if h5 is not None:
                if '/' + table in h5.keys():
                    h5.remove(table)
                    h5.put(table, df, format='table',data_columns=True,append=False)
                else:
                    h5.put(table, df, format='table',data_columns=True, append=False)
                h5.flush()
                    # h5[table] = df
            else:
                log.error("HDFile is None,Pls check:%s" % (fname))
    log.info("write hdf time:%0.2f" % (time.time() - time_t))

    return True

# def lo_hdf_db_old(fname,table='all',code_l=None,timelimit=True,index=False):
#    h_t = time.time()
#    h5=top_hdf_api(fname=fname, table=table, df=None,index=index)
#    if h5 is not None and code_l is not None:
#        if len(code_l) == 0:
#            return None
#        if h5 is not None:
#            diffcode = set(code_l) - set(h5.index)
#            if len(diffcode) > 10 and len(h5) <> 0 and float(len(diffcode))/float(len(code_l)) > ct.diffcode:
#                log.error("f:%s t:%s dfc:%s %s co:%s h5:%s"%(fname,table,len(diffcode),h5.index.values[0],code_l[:2],h5.index.values[:2]))
#                return None
#
#    if h5 is not None and not h5.empty and 'timel' in h5.columns:
#            o_time = h5[h5.timel <> 0].timel
#            if len(o_time) > 0:
#                o_time = o_time[0]
#    #            print time.time() - o_time
#                # if cct.get_work_hdf_status() and (not (915 < cct.get_now_time_int() < 930) and time.time() - o_time < ct.h5_limit_time):
#                if not cct.get_work_time() or (not timelimit or time.time() - o_time < ct.h5_limit_time):
#                    log.info("time hdf:%s %s"%(fname,len(h5))),
# if 'timel' in h5.columns:
# h5=h5.drop(['timel'],axis=1)
#                    if code_l is not None:
#                        if 'code' in h5.columns:
#                            h5 = h5.set_index('code')
#                        h5.drop([inx for inx in h5.index  if inx not in code_l], axis=0, inplace=True)
#                            # log.info("time in idx hdf:%s %s"%(fname,len(h5))),
#                    # if index == 'int' and 'code' not in h5.columns:
#                    #     h5=h5.reset_index()
#                    log.info("load hdf time:%0.2f"%(time.time()-h_t))
#                    return h5
#    else:
#        if h5 is not None:
#            return h5
#    return None


def load_hdf_db(fname, table='all', code_l=None, timelimit=True, index=False, limit_time=ct.h5_limit_time, dratio_limit=0.12):
    time_t = time.time()
    global RAMDISK_KEY, INIT_LOG_Error
    if not RAMDISK_KEY < 1:
        return None
    df = None
    dd = None
    if code_l is not None:
        if table is not None:
            with SafeHDFStore(fname) as store:
                if store is not None:
                    if '/' + table in store.keys():
                        dd = store[table]
            if dd is not None and len(dd) > 0:
                if index:
                    code_l = map((lambda x: str(1000000 - int(x))
                                  if x.startswith('0') else x), code_l)
                dif_co = list(set(dd.index) & set(code_l))
                dratio = (float(len(code_l)) - float(len(dif_co))) / \
                    float(len(code_l))
                # if dratio < 0.1 or len(dd) > 3100:
                if dratio < dratio_limit:
                    log.info("find all:%s :%s %0.2f" %
                             (len(code_l), len(code_l) - len(dif_co), dratio))
                    if timelimit and len(dd) > 0:
                        dd = dd.loc[dif_co]
                        o_time = dd[dd.timel <> 0].timel.tolist()
#                        if fname == 'powerCompute':
#                            o_time = sorted(set(o_time),reverse=True)
                        o_time = sorted(set(o_time), reverse=False)
                        o_time = [time.time() - t_x for t_x in o_time]

                        if len(dd) > 0 :
                        # if len(dd) > 0 and (not cct.get_work_time() or len(o_time) <= ct.h5_time_l_count):
                            l_time = np.mean(o_time)
                            return_hdf_status = (not cct.get_work_time()) or (
                                cct.get_work_time() and l_time < limit_time)
                            # return_hdf_status = l_time < limit_time
                            # print return_hdf_status,l_time,limit_time
                            if return_hdf_status:
                                df = dd
                                log.info("return hdf: %s timel:%s l_t:%s hdf ok:%s" % (
                                    fname, len(o_time), l_time, len(df)))
                        else:
                            log.error("%s %s o_time:%s %s" % (fname, table, len(
                                o_time), [time.time() - t_x for t_x in o_time[:3]]))
                        log.info('fname:%s l_time:%s' %
                                 (fname, [time.time() - t_x for t_x in o_time]))

                    else:
                        df = dd.loc[dif_co]
                else:
                    if len(code_l) > ct.h5_time_l_count * 10 and INIT_LOG_Error < 5:
                        # INIT_LOG_Error += 1
                        log.error("fn:%s cl:%s h5:%s don't find:%s dra:%0.2f log_err:%s" % (
                            fname, len(code_l), len(dd), len(code_l) - len(dif_co), dratio, INIT_LOG_Error))
        else:
            log.error("%s is not find %s" % (fname, table))
    else:
        # h5 = get_hdf5_file(fname,wr_mode='r')
        if table is not None:
            with SafeHDFStore(fname) as store:
                if store is not None:
                    if '/' + table in store.keys():
                        dd = store[table]
            if dd is not None and len(dd) > 0:
                if timelimit:
                    if dd is not None and len(dd) > 0:
                        o_time = dd[dd.timel <> 0].timel.tolist()
                        o_time = sorted(set(o_time))
                        o_time = [time.time() - t_x for t_x in o_time]
                        if len(o_time) > 0:
                            l_time = np.mean(o_time)
                            # l_time = time.time() - l_time
#                                    return_hdf_status = not cct.get_work_day_status()  or not cct.get_work_time() or (cct.get_work_day_status() and (cct.get_work_time() and l_time < limit_time))
                            return_hdf_status = not cct.get_work_time() or (
                                cct.get_work_time() and l_time < limit_time)
                            log.info("return_hdf_status:%s time:%0.2f" %
                                     (return_hdf_status, l_time))
                            if return_hdf_status:
                                log.info("return hdf5 data:%s o_time:%s" %
                                         (len(dd), len(o_time)))
                                df = dd
                            else:
                                log.info("no return time hdf5:%s" % (len(dd)))
                        log.info('fname:%s l_time:%s' %
                                 (fname, [time.time() - t_x for t_x in o_time]))
                else:
                    df = dd
            else:
                log.error("%s is not find %s" % (fname, table))
        else:
            log.error("% / table is Init None:%s"(fname, table))

    if df is not None and len(df) > 0:
        df = df.fillna(0)
        if 'timel' in df.columns:
            time_list = df.timel.tolist()
            # time_list = sorted(set(time_list),key = time_list.index)
            time_list = sorted(set(time_list))
            # log.info("test:%s"%(sorted(set(time_list),key = time_list.index)))
            if time_list is not None and len(time_list) > 0:
                df['timel'] = time_list[0]
                log.info("load hdf times:%s" %
                         ([time.time() - t_x for t_x in time_list]))

    log.info("load_hdf_time:%0.2f" % (time.time() - time_t))
    # if df is not None and len(df) > 1:
    # df = df.drop_duplicates()
    return df

# def load_hdf_db_old_outdate(fname,table='all',code_l=None,timelimit=True,index=False,limit_time=ct.h5_limit_time):
#     time_t = time.time()
#     df = None
#     global RAMDISK_KEY
#     # print RAMDISK_KEY
#     if not RAMDISK_KEY < 1:
#         return df
#     if code_l is not None:
#         h5 = get_hdf5_file(fname,wr_mode='r')
#         if h5 is not None:
#             if table is not None:
#                 if '/'+table in h5.keys():
#                     if index:
#                         code_l = map((lambda x:str(1000000-int(x)) if x.startswith('0') else x),code_l)
#                     dd = h5[table]
#                     dif_co = list(set(dd.index) & set(code_l))
#                     dratio = (float(len(code_l)) - float(len(dif_co)))/float(len(code_l))
#                     if dratio < 0.1 and len(dd) > 0:
#                         log.info("find all:%s :%s %0.2f"%(len(code_l),len(code_l)-len(dif_co),dratio))
#                         if timelimit and len(dd) > 0:
#                             dd = dd.loc[dif_co]
#                             o_time = dd[dd.timel <> 0].timel
#                             if len(o_time) > 0:
#                                 o_time = o_time[0]
#                                 l_time = time.time() - o_time
#                                 return_hdf_status = not cct.get_work_day_status()  or not cct.get_work_time() or (cct.get_work_day_status() and cct.get_work_time() and l_time < ct.limit_time)
#                                 if return_hdf_status:
#                                     df = dd
#                                     log.info("load %s time hdf ok:%s"%(fname,len(df)))

#                             log.info('fname:%s l_time:None'%(fname))
#                         else:
#                              df = dd.loc[dif_co]
#                     else:
#                         log.info("don't find :%s"%(len(code_l)-len(dif_co)))
#             else:
#                 log.error("%s is not find %s"%(fname,table))
#     else:
#         h5 = get_hdf5_file(fname,wr_mode='r')
#         dd=None
#         if h5 is not None:
#             if table is None:
#                 dd = h5
#             else:
#                 if table is not None:
#                     if '/'+table in h5.keys():
#                         dd = h5[table]
#                         if timelimit and len(dd) > 0:
#                             if dd is not None and len(dd)>0:
#                                 o_time = dd[dd.timel <> 0].timel
#                                 if len(o_time) > 0:
#                                     o_time = o_time[0]
#                                     l_time = time.time() - o_time
#                                     return_hdf_status = not cct.get_work_day_status()  or not cct.get_work_time() or (cct.get_work_day_status() and cct.get_work_time() and l_time < ct.h5_limit_time)
#                                     log.info("return_hdf_status:%s time:%0.2f"%(return_hdf_status,l_time))
#                                     if  return_hdf_status:
#                                         log.info("return hdf5 data:%s"%(len(h5)))
#                                         df = dd
#                                     else:
#                                         log.info("no return time hdf5:%s"%(len(h5)))
#                                 log.info('fname:%s l_time:None'%(fname))
#                         else:
#                              df = dd
#                     else:
#                         log.error("%s is not find %s"%(fname,table))
#     if h5 is not None and h5.is_open:
#         h5.close()

#     if df is not None and len(df) > 0:
#         df = df.fillna(0)
#         if 'timel' in df.columns:
#             time_list = df.timel.tolist()
#             time_list = sorted(set(time_list),key = time_list.index)
#             if time_list is not None and len(time_list) > 0:
#                 df['timel'] = time_list[0]
#                 log.info("load hdf times:%s"%(time_list))

#     log.info("load_hdf_time:%0.2f"%(time.time()-time_t))
#     return df


if __name__ == "__main__":

#    import tushare as ts
#    df = ts.get_k_data('300334', start='2017-04-01')
    fname = ['sina_data.h5','tdx_last_df','powerCompute.h5','get_sina_all_ratio']
    # fname = 'powerCompute.h5'
    for na in fname:
        with SafeHDFStore(na) as h5:
            print h5
        # print h5['d_21_y_all'].loc['300666']
        # h5.remove('high_10_y_20170620_all_15')
        # print h5
        # dd = h5['d_21_y_all']
        # print len(set(dd.timel))
        # print time.time()- np.mean(list(set(dd.timel)))

    # Only put inside this block the code which operates on the store
    # store['result'] = df
