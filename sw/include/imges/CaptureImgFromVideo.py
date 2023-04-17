from sys import displayhook
import cv2
from nbformat import write
import numpy as np
import time
from PIL import Image



def load_image( infilename ) :
    img = Image.open( infilename )
    img.load()
    data = np.asarray( img, dtype=np.uint16)
    return data


def save_image_hex_file( npdata, outfilename, level, cnt_frame) :
    img = Image.fromarray( np.asarray( np.clip(npdata,0,255), dtype="uint16"), "L" )
    file_hex = open('{}.h'.format(outfilename),'x')
    file_hex.write("unsigned char l{}_f{}[ {}*{} ]".format(level, cnt_frame, npdata.shape[1],npdata.shape[0])+"= {\n")
    height=0
    for h in range(npdata.shape[0]):
        for w in range(npdata.shape[1]):
            if height==15:
                file_hex.write('{}, \n'.format(hex(npdata[h][w])))
                height=0
            else:
                height+=1
                file_hex.write('{},'.format(hex(npdata[h][w])))
    file_hex.write("\n};")
    file_hex.close()




cap = cv2.VideoCapture('video.mp4')
# cap = cv2.VideoCapture(cv2.samples.findFile("vtest.avi"))



sHEIGHT = 816
#sHEIGHT = 1088
sWIDTH = 1920



if (cap.isOpened()== False):
  print("Error opening video file")



cnt_frame=0
while(cap.isOpened()):  
    ret, frame = cap.read()
    crop_img = frame[264:, 0:]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    display_frame = cv2.resize(gray, (sWIDTH, sHEIGHT), interpolation= cv2.INTER_LINEAR)
    print('frame ',cnt_frame)
    if cnt_frame>=195:
        # frame_f = str("frame{}").format(cnt_frame)
        # cv2.imwrite("{}.jpg".format(frame_f), gray)
        for i in range(1,4):
            if i==1:
                sH = 816
                #sH = 1088
                sW = 1920
                frame = cv2.resize(gray, (sW, sH), interpolation= cv2.INTER_LINEAR)
                frame_rgb = cv2.resize(crop_img, (sW, sH), interpolation=cv2.INTER_LINEAR)
            if i==2:
                sH = 408
                #sH = 544
                sW = 960
                frame = cv2.resize(gray, (sW, sH), interpolation= cv2.INTER_LINEAR)
                frame_rgb = cv2.resize(crop_img, (sW, sH), interpolation=cv2.INTER_LINEAR)
            if i==3:
                sH = 204
                #sH = 272
                sW = 480
                frame = cv2.resize(gray, (sW, sH), interpolation= cv2.INTER_LINEAR)
                frame_rgb = cv2.resize(crop_img, (sW, sH), interpolation=cv2.INTER_LINEAR)
            frame_f = str("L{}_Y8bit_{}x{}_frame{}").format(i,sW,sH,cnt_frame)
            frame_f_rgb = str("L{}_RGB_{}x{}_frame{}").format(i, sW, sH, cnt_frame)

            print(frame_f)
            cv2.imwrite("{}.jpg".format(frame_f), frame)
            cv2.imwrite("{}.jpg".format(frame_f_rgb), frame_rgb)
            image_data = load_image("{}.jpg".format(frame_f))
            save_image_hex_file(image_data, frame_f, i, cnt_frame)
    if cnt_frame>=200: break
    cnt_frame+=1
    # time.sleep(0.5)
    # cv2.imshow('Image', display_frame)
    cv2.waitKey(1)
cap.release()
cv2.destroyAllWindows()