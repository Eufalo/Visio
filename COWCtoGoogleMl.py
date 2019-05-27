import os
import shutil
from bs4 import BeautifulSoup
import pandas as pd
import cv2
#El cuadro delimitador no puede tener una cordenada fuera de la imagen (0,0)-(1,1)
def normalice1(num):
    if(num>1.0):
        num=1
    return num
#Listamos directorio raiz ya que ejecutamos dicho script en la carpeta del dataset
clase=[]
path=[]
xmin=[]
xmax=[]
ymin=[]
ymax=[]
set=[]
aux=[]

for i in os.listdir(path='./Training'):
    #Comprobamos que sea un directorio
    if(os.path.isdir('./Training/'+i) and i!="images" and i!="labels"):
        print('Leyendo ./Training/'+i+'/'+i+'.xml')
        infile = open('./Training/'+i+'/'+i+'.xml',"r")
        #infile = open('./MunichCrossroad01/MunichCrossroad01.xml',"r")
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        #Buamos todas las imagenes que contiene el fichero xml
        frames = soup.find_all('frame')
        #Por cada imagen debemos estraer los objetos anotados y wardarlos en el fichero
        for frame in frames:
            #Eliminamos C:
            pathimageInit=frame.get("file").split(":")[1]
            #Dividimos el path de la imagen para quedarnos con el nombre de esta
            pathimage=pathimageInit.split("/")
            objectlist=frame.find_all('objectlist')
            objects=frame.find_all('object')
            #El formato de google especifica cada vertice está especificado por los valores de las coordenadas x, y.
            #Estas coordenadas deben ser una flotación en el rango de 0 a 1, donde 0 representa el valor mínimo de xo y, y 1 representa el valor máximo de xo y.
            #En este caso el valor minimo es (0,0) y el maximo lo calculamos utilizando la libreria Opencv
            img = cv2.imread('./images/'+pathimage[2]+"_"+pathimage[3])
            #dimensions tupla de filas, columnas y canales
            dimensions = img.shape
            #En cada imagen buscamos los objetos que contiene dicha imagen
            for object in objects:
                obj=object.find_all('box')
                for  o in obj:
                    clase.append('car')
                    #Segmento de google ->gs://cowc_prueba_01/images/
                    path.append("gs://cowc_prueba_01/images/"+pathimage[2]+"_"+pathimage[3])
                    #Xc e Yc centro del ob objeto-> min=(Xc-w/2),(Yc-h/2) max=(Xc+w/2),(Yc+h/2)
                    #Division entre la dimension para lograr que el vertice tenga el formato % especificado por Google 0-1
                    xmin.append(normalice1((float(o.get("xc"))-float(o.get("w"))/2)/dimensions[1]))
                    ymin.append(normalice1((float(o.get("yc"))-float(o.get("h"))/2)/dimensions[0]))
                    xmax.append(normalice1((float(o.get("xc"))+float(o.get("w"))/2)/dimensions[1]))
                    ymax.append(normalice1((float(o.get("yc"))+float(o.get("h"))/2)/dimensions[0]))
                    set.append("UNASSIGNED")
                    aux.append("")
df=pd.DataFrame(data={'set':set,'path': path, 'clase': clase, 'xmin':xmin, 'ymin':ymin,'x2':aux, 'y2':aux, 'xmax':xmax, 'ymax':ymax,'x4':aux, 'y4':aux})
df.to_csv("./COWCgoogleAnotation(0-1).csv",sep=',', encoding='utf-8', index=False,header=False)
            #print('./'+i+'/'+i+'.xml')
