#! /usr/bin/env python
#coding=gbk
 
# http://my.oschina.net/yangyanxing/blog/167042

# ex2:
# http://stackoverflow.com/questions/32184398/sort-application-windows-side-by-side-in-alphabetical-order/32236936#32236936

import logging

from pywinauto import application,timings
logger = logging.getLogger('pywinauto')
# logger.level = logging.WARNING # or higher
logger.level = logging.DEBUG # or higher
# pywinauto.Timings.window_find_timeout = 10
timings.Timings.window_find_timeout = 0.1

App = application.Application()


# pywinauto.findwindows.find_windows(class_name=None,class_name_re=None, parent=None, process=None, title=None, title_re=None, top_level_only=True, visible_only=True, enabled_only=False, best_match=None, handle=None, ctrl_index=None, predicate_func=None, active_only=False, control_id=None)
def find_wait_pro():
    a_check = lambda: \
    pywinauto.findwindows.find_windows(title=u' Please select a batch file to run:', class_name='#32770')[0]
    try:
        w_handle = pywinauto.timings.WaitUntilPasses(timeout=10, retry_interval=1, a_check)
    except:
        print('Something went wrong')

# app = App.Connect(class_name='Notepad')
# app = App.start('notepad.exe')

# app.notepad.TypeKeys("%FX")
# time.sleep(.5)
# sys.exit(0)
app.Notepad.MenuSelect('����->���ڼ��±�'.decode('gb2312'))
# time.sleep(.5)
 
#���������ַ������Խ��ж�λ�����ڼ��±����ĶԻ���
#top_dlg = app.top_window_() ���Ƽ����ַ�ʽ����Ϊ���ܵõ��Ĳ���������Ҫ��
# about_dlg = app.window_(title_re = u"����", class_name = "#32770",found_index=1)#������Խ�������ƥ��title
about_dlg = app.window_(title_re = u"����", class_name = "#32770")#������Խ�������ƥ��title
# about_dlg.print_control_identifiers()
# app.window_(title_re = u'���ڡ����±���').window_(title_re = u'ȷ��').Click()
# app.Notepad.MenuSelect('����->���ڼ��±�'.decode('gb2312'))
# time.sleep(.5) #ͣ0.5s �����㶼�����������Ƿ񵯳����ˣ�
ABOUT = u'���ڡ����±���'
OK = u'ȷ��'
# lp=''
# app[ABOUT][OK].SendMessage(win32defines.WM_GETTEXT, wparam = 100, lparam = lp)
# about_dlg[OK].Click()
# app[u'���ڡ����±���'][u'ȷ��'].Click()
# print about_dlg.Children()
print "App Focus:%s"%(App.notepad.GetFocus())

if about_dlg.Exists():
    # reboot_dlg.No.Click()
    app[ABOUT][OK].Click()
    about_dlg.WaitNot('visible')  
notetitle=u"�ޱ���"    
# app[notetitle].SetFocus() 
print "App Focus:%s"%(App.notepad.GetFocus())

app.Notepad.TypeKeys(u"������")
dig = app.Notepad.MenuSelect("�༭(E)->�滻(R)".decode('gb2312'))
Replace = u'�滻'
Cancle = u'ȡ��'
Find = u'��������'
rep_dlg = app[Replace]
print rep_dlg.Exists()
print "App Focus:%s"%(App.notepad.GetFocus())
if rep_dlg.Exists():
    print "App Focus:%s"%(App.notepad.GetFocus())
    app[Replace][Cancle].SetFocus() 
    # rep_dlg[Cancle].click()
    # app[Replace][Find].Click()
    app[Replace][Cancle].CloseClick()
    # app.TypeKeys("{ENTER}")ff
    rep_dlg.WaitNot('visible')
    
app.Notepad.TypeKeys("%FX")
dotSave=u"������"
Savename=u"���±�"
app[Savename][dotSave].Click()
# time.sleep(.5)
# about_dlg.ChildWindow(title_re=Replace).Click()
# app.window_(title_re = Replace).window_(title_re = Cancle).Click()
# app[Replace][Cancle].Click()
# dialogs = app.windows_()
# app.Notepad.������