#! /usr/bin/env python
#coding=utf8
import os
import time
import win32gui
import win32api
import win32con
# http://www.orangecube.net/articles/python-win32-example.html
def find_idxSubHandle(pHandle, winClass, index=0):
    """
    ��֪�Ӵ��ڵĴ�������
    Ѱ�ҵ�index�Ÿ�ͬ���͵��ֵܴ���
    """
    assert type(index) == int and index >= 0
    handle = win32gui.FindWindowEx(pHandle, 0, winClass, None)
    while index > 0:
        handle = win32gui.FindWindowEx(pHandle, handle, winClass, None)
        index -= 1
    return handle

def find_subHandle(pHandle, winClassList):
    """
    �ݹ�Ѱ���Ӵ��ڵľ��
    pHandle���游���ڵľ��
    winClassList�Ǹ����Ӵ��ڵ�class�б�������list-indexС���ӱ�
    """
    assert type(winClassList) == list
    if len(winClassList) == 1:
        return find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])
    else:
        pHandle = find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])
        return find_subHandle(pHandle, winClassList[1:])    

handle = find_subHandle(self.Mhandle, [("ComboBoxEx32", 1), ("ComboBox", 0), ("Edit", 0)])
print "%x" % (handle)


# win32gui.PostMessage(self.Mhandle, win32con.WM_COMMAND, open_ID, 0)
    """
    �򿪲˵�
    """
class FaceGenWindow(object):
    def __init__(self, fgFilePath=None):
        self.Mhandle = win32gui.FindWindow("FaceGenMainWinClass", None)
        self.menu = win32gui.GetMenu(self.Mhandle)
        self.menu = win32gui.GetSubMenu(self.menu, 0)
        print "FaceGen initialization compeleted"
    def menu_command(self, command):
        """
        �˵�����
        ���ص����Ĵ򿪻򱣴�ĶԻ���ľ�� dig_handle
        ����ȷ����ť�ľ�� confBTN_handle
        """
        command_dict = {  # [Ŀ¼�ı��, �򿪵Ĵ�����]
            "open": [2, u"��"],
            "save_to_image": [5, u"���Ϊ"],
        }
        cmd_ID = win32gui.GetMenuItemID(self.menu, command_dict[command][0])
        win32gui.PostMessage(self.Mhandle, win32con.WM_COMMAND, cmd_ID, 0)
        for i in range(10):
            if win32gui.FindWindow(None, command_dict[command][1]):
                break
            else:
                win32api.Sleep(200)
        dig_handle = win32gui.FindWindow(None, command_dict[command][1])
        confBTN_handle = win32gui.FindWindowEx(dig_handle, 0, "Button", None)
        return dig_handle, confBTN_handle
    def open_fg(self, fgFilePath):
        """��fg�ļ�"""
        Mhandle, confirmBTN_handle = self.menu_command('open')
        handle = find_subHandle(Mhandle, [("ComboBoxEx32", 0), ("ComboBox", 0), ("Edit", 0)])
        if win32api.SendMessage(handle, win32con.WM_SETTEXT, 0, os.path.abspath(fgFilePath).encode('gbk')) == 1:
            return win32api.SendMessage(Mhandle, win32con.WM_COMMAND, 1, confirmBTN_handle)
        raise Exception("File opening path set failed")
        
        # handle = find_subHandle(Mhandle, [("ComboBoxEx32", 0), ("ComboBox", 0), ("Edit", 0)]) #�ı��� 
        # win32api.SendMessage(handle, win32con.WM_SETTEXT, 0, os.path.abspath(fgFilePath).encode('gbk'))#��������Ϣ
        #win32api.SendMessage(Mhandle, win32con.WM_COMMAND, 1, confirmBTN_handle) #ȷ�ϼ�
    '''
    buf_size = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1 # Ҫ���Ͻ�β���ֽ�
    str_buffer = win32gui.PyMakeBuffer(buf_size) # ����buffer����
    win32api.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, str_buffer) # ��ȡbuffer
    str = str(str_buffer[:-1]) # תΪ�ַ���
    '''
    
    #����ȷ��֪ͨMain
    # if win32api.SendMessage(CB_handle, win32con.CB_SETCURSEL, format_dict[format], 0) == format_dict[format]:
        # win32api.SendMessage(PCB_handle, win32con.WM_COMMAND, win32con.CBN_SELENDOK&lt;&lt;16+0, CB_handle)  # �ؼ���ID��0�����Ե�λֱ�Ӽ�0
        # win32api.SendMessage(PCB_handle, win32con.WM_COMMAND, win32con.CBN_SELCHANGE&lt;&lt;16+0, CB_handle)
    # else:
        # raise Exception("Change saving type failed")