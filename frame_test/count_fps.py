import cv2

########### add  ##################
import time # time library
###################################

CAM_ID = 0

cam = cv2.VideoCapture(CAM_ID) #make camera
if cam.isOpened() == False: #check camera
    print 'Can\'t open the CAM(%d)' % (CAM_ID)
    exit()

# resize when making window
cv2.namedWindow('CAM_Window')

########### add  ##################
prevTime = 0 #before time
###################################
while(True):

    #open image of camera
    ret, frame = cam.read()
     

    ########### add ##################
    #current time(s)
    curTime = time.time()

    #curr - before
    #time around once
    sec = curTime - prevTime
    #before = curr;
    prevTime = curTime

    # caculating frame
    # 1 / time per frame
    fps = 1/(sec)

    # debug message
    print "Time {0} " . format(sec)
    print "Estimated fps {0} " . format(fps)

    # fps to str
    str = "FPS : %0.1f" % fps

    # show
    cv2.putText(frame, str, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
    ###################################


    #show window
    cv2.imshow('CAM_Window', frame)


    #while 10ms wait
    if cv2.waitKey(10) >= 0:
       break;

#close window
cam.release()
cv2.destroyWindow('CAM_Window')
