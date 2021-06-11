from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from imutils.video import FPS
from sense_hat import SenseHat
import imutils
import time
import dlib
import cv2
import pygame

#### show digit ####
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

def show_digit(val, xd, yd, r, g, b):
    offset = val * 15
    for p in range(offset, offset + 15):
        xt = p % 3
        yt = (p-offset) // 3
        sense.set_pixel(xt+xd, yt+yd, r*NUMS[p], g*NUMS[p], b*NUMS[p])

def show_number(val, r, g, b):
    sense.clear()
    abs_val = abs(val)
    hunds = (abs_val // 100) % 8
    tens = (abs_val % 100) / 10
    units = abs_val % 10
    if (abs_val > 99):
        for i in range(1, hunds + 1):
            sense.set_pixel(8 - i, 0, 255,0,0)
    if (abs_val > 9): show_digit(tens, OFFSET_LEFT, OFFSET_TOP, r, g, b)
    show_digit(units, OFFSET_LEFT+4, OFFSET_TOP, r, g, b)

#### detect blink #####
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)
    return ear

EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 5

# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0

# initialize the timer, cycle, break flag
TIMER = 0
cycle = 60 # default cycle is 1 minute
bflag = 0
ear = 0

# open sound
pygame.mixer.init()
bang = pygame.mixer.Sound("alarm/sounds_warning.wav")
bang.set_volume(1)

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
vs = VideoStream(src=0).start()
time.sleep(1.0)

sense = SenseHat()
sense.clear()
prev = time.time()

# loop over frames from the video stream
while True: 
    # for timer
    cur = time.time()
    if cur-prev >= 1:
        prev = cur
        TIMER = TIMER + 1
    if TIMER != 0 and (TIMER % 4 == 0):
        if TOTAL < 2: # (cycle / 60) * 12 = cycle * 0.2
            bang.play(1)
            time.sleep(1)
        TOTAL = 0
        time.sleep(1)
        sense.clear()

    # joystick
    for event in sense.stick.get_events():
        sense.clear()
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
    if bflag:
        break
    
    fps = FPS().start()
    frame = vs.read()
    frame = imutils.resize(frame, width=300) # resize the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale frame
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1

        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
            COUNTER = 0

        """
        # draw the total number of blinks on the frame along with
        # the computed eye aspect ratio for the frame
        cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (210, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        """
    fps.update()
    fps.stop()
    # show digit
    show_number(TOTAL % 100, 0, 80, 0)    
    
    """
    cv2.putText(frame, "FPS: {:.2f}".format(fps.fps()), (210, 90),
             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if (key == ord("q") or bflag):
        break
    """
    print("EAR: {:.2f}".format(ear))
    print("TIME: {:d}".format(TIMER))
    print("FPS: {:.2f}".format(fps.fps()))
    print("TOTAL: {:d}".format(TOTAL))
    
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
sense.clear()
