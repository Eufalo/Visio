from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import math
import cv2
import os
class Detection:
#Método constructor de la clase
    def __init__(self,yolo_arg):
        # load the COCO class labels our YOLO model was trained on
    	labelsPath = os.path.sep.join([yolo_arg, "coco.names"])
    	LABELS = open(labelsPath).read().strip().split("\n")
    	# derive the paths to the YOLO weights and model configuration
    	weightsPath = os.path.sep.join([yolo_arg, "yolov3.weights"])
    	configPath = os.path.sep.join([yolo_arg, "yolov3.cfg"])

    	# load our YOLO object detector trained on COCO dataset (80 classes)
    	# and determine only the *output* layer names that we need from YOLO
    	print("[INFO] loading YOLO from disk...")
    	self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    	self.ln = self.net.getLayerNames()
    	self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
    	# initialize the video writer/output
    	writer = None
    	# instantiate our centroid tracker, ct is initialize as  a list for store
    	self.ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    	# cointainer inicialice for store the dlib correlation trackers
    	self.trackers = []
    	#inicialice the container of direction lines. Use on smart direction counter
    	self.linesH=[]
    	self.linesV=[]
    	# map each unique object ID to a TrackableObject
    	self.trackableObjects = {}
        # with the total number of vehicles n
    	self.totalCount = 0
        # initilize the box rectangles
    	self.rects = []
    def info_lines(self):
        objectsJson=[]
        if self.linesH:
            for i in self.linesH:
                json = {'lineID': '', 'flag_VorH': ""
                ,'direction':[] ,'objectID': []}
                json['lineID']= i
                json['flag_VorH']=False
                #add the json line to the cointainer
                objectsJson.append(json)
        if self.linesV:
            for i in self.linesV:
                json = {'lineID': '', 'flag_VorH': ""
                ,'direction':[] ,'objectID': []}
                json['lineID']= i
                json['flag_VorH']=True
                #add the json line to the cointainer
                objectsJson.append(json)
        #loop over the trackable object
        for objectid in self.trackableObjects:
            #get the trackable object
            to=self.trackableObjects.get(objectid)
            #if the object have some line counted
            if to.linecounted:
                for i,line in enumerate(to.linecounted):
                    for e,obj in enumerate(objectsJson):
                        #if we find the same line than the json we add a car
                        if obj['lineID']==line and objectsJson[e]['flag_VorH']==to.list_flag_VorH[i]:
                            json['direction'].append(to.direction[i])
                            json['objectID'].append(to.objectID)
    #fuction give a line informacion -> Array of Json -> id line flag for vertical or h line (V F)
    #array of direction and the array of object samte iterable position
    #[{'lineID': '', 'flag_VorH': "",'direction':[] ,'objectID': []}}]
    def info_lines_trackableObjectsToJson(self):
        #incialice cointainer
        objectsJson=[]
        #loop over the trackable object
        for objectid in self.trackableObjects:
            #get the trackable object
            to=self.trackableObjects.get(objectid)
            #if the object have some line counted
            if to.linecounted:
                #loop over the lines counter the trackable object
                for i,line in enumerate(to.linecounted):
                    #if the Json it empty create
                    if not objectsJson:
                        #create a json for the trackable object info
                        json = {'lineID': '', 'flag_VorH': ""
                        ,'direction':[] ,'objectID': []}
                        json['lineID']= line
                        json['flag_VorH']=to.list_flag_VorH[i]
                        json['direction'].append(to.direction[i])
                        json['objectID'].append(to.objectID)
                        #add the json line to the cointainer
                        objectsJson.append(json)
                    else:
                        #incialice varible for check if the line it not in json
                        aux_flag=True;
                        aux_e=0
                        #loop over the line in the json
                        for e,obj in enumerate(objectsJson):
                            #if we find the same line than the json we add a car
                            if obj['lineID']==line and obj['flag_VorH']==to.list_flag_VorH[i]:
                                objectsJson[e]['direction'].append(to.direction[i])
                                objectsJson[e]['objectID'].append(to.objectID)
                                aux_flag=False
                            aux_e=e
                        #if we do all the loop and the flag it true we add the new line in the Json
                        if aux_e==len(objectsJson)-1 and aux_flag:
                            #create a json for the trackable object info
                            json = {'lineID': '', 'flag_VorH': []
                            ,'direction':[] ,'objectID': []}
                            json['lineID']= line
                            json['flag_VorH']=to.list_flag_VorH[i]
                            json['direction'].append(to.direction[i])
                            json['objectID'].append(to.objectID)
                            #add the json line  to the cointainer
                            objectsJson.append(json)

        return objectsJson

    def info_id_trackableObjectsToJson(self,objectID):
        to = self.trackableObjects.get(objectID, None)
        # if exist the trackable object
        if to is not None:
            json = {'objectID': '', 'linecounted': to.linecounted , 'list_flag_VorH': to.list_flag_VorH
            ,'framecounted': to.framecounted,'direction': to.direction,'centroids':to.centroids}
            return json
        return None
    def info_trackableObjectsToJson(self):
        #incialice cointainer
        trackableObjectsJson=[]
        #loop over the trackable object
        for objectid in self.trackableObjects:
            #get the trackable object
            to=self.trackableObjects.get(objectid)

            #create a json for the trackable object info
            json = {'objectID': to.objectID, 'linecounted':  to.linecounted, 'list_flag_VorH': to.list_flag_VorH
            ,'framecounted': to.framecounted,'direction': to.direction,'centroids':to.centroids}
            #add the json trackable object to the cointainer
            trackableObjectsJson.append(json)
        return trackableObjectsJson
    def print_boundingbox(self,frame):
        for i in self.rects:
        	cv2.rectangle(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)
        	#cv2.rectangle(frame,  (i[0]+5, i[1]+5), (i[2]+5, i[3]+5), (255, 255, 255), 1)
    def paint_linesH(self,frame):
        for i in self.linesH:
        	cv2.line(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)
    def paint_linesV(self,frame):
        #loop over the vertical lines for printing
        for i in self.linesV:
        	cv2.line(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)
    #update the informacion of the tracker object and drawing the frame with the id and centroids
    def updateObjectInfo(self,frame,totalFrames):
        # use the centroid tracker to associate the (1) old object
        # centroids with (2) the newly computed object centroids
        objects = self.ct.update(self.rects)
        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
        	# check to see if a trackable object exists for the current
        	# object ID
        	to = self.trackableObjects.get(objectID, None)

        	# if there is no existing trackable object, create one
        	if to is None:
        		to = TrackableObject(objectID, centroid)

        	# otherwise, there is a trackable object so we can utilize it
        	# to determine direction
        	else:

        		# If the mean directionx it bigger than directiony will tell us
        		#than the direction it right or left or if the directiony it bigges will
        		#know that the direction it up or down
        		directionx = centroid[0] - to.centroids[-1][0]
        		directiony = centroid[1] - to.centroids[-1][1]
        		to.centroids.append(centroid)
        		#Detection for vertical and horizontal lines
        		if self.linesV:
        			to.linecross(self.linesV,True,directionx,totalFrames)
        		if self.linesH:
        			to.linecross(self.linesH,False,directiony,totalFrames)
        		#the distance traking between the centroid[-1] to centroid[-2] -> √((x2-x1)^2 + (y2-y1)^2)
        		(x2,y2)=(to.centroids[-1][0],to.centroids[-1][1])
        		(x1,y1)=(to.centroids[-2][0],to.centroids[-2][1])
        		distance = math.sqrt(pow((x2-x1),2)+pow(((y2-y1)),2))
        		# check to see if the object has been counted or not
        		if not to.counted:
        			# if the direction is negative (indicating the object
        			# is moving up) AND the centroid is above the center
        			# line, count the object
        			self.totalCount+=1
        			to.counted = True

        	# store the trackable object in our dictionary
        	self.trackableObjects[objectID] = to
        	# draw both the ID of the object and the centroid of the
        	# object on the output frame
        	text = "ID {}".format(objectID)
        	cv2.putText(frame, text, (centroid[0] - 15, centroid[1] - 15),
        		cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 0), 2)
        	cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
    #function for generate new detection or traking
    def new_detection(self,frame,flag,W, H,rgb,coef,totalFrames):
        self.rects = []
        # if flag is true strart the detection
        if flag:
        	# initialize a container for our new set of object we need to traking
        	self.trackers = []
        	# convert the frame to a blob
        	blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
        	swapRB=True, crop=False)
        	# pass the blob through the blob over the self.net
        	self.net.setInput(blob)
        	start = time.time()
        	# obtain the detections
        	layerOutputs = self.net.forward(self.ln)
        	end = time.time()

        	#initialize the list storage for the confidences
        	confidences = []
        	#initialize the list storage the classes
        	classIDs = []
        	# loop over the detections
        	for output in layerOutputs:
        		# loop over each of the detections
        		for detection in output:
        			# extract the class ID and confidence (i.e., probability) of
        			# the current object detection
        			scores = detection[5:]
        			classID = np.argmax(scores)
        			confidence = scores[classID]
        			# filter out weak predictions by ensuring the detected
        			# probability is greater than the minimum probability
        			if confidence > coef:
        				# scale the bounding box coordinates back relative to the
        				# size of the image, keeping in mind that YOLO actually
        				# returns the center (x, y)-coordinates of the bounding
        				# box followed by the boxes' width and height
        				box = detection[0:4] * np.array([W, H, W, H])
        				(centerX, centerY, width, height) = box.astype("int")
        				# use the center (x, y)-coordinates to derive the top and
        				# and left corner of the bounding box
        				x = int(centerX - (width / 2))
        				y = int(centerY - (height / 2))
        				# inicialice the tracker
        				tracker = dlib.correlation_tracker()
        				# construct a dlib rectangle object from the bounding
        				# box coordinates
        				# we need to keep in mind that we have the left-top (x,y)position
        				# so we need to sum the with and height to print the correct rectangle position
        				rect = dlib.rectangle( x, y, x + width, y + height)
        				#then start the dlib correlation
        				tracker.start_track(rgb, rect)
        				# add the tracker to our list of self.trackers so we can
        				# utilize it during skip frames
        				self.trackers.append(tracker)



        # if flag is false strart the tracking
        else:
        	# To obtain a higher frame processing throughput and a seudo-realtime
        	# we should utilize the object *trackers* for this reason first we do a
        	# loop over the trackers
            for tracker in self.trackers:
            	# update the tracker and grab the updated position
            	tracker.update(rgb)
            	pos = tracker.get_position()

            	# unpack the position object
            	startX = int(pos.left())
            	startY = int(pos.top())
            	endX = int(pos.right())
            	endY = int(pos.bottom())

            	# add the bounding box coordinates to the rectangles list
            	self.rects.append((startX, startY, endX, endY))
            #update the informacion of all objects
            self.updateObjectInfo(frame,totalFrames)
