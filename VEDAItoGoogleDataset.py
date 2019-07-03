import os
import shutil
import pandas as pd
'''
1 - car
2 - truck
3 - pickup
4 - tractor
5 - camping
6 - boat
7 - motorcycle
9 - bus
10 - van
11 - other
12 - small car
13 - large car
31 - plane
23 - board
'''
#El cuadro delimitador no puede tener una cordenada fuera de la imagen (0,0)-(1,1)
def normalice1(num):
    if(num>1.0):
        num=1
    return num
#Switch para parsear la clase de int to string
def switch_class(argument):
    switcher = {
        1: "car",
        2: "truck",
        3: "car",
        4: "tractor",
        7: "motorcycle",
        9: "bus",
        10: "van"
    }
    return (switcher.get(argument, "None"))
#path,class,boundingbox VEDAI dataset 1024
data=[]
anotation=[512,1024,1]
file = open('./annotation'+str(anotation[1])+'.txt', "r")
#anotation 512/1024

#Por cada linea del fichero nos quedamos con la id de la imagen, classe del objeto identificado y
#boundingbox del mismo objeto detectado
clase=[]
path=[]
xmin=[]
xmax=[]
ymin=[]
ymax=[]
set=[]
aux=[]
for line in file:
    stip=line.split(" ")
    #Object class
    clas=switch_class(int(stip[12]))
    if(clas != "None"):
        clase.append(clas)
        path.append("gs://cowc_prueba_01/VEDAI/"+stip[0]+"_co.png")
        #El formato de google especifica cada vertice está especificado por los valores de las coordenadas x, y.
        #Estas coordenadas deben ser una flotación en el rango de 0 a 1, donde 0 representa el valor mínimo de xo y, y 1 representa el valor máximo de xo y.
        #En este caso el valor minimo es (0,0) y (anotation[0-1],anotation[0-1])
        #Extraemos el valor minimo y maximo de las anotaciones x[4-8] e y [8-12]
        xmin.append(min(float(i) for i in stip[4:8])/anotation[1])
        xmax.append(normalice1(max(float(i) for i in stip[4:8])/anotation[1]))
        ymin.append(min(float(i) for i in stip[8:12])/anotation[1])
        ymax.append(normalice1(max(float(i) for i in stip[8:12])/anotation[1]))
        aux.append("")
        set.append("UNASSIGNED")
file.close()
#Volcamos los datos extraidos en un fichero . csv
df=pd.DataFrame(data={'set':set,'path': path, 'clase': clase, 'xmin':xmin, 'ymin':ymin,'x2':aux, 'y2':aux, 'xmax':xmax, 'ymax':ymax,'x4':aux, 'y4':aux})
df.to_csv("./VEDAIformatGoogleVertx(0-1)"+str(anotation[1])+".csv",sep=',', encoding='utf-8', index=False,header=False)
#numpy.savetxt("prueba.csv", numpy.asarray(data), delimiter=",")
