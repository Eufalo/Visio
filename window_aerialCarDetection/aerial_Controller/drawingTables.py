from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore
class drawingTables():
#Método constructor de la clase
    def car_table(self):
        #take the detection info in Json
        info_detection=self.detector.info_trackableObjectsToJson()
        #create the header
        header = ["ObjID","DetectionLineas"]
        #load the header in the table
        self.tableCarDetect.setColumnCount(2)
        self.tableCarDetect.setHorizontalHeaderLabels(header)
        #self.tableCarDetect.setRowCount(5)
        r=0
        for object_info in info_detection:
          c=0
          for e in range(2):
              if c==0:
                  item=QTableWidgetItem(object_info["objectID"])
                  print(item)
              else:
                  if c==1:
                    #string to contain the line counting
                    lineV_H=""
                    if len(object_info["linecounted"])>0:
                        for line, flagV_H in object_info["linecounted"],object_info["list_flag_VorH"]:
                            #detect vertical line
                            if flagV_H:
                                lineV_H+="("+line + "V) "
                            else:
                                lineV_H+="("+line + "H) "
                    item=QTableWidgetItem(lineV_H)
              item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
              self.tableCarDetect.setItem(r,c,item )
              c=c+1
          r=r+1
          #self.table_Categorias.cellClicked.connect(self.cellClick)
        	head = self.tableCarDetect.horizontalHeader()
        	head.setSectionResizeMode(QHeaderView.Stretch)
        	head.setStretchLastSection(True)
        	self.tableCarDetect.repaint()
