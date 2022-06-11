import json
import pickle

import torch
from torch2trt import TRTModule
import trt_pose.coco
from trt_pose.parse_objects import ParseObjects

from pose.utility import Utility


class Classifier:
    def __init__(self, result_callback, height=224, width=224,
                 cmap_thres=0.12, link_thres=0.15,
                 file_trt_model='pose/model/trt_model.pth',
                 file_skeleton='pose/model/skeleton.json',
                 file_svm_model='pose/model/svm_model.sav',
                 file_gesture='pose/model/gesture.json'):
        # Set basic attribute
        self.height = height
        self.width = width
        self.result_callback = result_callback
        # Load optimized TensorRT model for TRTPose
        self.nn = TRTModule()
        self.nn.load_state_dict(torch.load(file_trt_model))
        # Load topology infomation for hand
        skeleton = json.load(open(file_skeleton, 'r'))
        self.topology = trt_pose.coco.coco_category_to_topology(skeleton)
        self.n_joint = len(skeleton['keypoints'])
        self.n_link = len(skeleton['skeleton'])
        # Load SVM model for hand pose classfication
        self.clf = pickle.load(open(file_svm_model, 'rb'))
        # Load hand gesture dictionary
        gesture_dict = json.load(open(file_gesture, 'r'))
        self.gesture_type = gesture_dict["type"]
        # Initialize image data buffer
        self.data = torch.zeros((1, 3, self.height, self.width)).cuda()
        # Initialize utility and object parser
        self.util = Utility(self.topology, self.n_joint)
        self.object_parser = ParseObjects(
            self.topology, cmap_threshold=cmap_thres, link_threshold=link_thres)

    def classify_callback(self, cam_dict):
        image = cam_dict['new']
        data = self.util.process_image(image)
        cmap, paf = self.nn(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
        counts, objects, peaks = self.object_parser(cmap, paf)
        joints = self.util.infer_joint(image, counts, objects, peaks)
        joints_dist = self.util.get_joint_distance(joints)
        svc_input = [joints_dist, [0]*self.n_joint*self.n_joint]
        svc_result = self.clf.predict(svc_input)
        gesture = self.gesture_type[svc_result[0]-1]
        self.result_callback(gesture)
