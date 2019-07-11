from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog,QMessageBox,QTableWidgetItem,QWidget,QHeaderView,QLabel
from PyQt5.QtGui import QIcon,QImage,QBrush
from PyQt5 import uic
from PyQt5 import QtCore,QtWidgets

def drawing_car_table(self):
    #take the detection info in Json
    info_detection=self.detector.info_trackableObjectsToJson()
    #create the header
    header = ["ID","Obje","Linea, direccion"]
    #load the header in the table
    self.tableCarDetect.setColumnCount(3)
    self.tableCarDetect.setHorizontalHeaderLabels(header)
    self.tableCarDetect.setRowCount(len(info_detection))
    r=0
    #decrease loop over the info detection
    #we can see the last detection in the frist positions
    for aux_i in range(len(info_detection)-1,-1,-1):
        c=0
        for e in range(3):
            if c==1:
                #take the first image of the object
                img=QImage("./pyimagesearch/imagen_crapped/"
                +str(info_detection[aux_i]['objectID'])+".png")
                item=QTableWidgetItem("")
                item.setBackground(QBrush(img))
            elif c==0:
                item=QTableWidgetItem(str(info_detection[aux_i]['objectID']))
            elif c==2:
                #string to contain the line counting
                lineV_H=""
                if len(info_detection[aux_i]['linecounted'])>0:
                    #decrease loop over the line counted
                    #we can see the last line counted in the left positions
                    for i in range(len(info_detection[aux_i]['list_flag_VorH'])-1,-1,-1):
                        #detect vertical line
                        if info_detection[aux_i]['list_flag_VorH'][i]:
                            lineV_H+="("+str(info_detection[aux_i]['linecounted'][i]) + "V, "+str(info_detection[aux_i]['direction'][i]) +") "
                        else:
                            lineV_H+="("+str(info_detection[aux_i]['linecounted'][i]) + "H, "+ str(info_detection[aux_i]['direction'][i]) +") "
                item=QTableWidgetItem(str(lineV_H))
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.tableCarDetect.setItem(r,c,item )
            c=c+1
        r=r+1

    head = self.tableCarDetect.horizontalHeader()
    head.setSectionResizeMode(QHeaderView.ResizeToContents)
    head.setStretchLastSection(True)
    self.tableCarDetect.repaint()
def drawing_lines_tableH(self):
    #take the detection info in Json
    info_lines_detection=self.detector.info_lines_trackableObjectsToJson()
    #create the header
    header = ["LineID","CarID, direccion"]
    #load the header in the table horizontal
    self.tableHline.setColumnCount(2)
    self.tableHline.setHorizontalHeaderLabels(header)
    self.tableHline.setRowCount(len(info_lines_detection))
    r=0
    #decrease loop over the info line detection
    #we can see the last line in the frist positions
    for aux_i in range(len(info_lines_detection)-1,-1,-1):
        if not info_lines_detection[aux_i]['flag_VorH']:
            #print("Horizontales",info_lines_detection[aux_i])
            c=0
            for e in range(2):
                if c==0:
                    item=QTableWidgetItem(str(info_lines_detection[aux_i]['lineID']))
                elif c==1:
                    #string to contain the line counting
                    lineObjId_Dir=""
                    #decrease loop over the line counted
                    #we can see the last line counted in the left positions
                    for i in range(len(info_lines_detection[aux_i]['objectID'])-1,-1,-1):
                        lineObjId_Dir+="("+str(info_lines_detection[aux_i]['objectID'][i]) +str(info_lines_detection[aux_i]['direction'][i]) +") "

                    item=QTableWidgetItem(str(lineObjId_Dir))
                item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                self.tableHline.setItem(r,c,item )
                c=c+1
            r=r+1
    #self.table_Categorias.cellClicked.connect(self.cellClick)
    head = self.tableHline.horizontalHeader()
    head.setSectionResizeMode(QHeaderView.ResizeToContents)
    head.setStretchLastSection(True)
    self.tableHline.repaint()
def drawing_lines_tableV(self):
    #take the detection info in Json
    info_lines_detection=self.detector.info_lines_trackableObjectsToJson()
    #create the header
    header = ["LineID","CarID, direccion"]
    #load the header in the table horizontal
    self.tableVline.setColumnCount(2)
    self.tableVline.setHorizontalHeaderLabels(header)
    self.tableVline.setRowCount(len(info_lines_detection))
    r=0
    #decrease loop over the info line detection
    #we can see the last line in the frist positions
    for aux_i in range(len(info_lines_detection)-1,-1,-1):
        if info_lines_detection[aux_i]['flag_VorH']:
            #print("VERTICAL",info_lines_detection[aux_i])
            c=0
            for e in range(2):
                if c==0:
                    item=QTableWidgetItem(str(info_lines_detection[aux_i]['lineID']))
                elif c==1:
                    #string to contain the line counting
                    lineObjId_Dir=""
                    #decrease loop over the line counted
                    #we can see the last line counted in the left positions
                    for i in range(len(info_lines_detection[aux_i]['objectID'])-1,-1,-1):
                        lineObjId_Dir+="("+str(info_lines_detection[aux_i]['objectID'][i]) +str(info_lines_detection[aux_i]['direction'][i]) +") "

                    item=QTableWidgetItem(str(lineObjId_Dir))
                item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                self.tableVline.setItem(r,c,item )
                c=c+1
            r=r+1
    #self.table_Categorias.cellClicked.connect(self.cellClick)
    head = self.tableVline.horizontalHeader()
    head.setSectionResizeMode(QHeaderView.ResizeToContents)
    head.setStretchLastSection(True)
    self.tableVline.repaint()


    #QMessageBox.about(self,row)
