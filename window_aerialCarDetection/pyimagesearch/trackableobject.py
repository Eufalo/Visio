class TrackableObject:
	def __init__(self, objectID, centroid,path_first_image):
		# store the object ID, then initialize a list of centroids
		# using the current centroid
		self.objectID = objectID
		self.centroids = [centroid]

		# initialize a boolean used to indicate if the object has
		# already been counted or not
		self.counted = False
		# list of lines that the objetc cross
		self.linecounted=[]
		#list of flag_VorH lines True Vertical False Horizontal
		self.list_flag_VorH=[]
		#list of string for the direction L R UP D
		self.direction=[]
		# list of frame that the to cross one area detection
		self.framecounted=[]
		#incialice boolean used to indicate if we use the list of centroid traking
		self.traking_active=False
		#cropped = self.frame[y1:y2, x1:x2]
		#cv2.imshow("cropped", cropped)
		self.path_first_image=path_first_image
	def linecross(self,lines,flag_VorH,direction,totalFrames):
		countv=0
		#loop over vertical lines
		while countv < len(lines):
			#if we  have  line detection and the line and flag_VorH are different from the last detection
			#we tray to count
			aux_flag=True
			if self.list_flag_VorH :
				if self.list_flag_VorH[-1]==flag_VorH and self.linecounted[-1]==countv:
					aux_flag=False
			#if not self.list_flag_VorH or (self.list_flag_VorH[-1]!=flag_VorH and self.linecounted[-1]!=countv):
			if aux_flag:
				#If the last centroid cross between lineX1 to lineX2 and between lineY1 to lineY2
				if flag_VorH:
					if (self.centroids[-1][0] in range(lines[countv][0],lines[countv][2])) and ((self.centroids[-1][1] in range(lines[countv][1],lines[countv][3]))):
						#negative x direction <- go left
						if direction <= 0:
							self.addDetectionLine(countv,flag_VorH,totalFrames,"L")
						#positive x direction -> go right
						else:
							self.addDetectionLine(countv,flag_VorH,totalFrames,"R")
				else:
					if (self.centroids[-1][0] in range(lines[countv][0],lines[countv][2])) and ((self.centroids[-1][1] in range(lines[countv][3],lines[countv][1]))):
						#negative x direction <- go up
						if direction <= 0:
							self.addDetectionLine(countv,flag_VorH,totalFrames,"UP")
						#positive x direction -> go down
						else:
							self.addDetectionLine(countv,flag_VorH,totalFrames,"Down")

			countv+=1
	def addDetectionLine(self,lineCount,flag_VorH,totalFrames,direc):
		self.linecounted.append(lineCount)
		self.framecounted.append(totalFrames)
		self.list_flag_VorH.append(flag_VorH)
		self.direction.append(direc)
	def activeTraking(self):
		if self.traking_active:
			self.traking_active=False
		else:
			self.traking_active=True
