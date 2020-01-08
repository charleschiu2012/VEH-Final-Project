import os, time
import argparse
import cv2
import numpy as np
import socket
import pickle

#定義區
########################################
modelType = "yolo-tiny"  #yolo or yolo-tiny
confThreshold = 0.3  #Confidence threshold
nmsThreshold = 0.1   #Non-maximum suppression threshold

classesFile = "./data/obj.names";
modelConfiguration = "./data/yolov3-tiny.cfg";
modelWeights = "./data/yolov3-tiny_5000.weights";

displayScreen = False  #Do you want to show the image on LCD?
outputToFile = True   #output the predicted result to image or video file

image_path = "./images/image.jpg"

#Label & Box
fontSize = 0.35
fontBold = 1
labelColor = (0,0,255)
boxbold = 1
boxColor = (255,255,255)

if(modelType=="yolo"):
    inpWidth = 608       #Width of network's input image
    inpHeight = 608      #Height of network's input image
else:
    inpWidth = 416       #Width of network's input image
    inpHeight = 416      #Height of network's input image

classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
 
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
########################################


#Function
########################################
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def getROI_Color(roi):
    mean_blue = np.mean(roi[:,:,0])
    mean_green = np.mean(roi[:,:,1])
    mean_red = np.mean(roi[:,:,2])
    actual_name, closest_name = get_colour_name((mean_red, mean_green, mean_blue))

    return actual_name, closest_name, (mean_blue, mean_green, mean_red)
#-----------------------------------------------------------------

# Get the names of the output layers
def getOutputsNames(net):
    layersNames = net.getLayerNames()

    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
 
    classIds = []
    confidences = []
    boxes = []
    result = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])
                print("Predict:", classes[classId])
                result.append([1, classId, confidence, center_x, center_y, width, height, left, top])

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
    # with open("detection.txt", "w") as f:
    #     print(result, file =f)
    return result    
########################################

#Main
########################################
print("Here is 'playYOLO'. Connected to server")

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 8888))
        s.sendall(b"GET")
        signal = s.recv(1024)
        print(signal)
        #image = pickle.loads(image)
        if not os.path.isfile(image_path):
            print("No such file")
        
        cap = cv2.VideoCapture(image_path)
        hasFrame, frame = cap.read()
        
        blob = cv2.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)
        net.setInput(blob)
        outs = net.forward(getOutputsNames(net))
        result = postprocess(frame, outs)
    
        s.sendall(pickle.dumps(np.array(result), protocol=2))
        
        s.close()

# if (args.image):
#     # Open the image file
#     if not os.path.isfile(args.image):
#         print("Input image file ", args.image, " doesn't exist")
#         sys.exit(1)
#     cap = cv2.VideoCapture(args.image)
#     outputFile = args.image[:-4]+'_yolo.jpg'

# i = 0
# while cv2.waitKey(1) < 0:
#     hasFrame, frame = cap.read()

#     i += 1 
#     if not hasFrame:
#         print("Done processing !!!")
#         print("Output file is stored as ", outputFile)
#         cv2.waitKey(3000)
#         break

#     orgFrame = frame.copy()

#     blob = cv2.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)
#     net.setInput(blob)
#     outs = net.forward(getOutputsNames(net))
#     postprocess(frame, outs, orgFrame)

#     #t, _ = net.getPerfProfile()
#     #label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())

#     if (args.image):

#         if(outputToFile):
#             cv2.imwrite(outputFile, frame.astype(np.uint8))

#         if(displayScreen):
#             cv2.imshow("Predicted", frame)

#     else:
#         print("Frame #{} processed.".format(i))

#         if(outputToFile):
#             out.write(frame)

#         if(displayScreen):
#             cv.imshow("frame", frame)
#             cv.waitKey(1)

########################################
