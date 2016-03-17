import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick
# from matplotlib.finance import volume_overlay3
from matplotlib.finance import volume_overlay2
# from matplotlib.dates import num2date
# from matplotlib.dates import date2num
import matplotlib.mlab as mlab
import datetime
import pandas as pd
import tushare as ts
from matplotlib.dates import  DateFormatter, WeekdayLocator, HourLocator, \
     DayLocator, MONDAY, num2date,date2num

mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays    = DayLocator() 
weekFormatter = DateFormatter('%b %d')  # Eg, Jan 12
dayFormatter = DateFormatter('%d')      # Eg, 12
     
def plot_candlestick(frame, ylabel='BTC/USD', candle_width=1.0, freq='1W'):
    """
    Plot candlestick graph.
    @param frame: bitcoin OHLC data frame to be plotted.
    @param ylabel: label on the y axis.
    @param candle_width: width of the candles in days.
    @param freq: frequency of the plotted x labels.
    """
    candlesticks = zip(
        date2num(frame.index.to_datetime().to_pydatetime()),
        frame['open'],
        frame['close'],
        frame['high'],
        frame['low'],
        frame['volume'])
    # Figure
    ax0 = plt.subplot2grid((3,1), (0,0), rowspan=2)
    ax1 = plt.subplot2grid((3,1), (2,0), rowspan=1, sharex=ax0)
    # ax1.xaxis.set_major_locator(mondays)
    # ax1.xaxis.set_minor_locator(alldays)
    # ax0.xaxis.set_major_formatter(weekFormatter)
    plt.subplots_adjust(bottom=0.15)
    plt.setp(ax0.get_xticklabels(), visible=False)
    ax0.grid(True)
    ax0.set_ylabel(ylabel, size=20)
    # Candlestick
    candlestick(ax0, candlesticks,
        width=0.5*candle_width,
        colorup='g', colordown='r')
    # Get data from candlesticks for a bar plot
    dates = np.asarray([x[0] for x in candlesticks])
    volume = np.asarray([x[5] for x in candlesticks])
    # Make bar plots and color differently depending on up/down for the day
    pos = frame['open'] - frame['close'] < 0
    neg = frame['open'] - frame['close'] > 0
    ax1.grid(True)
    ax1.bar(dates[pos], volume[pos], color='g', width=candle_width, align='center')
    ax1.bar(dates[neg], volume[neg], color='r', width=candle_width, align='center')
    # Scale the x-axis tight
    ax1.set_xlim(min(dates),max(dates))
    ax1.set_ylabel('VOLUME', size=20)
    # Format the x-ticks with a human-readable date.
    xt = [date2num(date) for date in pd.date_range(
            start=min(frame.index),
            end=max(frame.index),
            freq=freq)]
    # ticks = ax1.get_xticks()
    # print frame.index.values[0],ticks
    # xt = [frame.index.values[i] for i in (np.append(ticks[:-1], len(frame) - 1))]
    ax1.set_xticks(xt)
    # xt_labels = [num2date(d).strftime('%Y-%m-%d\n%H:%M:%S') for d in xt]
    xt_labels = [num2date(d).strftime('%Y-%m-%d') for d in xt]
    ax1.set_xticklabels(xt_labels,rotation=15, horizontalalignment='right')
    # Plot
    # plt.ion()
    # plt.hold(True)
    plt.show()
    return (ax0, ax1)
    
r =  ts.get_hist_data('sz',start='2016-01-01')
r.sort_index(ascending=True,inplace=True)
plot_candlestick(r)

import sys
sys.exit(0)





# r.index=r.index.to_datetime().to_pydatetime()
# r.reset_index(inplace=True)
# r['date']=date

# prin

# r['date']=r['date'].apply(lambda date:datetime.datetime.strptime(date[:10],'%Y-%m-%d'))
# the dates in my example file-set are very sparse (and annoying) change the dates to be sequential
# for i in range(len(r)-1):
    # r['date'][i+1] = r['date'][i] + datetime.timedelta(days=1)
# r.index.to_datetime()  
candlesticks = zip(date2num(r.index.tolist()),r['open'],r['close'],r['high'],r['low'],r['volume'])

fig = plt.figure()
ax = fig.add_subplot(1,1,1)

ax.set_ylabel('Quote ($)', size=20)
candlestick(ax, candlesticks,width=1,colorup='g', colordown='r')

# shift y-limits of the candlestick plot so that there is space at the bottom for the volume bar chart
pad = 0.25
yl = ax.get_ylim()
ax.set_ylim(yl[0]-(yl[1]-yl[0])*pad,yl[1])

# create the second axis for the volume bar-plot
ax2 = ax.twinx()

# bc = volume_overlay2(ax2, r.close,r.volume, colorup='g', colordown='r', alpha=0.5, width=1)
# ax2.add_collection(bc)

# set the position of ax2 so that it is short (y2=0.32) but otherwise the same size as ax
ax2.set_position(matplotlib.transforms.Bbox([[0.125,0.1],[0.9,0.32]]))

# get data from candlesticks for a bar plot
dates = [x[0] for x in candlesticks]
dates = np.asarray(dates)
volume = [x[5] for x in candlesticks]
volume = np.asarray(volume)
# print volume

# make bar plots and color differently depending on up/down for the day
pos = r['open']-r['close']<0
neg = r['open']-r['close']>0
ax2.bar(dates[pos],volume[pos],color='green',width=1,align='center')
ax2.bar(dates[neg],volume[neg],color='red',width=1,align='center')

#scale the x-axis tight
ax2.set_xlim(min(dates),max(dates))
# the y-ticks for the bar were too dense, keep only every third one
yticks = ax2.get_yticks()
ax2.set_yticks(yticks[::3])

ax2.yaxis.set_label_position("right")
ax2.set_ylabel('Volume', size=20)

xt = ax.get_xticks()
new_xticks = [datetime.date.isoformat(num2date(d)) for d in xt]
ax.set_xticklabels(new_xticks,rotation=15, horizontalalignment='right')

# plt.ion()
plt.hold(True)
plt.show()

# import tushare as ts
# df= ts.get_hist_data('sh',start='2016-01-01').sort_index(ascending=True)
# fig = plt.figure(figsize=(16, 10))
# ax1 = fig.add_subplot(111)
# candlestick2_ochl(ax1, df.open,df.close,df.high,df.low, width=.6, colorup='g', colordown='r')
# ticks = ax1.get_xticks()
# ax1.set_xticklabels([df.index.values[i] for i in (np.append(ticks[:-1], len(df) - 1))],rotation=45, horizontalalignment='right')
# plt.show()

