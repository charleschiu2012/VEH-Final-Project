import os
import cv2 
import numpy as np

from skimage import io, data

def cropping(image):
    #------ Get index of top white and bottom white ------#
    white_idx = np.where(image > 0)
    x_min, x_max = min(white_idx[0]), max(white_idx[0])
    y_min, y_max = min(white_idx[1]), max(white_idx[1])
    
    #-------------- Determine cropping area --------------#
    cropped_h, cropped_w = 60, 40

    return cv2.resize(image[x_min:x_max+1, y_min:y_max+1].astype(np.float32), (cropped_w, cropped_h)).astype(int)

def get_features(image):
    binary_img = (image > 125).astype(int)
    crop_img = cropping(binary_img)

    features = []
    height, width = crop_img.shape
    for x in range(0, height, 4):
        blocks = []
        for y in range(0, width, 4):
            # Statistic total number of white pixel in each block
            blocks.append(np.sum(crop_img[x:x+4, y:y+4]))
        features.append(blocks)
    
    return np.array(features)

def main(input_imgs):
    # files = os.listdir("./Results_recognition")
    # for file in files:
    #     os.remove(os.path.join("./Results_recognition", file))

    #------------ Get the feature of ground truth image ------------#
    root_gt_path = "./ground_truth"
    gt_filenames = os.listdir(root_gt_path)
    gt_features = []
    for idx, gt_filename in enumerate(gt_filenames):
        gt_img = cv2.imread(os.path.join(root_gt_path, gt_filename), cv2.IMREAD_GRAYSCALE)
        gt_feature = get_features(gt_img)
        gt_features.append(gt_feature)
        # print("Ground Truth number:", idx)
        # print(gt_feature)
        # print("\n" + "-"*40 + "\n")
    
    #-------------- Predict the number of input image -------------#
    pred_numbers = []
    for idx, input_img in enumerate(input_imgs):
        show_img = cv2.cvtColor(input_img, cv2.COLOR_GRAY2RGB)

        #-------- Get the feature of input image ---------#
        input_feature = get_features(input_img)
        print("The index of input image:", idx)
        print(input_feature)
        
        #-- Compute the difference between GT and input --#
        differences = []
        for gt_feature in gt_features:
            difference = np.linalg.norm(gt_feature - input_feature)
            differences.append(difference)

        pred_number = np.argmin(differences)
        pred_numbers.append(pred_number)
        print("Number:", pred_number)
        print("Difference:", differences[pred_number])
        print("Differences:", differences)

        #---------------- Visualize the recognition result ---------------#
        # cv2.putText(show_img, str(pred_number), (10, 50), 0, 1, (0, 255, 0))
        # cv2.imshow("Original image: %d" %(pred_number), show_img)
        # cv2.waitKey(0)

        #------------------ Save the recognition result ------------------#
        os.makedirs("./Results_recognition", exist_ok=True)
        output_path = os.path.join("./Results_recognition", "%d_prediction=%d.jpg" %(idx, pred_number))
        print("Saved image to '%s'" %(output_path))
        io.imsave(output_path, show_img)
        
        if idx != len(input_imgs)-1:
            print("\n" + "-"*40 + "\n")

    return pred_numbers
