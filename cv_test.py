import cv2                             
import numpy as np                           #importing libraries
import time
import pdb
cap = cv2.VideoCapture(0)                #creating camera object
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.cv.CV_CAP_PROP_FPS, 125)
numframe = 0
tstart = time.time()
while( cap.isOpened() ) :
	numframe += 1
	ret,img = cap.read()                         #reading the frames
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray,(5,5),0)
	ret,thresh1 = cv2.threshold(blur,50,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	# cv2.imshow('input',gray)                  #displaying the frames
	contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	max_area = 0
	# print "number countours {0}".format(len(contours))
	for i in range(len(contours)):
		cnt=contours[i]
		area = cv2.contourArea(cnt)
		if(area>max_area):
			max_area=area
			ci=i
	cnt=contours[ci]
	print "max contour area {0}".format(max_area)
	hull = cv2.convexHull(cnt)
	drawing = np.zeros(img.shape,np.uint8)

	cv2.drawContours(drawing,[cnt],0,(0,255,0),2)
	cv2.drawContours(drawing,[hull],0,(0,0,255),2)
	# cv2.imshow('contours and hull',drawing)
	# pdb.set_trace()
	k = cv2.waitKey(1)
	# if k == 27:
	if numframe == 700:
		tend = time.time()
		break
fps = numframe/(tend-tstart)
print "FPS = {0}".format(fps)