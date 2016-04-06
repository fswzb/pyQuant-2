# -*- coding:utf-8 -*-
# !/usr/bin/env python

import gc
import re
import sys
import time
import traceback

import pandas as pd
# from bs4 import BeautifulSoup

import JohhnsonUtil.johnson_cons as ct
import singleAnalyseUtil as sl
from JSONData import realdatajson as rl
from JSONData import tdx_data_Day as tdd
from JSONData import powerCompute as pct
from JohhnsonUtil import LoggerFactory as LoggerFactory
from JohhnsonUtil import commonTips as cct


# from logbook import StderrHandler
# from logbook import Logger,StreamHandler,SyslogHandler


if __name__ == "__main__":
    # parsehtml(downloadpage(url_s))
    # StreamHandler(sys.stdout).push_application()
    log = LoggerFactory.getLogger('SinaMarketNew')
    # log.setLevel(LoggerFactory.DEBUG)

    # handler=StderrHandler(format_string='{record.channel}: {record.message) [{record.extra[cwd]}]')
    # log.level=log.debug
    # error_handler = SyslogHandler('Sina-M-Log', level='ERROR')

    if cct.isMac():
        cct.set_console(123, 16)
    else:
        cct.set_console(100, 15)
    status = False
    vol = '0'
    type = '2'
    # cut_num=10000
    success = 0
    top_all = pd.DataFrame()
    time_s = time.time()
    # delay_time = 3600
    delay_time = cct.get_delay_time()
    First = True
    # base_path = tdd.get_tdx_dir()
    # block_path = tdd.get_tdx_dir_blocknew() + '062.blk'
    blkname = '069.blk'
    block_path = tdd.get_tdx_dir_blocknew() + blkname
    status_change = False

    # all_diffpath = tdd.get_tdx_dir_blocknew() + '062.blk'
    while 1:
        try:
            # df = sina_data.Sina().all
            df = rl.get_sina_Market_json('all')
            top_now = rl.get_market_price_sina_dd_realTime(df, vol, type)
            # print top_now.loc['300208','name']
            # top_now.to_hdf("testhdf5", 'marketDD', format='table', complevel=9)
            df_count = len(df)
            now_count = len(top_now)
            del df
            gc.collect()
            radio_t = cct.get_work_time_ratio()
            time_Rt = time.time()
            # top_now = top_now[top_now.buy > 0]
            time_d = time.time()
            if time_d - time_s > delay_time:
                status_change = True
                time_s = time.time()
                top_all = pd.DataFrame()
            else:
                status_change = False
            # print ("Buy>0:%s" % len(top_now[top_now['buy'] > 0])),
            if len(top_now) > 10 or cct.get_work_time():
                # if len(top_now) > 10 and len(top_now[:20][top_now[:20]['buy'] > 0]) > 3:
                # if len(top_now) > 10 and not top_now[:1].buy.values == 0:
                #     top_now=top_now[top_now['percent']>=0]
                if 'trade' in top_now.columns:
                    top_now['buy'] = (
                        map(lambda x, y: y if int(x) == 0 else x, top_now['buy'].values, top_now['trade'].values))
                if len(top_all) == 0:
                    top_all = top_now
                    # top_all['llow'] = 0
                    # top_all['lastp'] = 0
                    # top_all = top_all[top_all.buy > 0]
                    codelist = top_all.index.tolist()
                    log.info('toTDXlist:%s' % len(codelist))
                    tdxdata = tdd.get_tdx_all_day_LastDF(codelist)
                    log.debug("TdxLastP: %s %s" % (len(tdxdata), tdxdata.columns.values))
                    tdxdata.rename(columns={'low': 'llow'}, inplace=True)
                    tdxdata.rename(columns={'high': 'lhigh'}, inplace=True)
                    tdxdata.rename(columns={'close': 'lastp'}, inplace=True)
                    tdxdata.rename(columns={'vol': 'lvol'}, inplace=True)
                    tdxdata = tdxdata.loc[:, ['llow', 'lhigh', 'lastp', 'lvol', 'date']]
                    # data.drop('amount',axis=0,inplace=True)
                    log.debug("TDX Col:%s" % tdxdata.columns.values)
                    # df_now=top_all.merge(data,on='code',how='left')
                    # df_now=pd.merge(top_all,data,left_index=True,right_index=True,how='left')
                    top_all = top_all.merge(tdxdata, left_index=True, right_index=True, how='left')
                    log.info('Top-merge_now:%s' % (top_all[:1]))
                    top_all = top_all[top_all['llow'] > 0]

                    # if len(top_all[:5][top_all[:5]['volume'] > 0]) > 3:
                    #     # top_all['volume'] = top_all['volume'].apply(lambda x: round(float(x) / radio_t, 1))
                    #     # C4 = np.asarray(map(lambda x,y: x**y, pdA.values, pdB.values))
                    #     # top_all['volume'] = round(
                    #     # top_now.loc[symbol, 'volume'] / top_all.loc[symbol, 'lvol'], 1)
                    #     top_all['volume'] = (
                    #         map(lambda x, y: round(x / y / radio_t, 1), top_all['volume'].values,
                    #             top_all['lvol'].values))
                    #     # top_all['volume']=np.asarray(map(lambda x,y: round(x/y,1), top_all['volume'].values, top_all['lvol'].values))
                    #     # print top_all[:1]
                    #     log.debug("First:vol/vol/:%s" % radio_t)

                    # import sys
                    # sys.exit(0)
                else:
                    if 'counts' in top_now.columns.values:
                        if not 'counts' in top_all.columns.values:
                            top_all['counts'] = 0
                            top_all['prev_p'] = 0
                    for symbol in top_now.index:
                        # code = rl._symbol_to_code(symbol)
                        if symbol in top_all.index and top_now.loc[symbol, 'buy'] <> 0:
                            # if top_all.loc[symbol,'diff'] == 0:
                            # print "code:",symbol
                            count_n = top_now.loc[symbol, 'buy']
                            count_a = top_all.loc[symbol, 'buy']
                            # print count_a,count_n
                            # print count_n,count_a
                            
                            if count_a == 0 and count_n == 0:
                                continue
                            elif count_a == 0 and count_n !=0:
                                top_all.loc[symbol, 'buy'] = top_now.loc[symbol, 'buy']
                                count_a = count_n
                            else:
                                pass
                            
                            
                            if cct.get_now_time_int() < 930 and count_a != count_n:
                                # if not count_n == count_a:
                                top_all.loc[symbol, 'buy'] = top_now.loc[symbol, 'buy']
                                
                            else:
                                if not count_n == count_a:
                                    # log.info("n_buy-a_buy:%s" % (count_n - count_a))
                                    top_now.loc[symbol, 'diff'] = round(
                                        ((float(count_n) - float(count_a)) / float(count_a) * 100), 1)
                                    if status_change and 'counts' in top_now.columns.values:
                                        print "change:", time.time() - time_s
                                        # top_now.loc[symbol,'lastp']=top_all.loc[symbol,'lastp']
                                        # top_all.loc[symbol, 'buy':'counts'] = top_now.loc[symbol, 'buy':'counts']
                                        top_all.loc[symbol, 'buy':'prev_p'] = top_now.loc[symbol, 'buy':'prev_p']
                                    else:
                                        # top_now.loc[symbol,'lastp']=top_all.loc[symbol,'lastp']
                                        top_all.loc[symbol, 'diff':'low'] = top_now.loc[symbol, 'diff':'low']
                                elif 'counts' in top_now.columns.values:
                                    # log.info("n_buy==a_buy:update Counts")
                                    top_all.loc[symbol, 'diff':'prev_p'] = top_now.loc[symbol, 'diff':'prev_p']
                                else:
                                    # log.info("n_buy==a_buy:no counts update low")
                                    top_now.loc[symbol, 'diff'] = round(
                                        ((float(top_now.loc[symbol, 'buy']) - float(top_all.loc[symbol, 'lastp'])) / float(top_all.loc[symbol, 'lastp']) * 100), 1)
                                    top_all.loc[symbol, 'diff':'low'] = top_now.loc[symbol, 'diff':'low']

                                    # top_all.loc[symbol]=top_now.loc[symbol]?
                                    # top_all.loc[symbol,'diff']=top_now.loc[symbol,'counts']-top_all.loc[symbol,'counts']

                                    # else:
                                    # value=top_all.loc[symbol,'diff']

                                    # else:
                                    #     if float(top_now.loc[symbol,'low'])>float(top_all.loc[symbol,'lastp']):
                                    #         # top_all.append(top_now.loc[symbol])
                                    #         print "not all ???"

                # top_all=top_all.sort_values(by=['diff','percent','counts'],ascending=[0,0,1])
                # top_all=top_all.sort_values(by=['diff','ratio','percent','counts'],ascending=[0,1,0,1])

                # top_all = top_all[top_all.open>=top_all.low*0.99]
                # top_all = top_all[top_all.buy >= top_all.open*0.99]
                # top_all = top_all[top_all.trade >= top_all.low*0.99]
                # top_all = top_all[top_all.trade >= top_all.high*0.99]
                # top_all = top_all[top_all.buy >= top_all.lastp]
                # top_all = top_all[top_all.percent >= 0]

                if cct.get_now_time_int() < 930:
                    top_all['diff'] = (
                        map(lambda x, y: round((x - y) / y * 100, 1), top_all['buy'].values, top_all['lastp'].values))

                top_dif = top_all
                log.info('dif1:%s' % len(top_dif))
                top_dif=top_dif[top_dif.lvol > ct.LvolumeSize]
                if cct.get_now_time_int() > 915:
                    top_dif = top_dif[top_dif.buy > top_dif.lastp]
                    top_dif = top_dif[top_dif.buy > top_dif.lhigh]
                log.debug('dif2:%s' % len(top_dif))
                # log.debug('dif2:%s' % top_dif[:1])
                # log

                # if top_dif[:1].llow.values <> 0:
                if len(top_dif[:5][top_dif[:5]['low'] > 0]) > 3:
                    log.debug('diff2-0-low>0')
                    top_dif = top_dif[top_dif.low >= top_dif.llow]
                    log.debug('diff2-1:%s' % len(top_dif))

                    top_dif = top_dif[top_dif.low >= top_dif.lastp]
                    log.debug('dif3 low<>0 :%s' % len(top_dif))

                    top_dif = top_dif[top_dif.open >= top_dif.lastp]

                    log.debug('dif4 open>lastp:%s' % len(top_dif))
                    log.debug('dif4-2:%s' % top_dif[:1])

                    top_dif = top_dif[top_dif.low >= top_dif.lhigh]

                    log.debug("dif5-0-low>lhigh>0:%s" % len(top_dif))

                    top_dif = top_dif[top_dif.percent >= 0]
                    log.debug("dif5-percent>0:%s" % len(top_dif))

                    # top_dif = top_dif[top_dif.percent >= 0]
                    # if len(top_dif[:5][top_dif[:5]['volume'] > 0]) > 3:
                    log.debug("Second:vol/vol/:%s" % radio_t)
                    # top_dif['volume'] = top_dif['volume'].apply(lambda x: round(x / radio_t, 1))
                    log.debug("top_diff:vol")
                    top_dif['volume'] = (
                        map(lambda x, y: round(x / y / radio_t, 1), top_dif['volume'].values, top_dif['lvol'].values))
                    # top_dif = top_dif[top_dif.volume > 1]
                if len(top_dif) == 0:
                    print "No G,DataFrame is Empty!!!!!!"
                    # top_dif = top_all

                log.debug('dif6 vol:%s' % (top_dif[:1].volume))

                log.debug('dif6 vol>lvol:%s' % len(top_dif))

                # top_dif = top_dif[top_dif.buy >= top_dif.open*0.99]
                # log.debug('dif5 buy>open:%s'%len(top_dif))
                # top_dif = top_dif[top_dif.trade >= top_dif.buy]

                # df['volume']= df['volume'].apply(lambda x:x/100)


                if 'counts' in top_dif.columns.values:
                    top_dif = top_dif.sort_values(by=['diff', 'volume', 'percent', 'counts', 'ratio'],
                                                  ascending=[0, 0, 0, 1, 1])
                else:
                    # print "Good Morning!!!"
                    top_dif = top_dif.sort_values(by=['diff', 'percent', 'ratio'], ascending=[0, 0, 1])
    
                # top_all=top_all.sort_values(by=['percent','diff','counts','ratio'],ascending=[0,0,1,1])
                # print rl.format_for_print(top_dif[:10])
                top_temp = top_dif[:50].copy()
                top_temp = pct.powerCompute_df(top_temp,dl='30')
                print ("A:%s N:%s K:%s %s G:%s" % (
                    df_count, now_count, len(top_all[top_all['buy'] > 0]),
                    len(top_now[top_now['volume'] <= 0]), len(top_dif))),
                # print "Rt:%0.3f" % (float(time.time() - time_Rt))
                print "Rt:%0.1f dT:%s" % (float(time.time() - time_Rt), cct.get_time_to_date(time_s))
                cct.set_console(
                    title=['dT:%s' % cct.get_time_to_date(time_s), 'G:%s' % len(top_dif), 'zxg: %s' % (blkname)])
               
                if 'op' in top_temp.columns:
                    top_temp = top_temp.sort_values(by=['op','ra','diff', 'percent', 'ratio'], ascending=[0,0,0, 0, 1])
                if cct.get_now_time_int() > 915 and cct.get_now_time_int() < 935:
                    top_temp = top_temp.loc[:,
                             ['name', 'buy', 'diff', 'op', 'ra','fib', 'percent','volume', 'ratio', 'counts',
                              'ldate', 'date']]
                else:
                    top_temp = top_temp.loc[:,
                             ['name', 'buy', 'diff', 'op', 'ra','fib', 'percent', 'volume', 'ratio', 'counts',
                              'ldate','date']]
                print rl.format_for_print(top_temp[:10])
                # print rl.format_for_print(top_dif[:10])
                # print top_all.loc['000025',:]
                # print "staus",status

                if status:
                    for code in top_dif[:10].index:
                        code = re.findall('(\d+)', code)
                        if len(code) > 0:
                            code = code[0]
                            kind = sl.get_multiday_ave_compare_silent(code)
                            # print top_all[top_all.low.values==0]

                            # else:
                            #     print "\t No RealTime Data"
            else:
                print "\tNo Data"
            int_time = cct.get_now_time_int()
            if cct.get_work_time():
                if int_time < 925:
                    cct.sleep(30)
                elif int_time < 930:
                    cct.sleep((930 - int_time) * 60)
                    top_all = pd.DataFrame()
                    time_s = time.time()
                else:
                    cct.sleep(60)
            elif cct.get_work_duration():
                while 1:
                    cct.sleep(60)
                    if cct.get_work_duration():
                        print ".",
                        cct.sleep(60)
                    else:
                        top_all = pd.DataFrame()
                        time_s = time.time()
                        print "."
                        break
            else:
                # break
                # cct.sleep(5)
                raise KeyboardInterrupt("StopTime")
        except (KeyboardInterrupt) as e:
            # print "key"
            print "KeyboardInterrupt:", e
            # cct.sleep(1)
            # if success > 3:
            #     raw_input("Except")
            #     sys.exit(0)
            st = raw_input("status:[go(g),clear(c),quit(q,e),W(w),Wa(a)]:")
            if len(st) == 0:
                status = False
            elif st == 'r':
                end = True
                while end:
                    cmd=(raw_input('DEBUG[top_dif,top_dd,e|q]:'))
                    if cmd =='e' or cmd=='q' or len(cmd)==0:
                        break
                    else:
                        print eval(cmd)
            elif st == 'g' or st == 'go':
                status = True
                for code in top_dif[:10].index:
                    code = re.findall('(\d+)', code)
                    if len(code) > 0:
                        code = code[0]
                        kind = sl.get_multiday_ave_compare_silent(code)
            elif st == 'clear' or st == 'c':
                top_all = pd.DataFrame()
                status = False
            elif st == 'w' or st == 'a':
                codew = (top_temp.index).tolist()
                if st == 'a':
                    cct.write_to_blocknew(block_path, codew[:10])
                    # sl.write_to_blocknew(all_diffpath, codew)
                else:
                    cct.write_to_blocknew(block_path, codew[:10], False)
                    # sl.write_to_blocknew(all_diffpath, codew, False)
                print "wri ok:%s" % block_path

                # cct.sleep(2)
            else:
                sys.exit(0)
        except (IOError, EOFError, Exception) as e:
            print "Error", e

            traceback.print_exc()
            # raw_input("Except")


            # sl.get_code_search_loop()
            # print data.describe()
            # while 1:
            #     intput=raw_input("code")
            #     print
            # pd = DataFrame(data)
            # print pd
            # parsehtml("""
            # <a href="www.google.com"> google.com</a>
            # <A Href="www.pythonclub.org"> PythonClub </a>
            # <A HREF = "www.sina.com.cn"> Sina </a>
            # """)
'''
{symbol:"sz000001",code:"000001",name:"平安银行",trade:"0.00",pricechange:"0.000",changepercent:"0.000",buy:"12.36",sell:"12.36",settlement:"12.34",open:"0.00",high:"0.00",low:"0",volume:0,amount:0,ticktime:"09:17:55",per:7.133,pb:1.124,mktcap:17656906.355526,nmc:14566203.350486,turnoverratio:0},
{symbol:"sz000002",code:"000002",name:"万  科Ａ",trade:"0.00",pricechange:"0.000",changepercent:"0.000",buy:"0.00",sell:"0.00",settlement:"24.43",open:"0.00",high:"0.00",low:"0",volume:0,amount:0,ticktime:"09:17:55",per:17.084,pb:3.035,mktcap:26996432.575,nmc:23746405.928119,turnoverratio:0},

python -m cProfile -s cumulative timing_functions.py
http://www.jb51.net/article/63244.htm

'''
