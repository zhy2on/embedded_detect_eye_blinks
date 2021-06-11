
from sense_hat import SenseHat


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

sense = SenseHat()
sense.clear()
show_number(511, 0, 0, 255)
import time
time.sleep(1)
show_number(612, 0, 0, 255)
time.sleep(1)
show_number(1, 0, 0, 255)