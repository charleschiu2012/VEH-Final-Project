import os
import cv2
import numpy as np

from skimage import io, data

def stretch(image):
    #-------- Image stretching function --------#
    maximum = float(image.max())
    minimum = float(image.min())
    diff = maximum - minimum

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            image[i, j] = 255 / diff * image[i, j] - (255 * minimum) / diff
    
    return image

def binarization(image):
    #-------- Binary processing function --------#
    
    # After binarization, return ret, binary_img (threshold, binary image)
    # maximum = float(image.max())
    # minimum = float(image.min())
    # diff = maximum - minimum
    # threshold = maximum - (diff / 2.5)
    # ret, binary_img = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
    ret, binary_img = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)

    return binary_img

def find_vertex(contour):
    #-------- Find the vertex of rectangle (contour) --------#
    y, x = [], []
    for cnt in contour:
        y.append(cnt[0][0])
        x.append(cnt[0][1])

    return [min(y), min(x), max(y), max(x)]

def locate_CM(image, resize_img):
    #-------- Located the calling machine --------#
    try:
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except Exception:
        _, contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Collect the area and the height-width ratio of contours
    blocks = []
    for cnt in contours:
        # Located the top left and bottom right points of contour to compute the area and height-width ratio
        rectangle = find_vertex(cnt)
        area = (rectangle[2] - rectangle[0]) * (rectangle[3] - rectangle[1]) # Area
        ratio = (rectangle[2] - rectangle[0]) / (rectangle[3] - rectangle[1]) # Height-width ratio
        blocks.append([rectangle, area, ratio])

    # Find the first three rectangles with the largest area
    blocks = sorted(blocks, key=lambda b: b[1])[-3:]

    # Use background color to find the block most like a calling machine
    maxweight, maxindex = 0, -1
    for idx in range(len(blocks)):
        block = resize_img[blocks[idx][0][1]:blocks[idx][0][3], blocks[idx][0][0]:blocks[idx][0][2]]

        # Transform the color space from RGB to HSV
        block_hsv = cv2.cvtColor(block, cv2.COLOR_BGR2HSV)

        # Black background
        lower = np.array([0, 0, 0])
        upper = np.array([50, 50, 50])

        # white background
        # lower = np.array([225, 225, 225])
        # upper = np.array([255, 255, 255])

        # Create mask based on the threshold of black background
        mask = cv2.inRange(block_hsv, lower, upper)

        # Statistic weight value
        weight = np.sum(mask) / 255
        
        # Find the largest weight value of blocks
        if weight > maxweight:
            maxindex = idx
            maxweight = weight
    print("Rectangle: ", blocks[maxindex][0])
    return blocks[maxindex][0]

def find_CM(image):
    # Resize the image to image width is equal to 400
    resize_w = 400
    resize_h = int(resize_w * image.shape[0] / image.shape[1])
    resize_img = cv2.resize(image, (resize_w, resize_h), interpolation=cv2.INTER_CUBIC)

    # Transform the color space from BGR to gray
    gray_img = cv2.cvtColor(resize_img, cv2.COLOR_BGR2GRAY)

    # Stretch the gray image
    stretched_img = stretch(gray_img)
    cv2.imwrite("./images/img_gray.jpg", stretched_img)
    # cv2.imshow("Stretched image", stretched_img)

    # r = 16
    # h = w = r * 2 + 1
    # kernel = np.zeros((h, w), dtype=np.uint8)
    # cv2.circle(kernel, (r, r), r, 1, -1)
     
    # openingimg = cv2.morphologyEx(stretched_img, cv2.MORPH_OPEN, kernel)
    # strtimg = cv2.absdiff(stretched_img,openingimg)
    
    # Image binarization
    binary_img = binarization(stretched_img)
    # cv2.imshow("Binary image", binary_img)

    # Canny edge detection 
    canny = cv2.Canny(binary_img, binary_img.shape[0], binary_img.shape[1])
    # cv2.imshow("Canny Edge Detection", canny)
    canny[:10] = 0
    canny[:, :10] = 0
    canny[-10:] = 0
    canny[:, -10:] = 0
    # cv2.imshow("Canny Edge Detection (after denoise)", canny)
    cv2.imwrite("./images/img_canny.jpg", canny)
    
    # Eliminate the small area, keep the big area, to locate the calling machine
    # Excute closing operation
    kernel = np.ones((5, 20), np.uint8)
    closingimg = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("Closing Opeartion image", closingimg)
    # cv2.waitKey(0)
    cv2.imwrite("./images/img_closing.jpg", closingimg)

    rectangle = locate_CM(closingimg, resize_img)

    return resize_img, rectangle

def segmentation(resize_img, rectangle):
    # Compute the height and width of rectangle
    rectangle[2] = rectangle[2] - rectangle[0]
    rectangle[3] = rectangle[3] - rectangle[1]
    rectangle_copy = tuple(rectangle.copy())
    rectangle = [0, 0, 0, 0]
    
    # Create mask based on fg model and bg model (1, 13*5)
    mask = np.zeros(resize_img.shape[:2], np.uint8)
    fgModel = np.zeros((1, 13*5), np.float64)
    bgModel = np.zeros((1, 13*5), np.float64)
    
    # Image segmentation
    cv2.grabCut(resize_img, mask, rectangle_copy, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    seg_img = resize_img * mask2[:, :, np.newaxis]

    return seg_img

def smooth_and_binarization(CM_img):
    # Transform the color space from BGR to gray
    gray_img = cv2.cvtColor(CM_img, cv2.COLOR_BGR2GRAY)

    # Using average filter to denoise
    kernel = np.ones((3, 3), np.float32) / 9
    gray_img = cv2.filter2D(gray_img, -1, kernel)
    # cv2.imshow("Gray image after average filter", gray_img)

    # Binarization
    maximum = float(gray_img.max())
    minimum = float(gray_img.min())
    diff = maximum - minimum
    threshold = maximum - (diff / 2.5)
    ret, binary_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY)

    return binary_img

def locate_number(start, arg, black, white, width, black_max, white_max, ratio):
    end = start + 1
    for position in range(start+1, width-1):
        if (black[position] if arg else white[position]) > ((1-ratio) * black_max if arg else (1-ratio) * white_max):
            end = position
            break

    return end


def main(filename):
    # files = os.listdir("./Results_segmentation")
    # for file in files:
    #     os.remove(os.path.join("./Results_segmentation", file))
    #
    # filepath = "F:/Tello_img/New folder/2020-01-08_16-25-04.jpg"
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    # image = cv2.imread(os.path.join("./images", filename + ".jpg"), cv2.IMREAD_COLOR)
    # resize_img = cv2.resize(image, (400, 300))
    # cv2.imshow("Original image", resize_img)

    # Transform color space from RGB to HSV color to do histogram equalization
    # hsv_img = cv2.cvtColor(resize_img, cv2.COLOR_RGB2HSV)
    # hsv_img[:, :, 2] = cv2.equalizeHist(hsv_img[:, :, 2])
    # eq_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
    # cv2.imshow("Histogram Equalization", eq_img)

    # Resize the image and find rectangle of calling machine
    resize_img, rectangle = find_CM(image)
    cv2.rectangle(resize_img, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 255, 0), 2)
    # cv2.imshow("Bounding box of number", resize_img)

    # Segment the calling machine and background
    seg_img = segmentation(resize_img, rectangle)
    # cv2.imshow("Segment image into fg and bg", seg_img)

    # Binarize the segmentation result
    binary_img = smooth_and_binarization(seg_img)
    # cv2.imshow("Binary segmentation result", binary_img)
    cv2.imwrite("./images/img_binary.jpg", binary_img)

    # Analyze the color of background and numbers, and segment the each numbers#
    # 紀錄黑白像素總和
    white, black = [], []
    white_max, black_max = 0, 0
    height, width = binary_img.shape # height = 263, width = 400

    # 計算每一列黑白像素總和
    for i in range(width):
        line_white = np.sum(binary_img[:, i] == 255)
        line_black = np.sum(binary_img[:, i] == 0)

        white_max = max(white_max, line_white)
        black_max = max(black_max, line_black)
        
        white.append(line_white)
        black.append(line_black)
    
    # arg ... True表示黑底白字，False表示為白底黑字
    arg = black_max >= white_max

    ratio = 0.01
    position = 1
    start, end = 1, 2
    segmentation_numbers = []
    while position < width-2:
        position += 1
        # Analyze the calling machine is (white bg and black number) or (black bg and white number)
        if (white[position] if arg else black[position]) > (ratio * white_max if arg else ratio * black_max):
            start = position
            end = locate_number(start, arg, black, white, width, black_max, white_max, ratio)
            position = end

            if end - start > 5:
                #--------------- Visualize the segmentation result ---------------#
                print("Start:", start, ", End:", end)
                number = binary_img[:, start-2:end+2] # Crop the area of number
                resize_number = cv2.resize(number, (40, 300))
                # cv2.imshow('Number between (%d, %d)' %(start, end), resize_number)
                # cv2.waitKey(0)

                #------------------ Save the segmentation result -----------------#
                os.makedirs("./Results_segmentation", exist_ok=True)
                output_path = os.path.join("./Results_segmentation", "%s_position=%d.jpg" % ("crop", position))
                print("Saved image to '%s'\n" %(output_path))
                io.imsave(output_path, resize_number)
                segmentation_numbers.append(resize_number)

    cv2.destroyAllWindows()

    return segmentation_numbers