# -*- coding:utf-8 -*-
# !/usr/bin/env python

import gc
import re
import sys
import time
import traceback
import urllib2

import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame

import JohhnsonUtil.johnson_cons as ct
import singleAnalyseUtil as sl
from JSONData import realdatajson as rl
from JSONData import tdx_data_Day as tdd
from JohhnsonUtil import LoggerFactory as LoggerFactory
from JohhnsonUtil import commonTips as cct


# from logbook import Logger,StreamHandler,SyslogHandler
# from logbook import StderrHandler


def downloadpage(url):
    fp = urllib2.urlopen(url)
    data = fp.read()
    fp.close()
    return data


def parsehtml(data):
    soup = BeautifulSoup(data)
    for x in soup.findAll('a'):
        print x.attrs['href']


def html_clean_content(soup):
    [script.extract() for script in soup.findAll('script')]
    [style.extract() for style in soup.findAll('style')]
    soup.prettify()
    reg1 = re.compile("<[^>]*>")  # 剔除空行空格
    content = reg1.sub('', soup.prettify())
    print content


def get_sina_url(vol='0', type='0', pageCount='100'):
    # if len(pageCount) >=1:
    url = ct.SINA_DD_VRatio_All % (
        ct.P_TYPE['http'], ct.DOMAINS['vsf'], ct.PAGES['sinadd_all'], pageCount, ct.DD_VOL_List[vol], type)
    # print url
    return url


def get_sina_all_dd(vol='0', type='0', retry_count=3, pause=0.001):
    if len(vol) != 1 or len(type) != 1:
        return None
    else:
        print ("Vol:%s  Type:%s" % (ct.DD_VOL_List[vol], ct.DD_TYPE_List[type]))
    # symbol = _code_to_symbol(code)
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            ct._write_console()
            url = get_sina_url(vol, type)
            page = urllib2.urlopen(url)
            html_doc = page.read()
            # print (html_doc)
            # soup = BeautifulSoup(html_doc,fromEncoding='gb18030')
            # print html_doc
            pageCount = re.findall('fillCount\"\]\((\d+)', html_doc, re.S)
            if len(pageCount) > 0:
                start_t = time.time()
                pageCount = pageCount[0]
                if int(pageCount) > 100:
                    if int(pageCount) > 10000:
                        print "BigBig:", pageCount
                        pageCount = '10000'

                    print "AllBig:", pageCount
                    html_doc = urllib2.urlopen(get_sina_url(vol, type, pageCount=pageCount)).read()
                    print (time.time() - start_t)

            soup = BeautifulSoup(html_doc, "lxml")
            print (time.time() - start_t)
            # abc= (soup.find_all('script',type="text/javascript"))
            # print(len(abc))
            # print (abc[4].text).strip().find('window["fillCount"]')
            # print abc[4].contents


            # pageCount= soup.find_all(string=re.compile('fillCount\"\]\((\d+)'))
            # pageCount=re.findall('(\d+)',pageCount[0])

            # sys.exit(0)
            # print soup.find_all('__stringHtmlPages')

            # sys.exit(0)

            # soup = BeautifulSoup(html_doc.decode('gb2312','ignore'))
            # print soup.find_all('div', id="divListTemplate")
            # for i in soup.find_all('tr',attrs={"class": "gray"."class":""}):
            alldata = {}
            dict_data = {}
            # print soup.find_all('div',id='divListTemplate')

            row = soup.find_all('div', id='divListTemplate')
            sdata = []
            if len(row) >= 1:
                '''
                colums:CHN name

                '''
                # firstCells = row[0].find('tr')
                # th_cells = firstCells.find_all('th')
                # td_cells = firstCells.find_all('td')
                # m_name=th_cells[0].find(text=True)
                # m_code=th_cells[1].find(text=True)
                # m_time=th_cells[2].find(text=True)
                # m_status=th_cells[3].find(text=True)
                # m_detail=th_cells[4].find(text=True)
                # m_price=td_cells[0].find(text=True)
                # m_vol=td_cells[1].find(text=True)
                # m_pre_p=td_cells[2].find(text=True)
                # print "m_name:",m_name,m_pre_p
                for tag in row[0].find_all('tr', attrs={"class": True}):
                    # print tag
                    th_cells = tag.find_all('th')
                    td_cells = tag.find_all('td')
                    m_name = th_cells[0].find(text=True)
                    m_code = th_cells[1].find(text=True)
                    m_time = th_cells[2].find(text=True)
                    # m_detail=(th_cells[4]).find('a')["href"]   #detail_url
                    m_price = td_cells[0].find(text=True)
                    m_vol = float(td_cells[1].find(text=True).replace(',', '')) * 100
                    m_pre_p = td_cells[2].find(text=True)
                    m_status_t = th_cells[3].find(text=True)
                    if m_status_t in status_dict.keys():
                        m_status = status_dict[m_status_t]
                        # print m_status
                    sdata.append({'code': m_code, 'time': m_time, 'vol': m_vol, 'price': m_price, 'pre_p': m_pre_p,
                                  'status': m_status, 'name': m_name})
                    # sdata.append({'code':m_code,'time':m_time,'vol':m_vol,'price':m_price,'pre_p':m_pre_p,'detail':m_detail,'status':m_status,'name':m_name})
                    # print sdata
                    # print m_name
                    # break
            # pd = DataFrame(sdata,columns=['code','time','vol','price','pre_p','detail','status','name'])
            df = DataFrame(sdata, columns=['code', 'time', 'vol', 'price', 'pre_p', 'status', 'name'])
            # for row in soup.find_all('tr',attrs={"class":"gray","class":""}):
        except Exception as e:
            print "Except:", (e)
        else:
            return df
        raise IOError(ct.NETWORK_URL_ERROR_MSG)

def parseArgmain():
    # from ConfigParser import ConfigParser
    # import shlex
    import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-s', '--start', type=int, dest='start',
    # help='Start date', required=True)
    # parser.add_argument('-e', '--end', type=int, dest='end',
    # help='End date', required=True)
    # parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
    # help='Enable debug info')
    # parser.add_argument('foo', type=int, choices=xrange(5, 10))
    # args = parser.parse_args()
    # print args.square**2
    parser = argparse.ArgumentParser()
    parser.add_argument('dt', type=str, nargs='?', help='20150612')
    
    # parser.add_argument('dt', nargs='?', type=str, help='20150612')
    # parser.add_argument('dt', nargs='?', type=str, help='20150612')
    # parser.add_argument('-dt', action="store", dest="dtype", type=str, nargs='?',help='20150612')
    # parser.add_argument('dt', action="store", dest="dt", type=str, nargs='?',help='20150612')
    # parser.add_argument('e', nargs='?',action="store", dest="end", type=str, help='end')
    # parser.add_argument('end', nargs='?', type=str, help='20160101')
    # parser.add_argument('-d', action="store", dest="dtype", type=str, nargs='?', choices=['d', 'w', 'm'], default='d',
                        # help='DateType')
    # parser.add_argument('-p', action="store", dest="ptype", type=str, choices=['f', 'b'], default='f',
                        # help='Price Forward or back')
    # parser.add_argument('-help',type=str,help='Price Forward or back')
    # args = parser.parse_args()
    # args=parser.parse_args(input)
    return parser

if __name__ == "__main__":
    # parsehtml(downloadpage(url_s))
    # StreamHandler(sys.stdout).push_application()
    log = LoggerFactory.getLogger('SinaMarketNew')
    # log.setLevel(LoggerFactory.DEBUG)

    # handler=StderrHandler(format_string='{record.channel}: {record.message) [{record.extra[cwd]}]')
    # log.level=log.debug
    # error_handler = SyslogHandler('Sina-M-Log', level='ERROR')

    cct.set_console(160, 15)
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
    base_path = tdd.get_tdx_dir()
    block_path = tdd.get_tdx_dir_blocknew() + '061.blk'
    status_change = False
    lastpTDX_DF=''
    duration_date=120
    # all_diffpath = tdd.get_tdx_dir_blocknew() + '062.blk'
    while 1:
        try:
            # df = sina_data.Sina().all
            df = rl.get_sina_Market_json('all')
            top_now = rl.get_market_price_sina_dd_realTime(df, vol, type)
            # print top_now.loc['300208','name']
            # top_now.to_hdf("testhdf5", 'marketDD', format='table', complevel=9)
            # df_count = len(df)
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
                if len(top_all) == 0 and len(lastpTDX_DF) == 0:
                    top_all = top_now
                    codelist = top_all.index.tolist()
                    log.info('toTDXlist:%s' % len(codelist))
                    tdxdata = tdd.get_tdx_all_day_LastDF(codelist,dt=duration_date)
                    log.debug("TdxLastP: %s %s" % (len(tdxdata), tdxdata.columns.values))
                    tdxdata.rename(columns={'low': 'llow'}, inplace=True)
                    tdxdata.rename(columns={'high': 'lhigh'}, inplace=True)
                    tdxdata.rename(columns={'close': 'lastp'}, inplace=True)
                    tdxdata.rename(columns={'vol': 'lvol'}, inplace=True)
                    tdxdata = tdxdata.loc[:, ['llow', 'lhigh', 'lastp', 'lvol', 'date']]
                    log.debug("TDX Col:%s" % tdxdata.columns.values)
                    top_all = top_all.merge(tdxdata, left_index=True, right_index=True, how='left')
                    lastpTDX_DF=tdxdata
                    log.info('Top-merge_now:%s' % (top_all[:1]))
                    top_all = top_all[top_all['llow'] > 0]
                    

                elif    len(top_all) == 0 and len(lastpTDX_DF) > 0:
                    top_all = top_now
                    top_all = top_all.merge(lastpTDX_DF, left_index=True, right_index=True, how='left')
                    # lastpTDX_DF=tdxdata
                    log.info('Top-merge_now:%s' % (top_all[:1]))
                    top_all = top_all[top_all['llow'] > 0]
                    
                else:
                    if 'counts' in top_now.columns.values:
                        if not 'counts' in top_all.columns.values:
                            top_all['counts'] = 0
                            top_all['prev_p'] = 0
                    for symbol in top_now.index:
                        top_all.loc[symbol, 'buy'] = top_now.loc[symbol, 'buy']
                        # '''
                        # code = rl._symbol_to_code(symbol)
                        if symbol in top_all.index and top_all.loc[symbol, 'buy'] <> 0:
                            count_n = top_now.loc[symbol, 'buy']
                            count_a = top_all.loc[symbol, 'buy']
                            if cct.get_now_time_int() < 930:
                                top_all.loc[symbol, 'buy'] = top_now.loc[symbol, 'buy']
                            else:
                                if not count_n == count_a:
                                    top_now.loc[symbol, 'diff'] = round(
                                        ((float(count_n) - float(count_a)) / float(count_a) * 100), 1)
                                    if status_change and 'counts' in top_now.columns.values:
                                        print "change:", time.time() - time_s
                                        top_all.loc[symbol, 'buy':'prev_p'] = top_now.loc[symbol, 'buy':'prev_p']
                                    else:
                                        top_all.loc[symbol, 'diff':'low'] = top_now.loc[symbol, 'diff':'low']
                                elif 'counts' in top_now.columns.values:
                                    top_all.loc[symbol, 'diff':'prev_p'] = top_now.loc[symbol, 'diff':'prev_p']
                                else:
                                    top_now.loc[symbol, 'diff'] = round(
                                        ((float(top_now.loc[symbol, 'buy']) - float(top_all.loc[symbol, 'lastp'])) / float(top_all.loc[symbol, 'lastp']) * 100), 1)
                                    top_all.loc[symbol, 'diff':'low'] = top_now.loc[symbol, 'diff':'low']
                        # '''
                # top_all=top_all.sort_values(by=['diff','percent','counts'],ascending=[0,0,1])
                # top_all=top_all.sort_values(by=['diff','ratio','percent','counts'],ascending=[0,1,0,1])
                # top_all = top_all[top_all.open>=top_all.low*0.99]
                # top_all = top_all[top_all.buy >= top_all.open*0.99]
                # top_all = top_all[top_all.trade >= top_all.low*0.99]
                # top_all = top_all[top_all.trade >= top_all.high*0.99]
                # top_all = top_all[top_all.buy >= top_all.lastp]
                # top_all = top_all[top_all.percent >= 0]
                
                # if cct.get_now_time_int() < 930 or cct.get_now_time_int() > 1505 or (cct.get_now_time_int() > 1125 and cct.get_now_time_int() < 1505):
                    # top_all['diff'] = (
                        # map(lambda x, y: round((x - y) / y * 100, 1), top_all['buy'].values, top_all['lastp'].values))
                # if  cct.get_now_time_int() > 930 and cct.get_now_time_int() < 1505:
                    # top_all['diffA'] = (
                        # map(lambda x, y: round((x - y) / y * 100, 1), top_all['buy'].values, top_all['lastp'].values))
                top_all['diff'] = (
                        map(lambda x, y: round((x - y) / y * 100, 1), top_all['buy'].values, top_all['lastp'].values))
                        
                top_dif = top_all
                log.info('dif1:%s' % len(top_dif))
                log.info(top_dif[:1])
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


                print ("N:%s K:%s %s G:%s" % (
                    now_count, len(top_all[top_all['buy'] > 0]),
                    len(top_now[top_now['volume'] <= 0]), len(top_dif))),
                # print "Rt:%0.3f" % (float(time.time() - time_Rt))
                print "Rt:%0.1f dT:%s" % (float(time.time() - time_Rt),cct.get_time_to_date(time_s))
                if 'counts' in top_dif.columns.values:
                    top_dif = top_dif.sort_values(by=['diff', 'volume', 'percent', 'counts', 'ratio'],
                                                  ascending=[0, 0, 0, 1, 1])
                else:
                    print "Good Morning!!!"
                    top_dif = top_dif.sort_values(by=['diff', 'percent', 'ratio'], ascending=[0, 0, 1])

                # top_all=top_all.sort_values(by=['percent','diff','counts','ratio'],ascending=[0,0,1,1])
                # print rl.format_for_print(top_dif[:10])
                top_dd= pd.concat([top_dif[:10],top_dif[-5:]],axis=0)
                top_dd= top_dd.loc[:,['name','buy','diff','volume','percent','ratio','counts','lastp','date']]
                print rl.format_for_print(top_dd)
                # if cct.get_now_time_int() < 930 or cct.get_now_time_int() > 1505 or (cct.get_now_time_int() > 1125 and cct.get_now_time_int() < 1505):
                    # print rl.format_for_print(top_dif[-10:])
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
                    time.sleep(30)
                elif int_time < 930:
                    time.sleep((930 - int_time) * 60)
                    top_all = pd.DataFrame()
                    time_s = time.time()
                else:
                    time.sleep(60)
            elif cct.get_work_duration():
                while 1:
                    time.sleep(60)
                    if cct.get_work_duration():
                        print ".",
                        time.sleep(60)
                    else:
                        top_all = pd.DataFrame()
                        time_s = time.time()
                        print "."
                        break
            else:
                '''
                st = raw_input("status:[go(g),clear(c),date(dt),quit(q,e),W(w),Wa(a)]:")
                if len(st) == 0:
                    status = False
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
                    
                elif st.startswith('d') or st.startswith('dt'):
                    st = raw_input('Low[20150612]:')
                    parser = parseArgmain()
                    args = parser.parse_args(st.split())
                    if args.dt != None and len(args.dt)==8:
                        duration_date=args.dt
                        top_all = pd.DataFrame()
                        status = False
                        lastpTDX_DF=''
                    # print ("reload new Duration:%s"%duration_date)
                    
                elif st == 'w' or st == 'a':
                    codew = (top_dif.index).tolist()
                    if st == 'a':
                        cct.write_to_blocknew(block_path, codew[:10])
                        # sl.write_to_blocknew(all_diffpath, codew)
                    else:
                        cct.write_to_blocknew(block_path, codew[:10], False)
                        # sl.write_to_blocknew(all_diffpath, codew, False)
                    print "wri ok:%s" % block_path

                    # time.sleep(2)
                else:
                    sys.exit(0)
                '''
                raise KeyboardInterrupt("StopTime.")
        except (KeyboardInterrupt) as e:
            # print "key"
            print "KeyboardInterrupt:", e
            # time.sleep(1)
            # if success > 3:
            #     raw_input("Except")
            #     sys.exit(0)
            st = raw_input("status:[go(g),clear(c),date(dt),quit(q,e),W(w),Wa(a)]:")
            if len(st) == 0:
                status = False
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
            elif st.startswith('d') or st.startswith('dt'):
                st = raw_input('LowD[20150612]:')
                parser = parseArgmain()
                args = parser.parse_args(st.split())
                if args.dt != None and len(args.dt)>0:
                    duration_date=args.dt
                    top_all = pd.DataFrame()
                    status = False
                    lastpTDX_DF=''
                # print ("reload new Duration:%s"%duration_date)
                
            elif st == 'w' or st == 'a':
                codew = (top_dd.index).tolist()
                if st == 'a':
                    cct.write_to_blocknew(block_path, codew)
                    # sl.write_to_blocknew(all_diffpath, codew)
                else:
                    cct.write_to_blocknew(block_path, codew, False)
                    # sl.write_to_blocknew(all_diffpath, codew, False)
                print "wri ok:%s" % block_path

                # time.sleep(2)
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