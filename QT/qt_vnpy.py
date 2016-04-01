# -*- coding: gbk -*-
import pyQt
class LogMonitor(QtGui.QTableWidget):
    """������ʾ��־"""
    signal = QtCore.pyqtSignal(type(Event()))

    #----------------------------------------------------------------------
    def __init__(self, eventEngine, parent=None):
        """Constructor"""
        super(LogMonitor, self).__init__(parent)
        self.__eventEngine = eventEngine

        self.initUi()
        self.registerEvent()

    #----------------------------------------------------------------------
    def initUi(self):
        """��ʼ������"""
        self.setWindowTitle(u'��־')

        self.setColumnCount(2)                     
        self.setHorizontalHeaderLabels([u'ʱ��', u'��־'])

        self.verticalHeader().setVisible(False)                 # �ر���ߵĴ�ֱ��ͷ
        self.setEditTriggers(QtGui.QTableWidget.NoEditTriggers) # ��Ϊ���ɱ༭״̬

        # �Զ������п�
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)        

    #----------------------------------------------------------------------
    def registerEvent(self):
        """ע���¼�����"""
        # Qtͼ�������GUI���±���ʹ��Signal/Slot���ƣ������п��ܵ��³������
        # ��������Ƚ�ͼ�θ��º�����ΪSlot�����ź���������
        # Ȼ���źŵĴ�������ע�ᵽ�¼�����������
        self.signal.connect(self.updateLog)
        self.__eventEngine.register(EVENT_LOG, self.signal.emit)

    #----------------------------------------------------------------------
    def updateLog(self, event):
        """������־"""
        # ��ȡ��ǰʱ�����־����
        t = time.strftime('%H:%M:%S',time.localtime(time.time()))   
        log = event.dict_['log']                                    

        # �ڱ�����Ϸ�����һ��
        self.insertRow(0)              

        # ������Ԫ��
        cellTime = QtGui.QTableWidgetItem(t)    
        cellLog = QtGui.QTableWidgetItem(log)

        # ����Ԫ�������
        self.setItem(0, 0, cellTime)            
        self.setItem(0, 1, cellLog)