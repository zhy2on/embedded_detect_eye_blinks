from scipy.spatial import distance as dist
from imutils import face_utils
from imutils.video import FPS
from sense_hat import SenseHat
import imutils
import time
import dlib
import cv2
import pygame

#### show_digit ####
OFFSET_LEFT = 1
OFFSET_TOP = 2

NUMS =[1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,  # 0
       0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,  # 1
       1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,  # 2
       1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,  # 3
       1,0,0,1,0,1,1,1,1,0,0,1,0,0,1,  # 4
       1,1,1,1,0,0,1,1,1,0,0,1,1,1,1,  # 5
       1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,  # 6
       1,1,1,0,0,1,0,1,0,1,0,0,1,0,0,  # 7
       1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,  # 8
       1,1,1,1,0,1,1,1,1,0,0,1,0,0,1]  # 9

# Displays a single digit (0-9)
def show_digit(val, xd, yd, r, g, b):
  offset = val * 15
  for p in range(offset, offset + 15):
    xt = p % 3
    yt = (p-offset) // 3
    sense.set_pixel(xt+xd, yt+yd, r*NUMS[p], g*NUMS[p], b*NUMS[p])

# Displays a two-digits positive number (0-99)
def show_number(val, r, g, b):
  abs_val = abs(val)
  tens = abs_val // 10
  units = abs_val % 10
  if (abs_val > 9): show_digit(tens, OFFSET_LEFT, OFFSET_TOP, r, g, b)
  show_digit(units, OFFSET_LEFT+4, OFFSET_TOP, r, g, b)

#### detect_py #####
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear

EYE_AR_THRESH = 0.23
EYE_AR_CONSEC_FRAMES = 3
# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0

# initialize timer
TIMER = 0
cycle = 60 # default cycle is 1 minute
ear = 0
bflag = 0

# open sound
pygame.mixer.init()
bang = pygame.mixer.Sound("alarm/sounds_warning.wav")

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
cam = cv2.VideoCapture(0)
time.sleep(1.0)

sense = SenseHat()
sense.clear()
prev = time.time()

# loop over frames from the video stream
while True:
    # grab the frame from the threaded video file stream, resize
    # it, and convert it to grayscale
    # channels)
    fps = FPS().start()
    (grabbed,frame) = cam.read()
    frame = imutils.resize(frame, width=300)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale frame
    rects = detector(gray, 0)

    # joystick
    for event in sense.stick.get_events():
        sense.clear()
        # Check if the joystick was pressed
        if event.action == "pressed":
            if event.direction == "up":
                if cycle <= 480:
                    cycle += 120
                show_number(cycle / 60, 0, 0, 255)
            elif event.direction == "down":
                if cycle >= 240:
                    cycle -= 120
                show_number(cycle / 60, 0, 0, 255)
            elif event.direction == "left": 
                if cycle >= 120:
                    cycle -= 60
                show_number(cycle / 60, 0, 0, 255)
            elif event.direction == "right":
                if cycle <= 540:
                    cycle +=  60
                show_number(cycle / 60, 0, 0, 255)
            elif event.direction == "middle":
                bflag = 1
	    # Wait a while and then clear the screen
        time.sleep(0.4)
        sense.clear()

    # for timer
    cur = time.time()
    if cur-prev >= 1:
        prev = cur
	TIMER = TIMER + 1
    if TIMER != 0 and TIMER % cycle == 0: # change to cycle
        if TOTAL < cycle * 0.2: # change to (cycle / 60) * 12 = cycle * 0.2
            bang.play()
        TOTAL = 0

    # loop over the face detections
    for rect in rects:
    	# for timer
        cur = time.time()
        if cur-prev >= 1:
	        prev = cur
	        TIMER = TIMER + 1

	# determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink frame counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1

        # otherwise, the eye aspect ratio is not below the blink
        # threshold
        else:
            # if the eyes were closed for a sufficient number of
            # then increment the total number of blinks
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1

            # reset the eye frame counter
            COUNTER = 0

        # draw the total number of blinks on the frame along with
        # the computed eye aspect ratio for the frame
        #cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #cv2.putText(frame, "EAR: {:.2f}".format(ear), (210, 30),
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    fps.update()
    fps.stop()
    # show digit
    show_number(TOTAL % 100, 0, 80, 0)
    #cv2.putText(frame, "FPS: {:.2f}".format(fps.fps()), (210, 90),
    #         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # show the frame
    #cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    print(TIMER)
    print("{:.2f}".format(fps.fps()))
    # if the `q` key was pressed, break from the loop
    if bflag:
        break

# do a bit of cleanup
cv2.destroyAllWindows()
cam.release()
sense.clear()
