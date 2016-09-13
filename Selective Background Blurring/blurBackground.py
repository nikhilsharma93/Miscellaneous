#!/usr/bin/python
'''
This script can be used to gradually blur out selected portion of an image.
The current code is suited to keep the face of a person (if present in the given
image) in focus, by gradually blurring the surroundings. However, it can be
tailored at ease to select any region in an image and blur the rest of it.
Please refer to requirements.txt, to see the packages used/necessary.
'''


from __future__ import division
__author__='Nikhil Sharma'
#import base64
import cv2
import numpy as np
import dlib
import math
import sys, os


def blurBackgroundMinimal(imgOrg , locations , blurAmount = 20):
    def rotateImage(image, angle,image_center):
        image_center = tuple(image_center)
        rot_mat = cv2.getRotationMatrix2D(image_center,angle,1.0)
        result = cv2.warpAffine(image, rot_mat, (image.shape[1],image.shape[0]),flags=cv2.INTER_LINEAR)
        return result
    try:
        height, width = imgOrg.shape[:2]
        imgOrgClone=np.copy(imgOrg)
        locations = np.array(locations)
        if len(locations)==3:
            faceLeft,faceTop,faceRight,faceBottom = locations[0]
            areaOfFace = (faceRight-faceLeft)*(faceBottom-faceTop)
            areaOfImage=width*height

            #only if the face covers less than 70% of the image, blur it. Else, return the original image.
            if areaOfFace/areaOfImage < 0.7:
                #print areaOfFace, areaOfImage
                pts=[]
                xWidth=(locations[1][16]-locations[1][0])
                yHeight=(locations[0][3]-locations[0][1])
                pts.append([max(locations[1][0]-xWidth/4,0),max(locations[0][1]-yHeight/2.5,0)])
                pts.append([min(locations[1][16]+xWidth/4,width),max(locations[0][1]-yHeight/2.5,0)])
                pts.append([min(locations[1][16]+xWidth/4,width),locations[0][3]])
                pts.append([min(locations[1][16]+7*xWidth/12,width),min(locations[0][3]+yHeight/6,height)])
                pts.append([min(locations[1][16]+7*xWidth/12,width),min(locations[0][3]+yHeight,height)])
                pts.append([max(locations[1][0]-7*xWidth/12,0),min(locations[0][3]+yHeight,height)])
                pts.append([max(locations[1][0]-7*xWidth/12,0),min(locations[0][3]+yHeight/6,height)])
                pts.append([max(locations[1][0]-xWidth/4,0),locations[0][3]])
                kernel=np.ndarray([8,8],dtype='float')
                kernel.fill(1)
                imgBase=np.ndarray([height,width],dtype='float')
                imgBase.fill(0)
                imgBase=cv2.fillConvexPoly(imgBase,np.array(pts,dtype='int32'),(1))

                #get the alignment of the face to align the mask accordingly
                if locations[1][0]==locations[1][16]:
                    angle=90
                else:
                    angle=math.degrees(math.atan((locations[2][16]-locations[2][0])/(locations[1][16]-locations[1][0])))

                #get the center (moments) of the mask, about which the image will be rotated
                moments=cv2.moments(imgBase)
                xCenter=moments['m10']/moments['m00']
                yCenter=moments['m01']/moments['m00']
                centroid=[yCenter,xCenter]
                imgBase=rotateImage(imgBase,-angle,centroid)
                #uncomment the next line to see the mask that is used for blurring
                #cv2.imshow('mask',imgBase); cv2.waitKey()
                maskt1=imgBase.copy()
                kernel1=np.ndarray([3,3],dtype='float')
                kernel1.fill(1)
                maskt1=cv2.dilate(maskt1,kernel1)
                blurRadius=4
                for loopDilate in range(4*blurRadius):
                    imgBaseClone=imgBase.copy()
                    imgBase=cv2.dilate(imgBase,kernel)
                    imgDifference=imgBase-imgBaseClone
                    imgDifference=np.where(imgDifference[:,:]==(blurRadius-loopDilate/4)/blurRadius,\
                                                                (blurRadius-1/4-loopDilate/4)/blurRadius,\
                                                                0)
                    imgBase=imgDifference+imgBaseClone
                imgBase=imgBase*(1-maskt1)+maskt1
                imgOrgBlur=cv2.blur(imgOrg,(blurAmount,blurAmount))
                imgBlur3D=np.ndarray([height,width,3],dtype='float')
                imgBlur3D[:,:,0]=imgBase
                imgBlur3D[:,:,1]=imgBase
                imgBlur3D[:,:,2]=imgBase
                blurredImage=(imgBlur3D*imgOrgClone+(1-imgBlur3D)*imgOrgBlur).astype('uint8')
            else:
                blurredImage=imgOrg
        else:
            blurredImage=imgOrg
        return blurredImage
    except Exception as e:
        print 'Error blurring the background (minimal)'
        raise

def getFacialLocations(img,facePredictorPath):
    predictor = dlib.shape_predictor(facePredictorPath)
    maxAreaOfFace=0
    faceDetector = dlib.get_frontal_face_detector()
    dets = faceDetector(img, 1)
    for k, d in enumerate(dets):
        areaCoveredByFace=(d.right()-d.left())*(d.bottom()-d.top())
        if areaCoveredByFace > maxAreaOfFace:
            dMax=d
            maxAreaOfFace=areaCoveredByFace
    try:
        loc=[]
        loc.append([dMax.left(),dMax.top(),dMax.right(),dMax.bottom()])
        shape = predictor(img, dMax)
        loc.append([shape.part(i).x for i in range(68)])
        loc.append([shape.part(i).y for i in range(68)])
    except:
        loc=[]
    return loc


if len(sys.argv) != 2 and len(sys.argv) != 3:
    print '\nPlease enter the required arguments. Follow the syntax "python <filename> <path to input image> <blur value (optional; Default = 20)>"\n'
    sys.exit()

if not os.path.isfile(sys.argv[1]):
    print '\nThe image was not found. Please make sure to provide the correct path.\n'
    sys.exit()

inputImage = cv2.imread(sys.argv[1])
blurAmount = int(sys.argv[2]) if len(sys.argv) == 3 else 20

#If the image's size is too large, it might consume some more time for processing.
#To make the process faster, an image of size > 900*1200 (height*width) will be decimated.
heightMax=900; widthMax=1200; heightOrg=inputImage.shape[0]; widthOrg=inputImage.shape[1]
if heightOrg > heightMax or widthOrg > widthMax:
    decimationFactor=max(heightOrg/heightMax,widthOrg/widthMax)
    height=int(heightOrg/decimationFactor); width=int(widthOrg/decimationFactor)
    inputImage=cv2.resize(inputImage,(width,height))

currentDir = os.path.dirname(os.path.abspath(__file__))
facePredictorPath = currentDir+'/shape_predictor_68_face_landmarks.dat'
if not os.path.isfile(facePredictorPath):
    print '\nThe .dat file was not found. Please make sure to include it in the same working directory as this.\n'
    sys.exit()


facialLocations = getFacialLocations(inputImage,facePredictorPath)
if not facialLocations:
    print '\nSorry. The program did not detect a face. Please try with another image.\n'
    sys.exit()

outputImage = blurBackgroundMinimal(inputImage , facialLocations , blurAmount)
cv2.imshow('output',outputImage); cv2.waitKey()
