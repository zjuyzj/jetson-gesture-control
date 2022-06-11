import torch
import torchvision
import numpy as np

from tsm.transform import Stack, GroupCenterCrop, GroupNormalize, GroupScale


class ToTorchFormatTensor(object):
    def __init__(self, div=True):
        self.div = div

    def __call__(self, pic):
        if isinstance(pic, np.ndarray):  # numpy array
            img = torch.from_numpy(pic).permute(2, 0, 1).contiguous()
        else:  # PIL Image
            img = torch.ByteTensor(
                torch.ByteStorage.from_buffer(pic.tobytes()))
            img = img.view(pic.size[1], pic.size[0], len(pic.mode))
            img = img.transpose(0, 1).transpose(0, 2).contiguous()
        return img.float().div(255) if self.div else img.float()


class Utility:
    @staticmethod
    def refine_output(index, history):
        max_history_len = 20  # max history buffer
        # mask out illegal action
        if index in [7, 8, 21, 22, 3]:
            index = history[-1]
        # use only single no action class
        if index == 0:
            index = 2
        # history smoothing
        if index != history[-1]:
            # and history[-2] == history[-3]):
            if not (history[-1] == history[-2]):
                index = history[-1]
        history.append(index)
        history = history[-max_history_len:]
        return history[-1], history

    @staticmethod
    def get_transform():
        cropping = torchvision.transforms.Compose([
            GroupScale(256),
            GroupCenterCrop(224),
        ])
        transform = torchvision.transforms.Compose([
            cropping,
            Stack(roll=False),
            ToTorchFormatTensor(div=True),
            GroupNormalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        return transform
