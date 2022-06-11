import math
import torch
import cv2
import PIL.Image
import torchvision.transforms as transforms


class Utility:
    def __init__(self, topology, num_parts):
        self.topology = topology
        self.num_parts = num_parts
        self.device = torch.device('cuda')

    def process_image(self, image):
        mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
        std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self.device)
        image.sub_(mean[:, None, None]).div_(std[:, None, None])
        return image[None, ...]

    def infer_joint(self, image, counts, objects, peaks):
        joints_t = []
        height = image.shape[0]
        width = image.shape[1]
        K = self.topology.shape[0]
        count = int(counts[0])
        for i in range(count):
            obj = objects[0][i]
            C = obj.shape[0]
            for j in range(C):
                k = int(obj[j])
                picked_peaks = peaks[0][j][k]
                joints_t.append(
                    [round(float(picked_peaks[1]) * width), round(float(picked_peaks[0]) * height)])
        joints_pt = joints_t[:self.num_parts]
        rest_of_joints_t = joints_t[self.num_parts:]
        # when it does not predict a particular joint in the same association it will try to find it in a different association
        for i in range(len(rest_of_joints_t)):
            l = i % self.num_parts
            if joints_pt[l] == [0, 0]:
                joints_pt[l] = rest_of_joints_t[i]
        # if nothing is predicted
        if count == 0:
            joints_pt = [[0, 0]]*self.num_parts
        return joints_pt

    def get_joint_distance(self, joints):
        joints_features = []
        for i in joints:
            for j in joints:
                dist_between_i_j = math.sqrt((i[0]-j[0])**2+(i[1]-j[1])**2)
                joints_features.append(dist_between_i_j)
        return joints_features
