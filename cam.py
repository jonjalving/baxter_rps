#!/usr/bin/env python 
import cv2
import numpy as np
import time
import rospy
import bisect
import std_msgs.msg

rospy.init_node('hand_detector')
pub = rospy.Publisher('user_hand', std_msgs.msg.String, queue_size=1, tcp_nodelay=True)

numframe = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.cv.CV_CAP_PROP_FPS, 125)

hand_list = [(75, 'rock'), (200, 'scissors'), (1000,'paper')]
hand_list.sort()
# ~25 for rock, ~70 for scissors, ~250 for paper (fingers spread)
tstart = time.time()
while( cap.isOpened() ):
    ret,img = cap.read()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    ret,thresh1 = cv2.threshold(blur,50,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  
    contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(img.shape,np.uint8)

    max_area=0
   
    for i in range(len(contours)):
            cnt=contours[i]
            area = cv2.contourArea(cnt)
            if(area>max_area):
                max_area=area
                ci=i
    cnt=contours[ci]
    hull = cv2.convexHull(cnt)
    moments = cv2.moments(cnt)
    if moments['m00']!=0:
                cx = int(moments['m10']/moments['m00']) # cx = M10/M00
                cy = int(moments['m01']/moments['m00']) # cy = M01/M00
              
    centr=(cx,cy)       
    cv2.circle(img,centr,5,[0,0,255],2)       
    cv2.drawContours(drawing,[cnt],0,(0,255,0),2) 
    cv2.drawContours(drawing,[hull],0,(0,0,255),2) 
          
    cnt = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    hull = cv2.convexHull(cnt,returnPoints = False)

    try:
        defects = cv2.convexityDefects(cnt,hull)
        mind=0
        maxd=0
        if defects is not None:
            total_def = 0.0
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])
                dist = cv2.pointPolygonTest(cnt,centr,True)
                cv2.line(img,start,end,[0,255,0],2)
                
                cv2.circle(img,far,5,[0,0,255],-1)
                total_def += d/256.0
        print(i)
        hand_ind = bisect.bisect_right(hand_list, (total_def,))
        print "hand index is {0}".format(hand_ind)
        hand_shape = hand_list[hand_ind][1]
        print "total defect distance {0}".format(total_def)
        print "predicted hand shape is {0}".format(hand_shape)
        # ~25 for rock, ~70 for scissors, ~250 for paper (fingers spread)
        pub.publish(hand_shape)
        i=0
    except:
        print "error"

    cv2.imshow('output',drawing)
    cv2.imshow('input',img)
                
    k = cv2.waitKey(1)
    if k == 27:
        tend = time.time()
        break
fps = numframe/(tend-tstart)
print "FPS = {0}".format(fps)