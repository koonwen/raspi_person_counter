import cv2
# cap = cv2.VideoCapture(1)
# cap.set(3,1280)
# cap.set(4,720)
# cap.set(10,70)

thresh = 0.5 # Threshold to detect object
classNames= ["person"]

# Uncomment to import list of coconames
# classFile = './Object_Detection_files/coco.names'
# with open(classFile,'rt') as f:
#     classNames = f.read().rstrip('\n').split('\n')

def detect(image):
    """image: image file -> <numpy.ndarray> integer classIds """
    img = cv2.imread(image)

    configPath = './Object_Detection_files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = './Object_Detection_files/frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(640,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    classIds, confs, bbox = net.detect(img, confThreshold= thresh)
    # Uncomment to visualize object detection with bounding box
    # for classId, confidence, box in zip(classIds.flatten(),confs.flatten(),bbox):
    #     cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
    #     cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    #     cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    #
    #     cv2.imshow("Output",img)
    #     cv2.waitKey(0)
    return classIds

def people_count(classId_arr):
    cnt = 0
    for object in classId_arr.flatten():
        if object == 1:
            cnt += 1
    print('{} person'.format(cnt))

#For testing
# if __name__ == '__main__':
#     img1_object_arr = detect("1024px-usmc-120205-m-av740-004copy.jpg")