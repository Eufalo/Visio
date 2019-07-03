# we use the library centroideTracker and trackableobject which were developed for Adrian Rosebrock
#the creator of the pyimagesearch website
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

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
	help="path to input video")
ap.add_argument("-o", "--output", required=True,
	help="path to output video")
ap.add_argument("-y", "--yolo", required=True,
	help="base path to YOLO directory")
ap.add_argument("-c", "--confidence", type=float, default=0.7,
	help="minimum probability to filter weak detections")
ap.add_argument("-t", "--threshold", type=float, default=0.3,
	help="threshold when applyong non-maxima suppression")
ap.add_argument("-s", "--skip-frames", type=int, default=50,
	help="# of skip frames between detections")
args = vars(ap.parse_args())

#def detectionModel():

# load the COCO class labels our YOLO model was trained on
labelsPath = os.path.sep.join([args["yolo"], "coco.names"])
LABELS = open(labelsPath).read().strip().split("\n")
# derive the paths to the YOLO weights and model configuration
weightsPath = os.path.sep.join([args["yolo"], "yolov3.weights"])
configPath = os.path.sep.join([args["yolo"], "yolov3.cfg"])

# load our YOLO object detector trained on COCO dataset (80 classes)
# and determine only the *output* layer names that we need from YOLO
print("[INFO] loading YOLO from disk...")
net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]


print("[INFO] opening video file...")
vs = cv2.VideoCapture(args["input"])

# initialize the video writer/output
writer = None

# instantiate our centroid tracker, ct is initialize as  a list for store
ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
# cointainer inicialice for store the dlib correlation trackers
trackers = []
#inicialice the container of direction lines Horizontal. Use on smart direction counter
linesH=[]
linesV=[]
# map each unique object ID to a TrackableObject
trackableObjects = {}

# initialize the total number of frames processed
totalFrames = 0
# with the total number of vehicles n
totalCount = 0

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
W = None
H = None

# start the frames per second throughput estimator
fps = FPS().start()

# loop over frames from the video stream
while True:
	# grab the next frame
	frame = vs.read()
	frame = frame[1]

	# if we are viewing a video and we did not grab a frame then we
	# have reached the end of the video
	if args["input"] is not None and frame is None:
		break

	# resize the frame to have a maximum width of 700 pixels
	frame = imutils.resize(frame, width=700)
	# convert the frame from BGR to RGB for dlib
	# increase the acurazy of the traking
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# if the frame dimensions are empty, set them
	if W is None or H is None:
		(H, W) = frame.shape[:2]

	# if we are supposed to be writing a video to disk, initialize
	# the writer
	if args["output"] is not None and writer is None:
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter(args["output"], fourcc, 30,
			(W, H), True)

	# initialize the current status along with our list of bounding
	status = "Waiting"
	# initilize the box rectangles
	rects = []

	# We need to skip some frames  (args["skip_frames"])  because
	# the car detected will be comput expensive and "detection it not in seudo-realtime"
	if totalFrames % args["skip_frames"] == 0:
		# set the status and initialize  on detection
		status = "Detecting"
		# initialize a container for our new set of object we need to traking
		trackers = []

		# convert the frame to a blob
		blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
		swapRB=True, crop=False)
		# pass the blob through the blob over the net
		net.setInput(blob)
		start = time.time()
		# obtain the detections
		layerOutputs = net.forward(ln)
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
				if confidence > args["confidence"]:

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

					# add the tracker to our list of trackers so we can
					# utilize it during skip frames
					trackers.append(tracker)

	# During the skip frame
	else:
		# To obtain a higher frame processing throughput and a seudo-realtime
		# we should utilize the object *trackers* for this reason first we do a
		# loop over the trackers
		for tracker in trackers:
			# set the status of our system to be 'tracking'
			status = "Tracking"

			# update the tracker and grab the updated position
			tracker.update(rgb)
			pos = tracker.get_position()

			# unpack the position object
			startX = int(pos.left())
			startY = int(pos.top())
			endX = int(pos.right())
			endY = int(pos.bottom())

			# add the bounding box coordinates to the rectangles list
			rects.append((startX, startY, endX, endY))
	# use the centroid tracker to associate the (1) old object
	# centroids with (2) the newly computed object centroids
	objects = ct.update(rects)

	#loop over the rects for printing
	for i in rects:
		cv2.rectangle(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)
		#cv2.rectangle(frame,  (i[0]+5, i[1]+5), (i[2]+5, i[3]+5), (255, 255, 255), 1)
	for i in linesH:
		cv2.line(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)
	for i in linesV:
		cv2.line(frame,  (i[0], i[1]), (i[2], i[3]), (0, 255, 0), 4)

	# loop over the tracked objects
	for (objectID, centroid) in objects.items():
		# check to see if a trackable object exists for the current
		# object ID
		to = trackableObjects.get(objectID, None)

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
			if linesV:
				to.linecross(linesV,True,directionx,totalFrames)
			if linesH:
				to.linecross(linesH,False,directiony,totalFrames)



			#the distance traking between the centroid[-1] to centroid[-2] -> √((x2-x1)^2 + (y2-y1)^2)
			(x2,y2)=(to.centroids[-1][0],to.centroids[-1][1])
			(x1,y1)=(to.centroids[-2][0],to.centroids[-2][1])
			distance = math.sqrt(pow((x2-x1),2)+pow(((y2-y1)),2))


			# check to see if the object has been counted or not
			if not to.counted:
				# if the direction is negative (indicating the object
				# is moving up) AND the centroid is above the center
				# line, count the object
				totalCount+=1
				to.counted = True

		# store the trackable object in our dictionary
		trackableObjects[objectID] = to

		# draw both the ID of the object and the centroid of the
		# object on the output frame
		text = "ID {}".format(objectID)
		cv2.putText(frame, text, (centroid[0] - 15, centroid[1] - 15),
			cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 255, 0), 2)
		cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
		#cv2.rectangle(frame,  (rects[i][0], rects[i][1]), (rects[i][2], rects[i][3]), (0, 255, 0), 5)


	# construct a tuple of information we will be displaying on the
	# frame
	info = [
		("Contador", totalCount),
		("Status", status),
	]

	# loop over the info tuples and draw them on our frame
	for (i, (k, v)) in enumerate(info):
		text = "{}: {}".format(k, v)
		cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	# check to see if we should write the frame to disk
	if writer is not None:
		writer.write(frame)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	# if the `s` key was pressed, can add special region who cointain a vehicle
	elif key == ord("s"):
		# select the bounding box of the object we want to track (make
		# sure you press ENTER or SPACE after selecting the ROI)
		box = cv2.selectROI("Frame", frame, fromCenter=False,
			showCrosshair=True)
		# create a new object tracker for the bounding box and add it
		# to our multi-object tracker
		tracker = dlib.correlation_tracker()
		rect = dlib.rectangle( box[0], box[1], box[0] + box[2], box[1] + box[3])
		tracker.start_track(rgb, rect)
		# add the tracker to our list of trackers so we can
		# utilize it during skip frames
		trackers.append(tracker)
	# if the `v` key was pressed, u can add a vertical line
	elif key == ord("v"):
			# select the bounding box of the object we want to track (make
			# sure you press ENTER or SPACE after selecting the ROI)
			box = cv2.selectROI("Frame", frame, fromCenter=False,
				showCrosshair=True)
			# create a new line for counting in that WAy
			print((box[0], box[1],box[0]+box[2],box[1]+ box[3]))
			linesV.append((box[0], box[1],box[0]+box[2],box[1]+ box[3]))

	# if the `h` key was pressed, u can add a horizontal line
	elif key == ord("h"):
			# select the bounding box of the object we want to track (make
			# sure you press ENTER or SPACE after selecting the ROI)
			box = cv2.selectROI("Frame", frame, fromCenter=False,
				showCrosshair=True)
			# create a new line for counting in that WAy
			linesH.append((box[0], box[1]+ box[3],box[0]+box[2],box[1]))
			print(linesH)
	# increment the total number of frames processed thus far and
	# then update the FPS counter
	totalFrames += 1
	fps.update()


# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# check to see if we need to release the video writer pointer
if writer is not None:
	writer.release()

# if we are not using a video file, stop the camera video stream
if not args.get("input", False):
	vs.stop()

# otherwise, release the video file pointer
else:
	vs.release()

# close any open windows
cv2.destroyAllWindows()
