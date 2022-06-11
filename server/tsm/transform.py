import numpy as np
import torchvision
from torchvision.transforms import InterpolationMode


class Stack(object):
    def __init__(self, roll=False):
        self.roll = roll

    def __call__(self, img_group):
        if self.roll:
            return np.concatenate([np.array(x)[:, :, ::-1] for x in img_group], axis=2)
        else:
            return np.concatenate(img_group, axis=2)


class GroupScale(object):
    def __init__(self, size, interpolation=InterpolationMode.BILINEAR):
        self.worker = torchvision.transforms.Resize(size, interpolation)

    def __call__(self, img_group):
        return [self.worker(img) for img in img_group]


class GroupCenterCrop(object):
    def __init__(self, size):
        self.worker = torchvision.transforms.CenterCrop(size)

    def __call__(self, img_group):
        return [self.worker(img) for img in img_group]


class GroupNormalize(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, tensor):
        rep_mean = self.mean * (tensor.size()[0] // len(self.mean))
        rep_std = self.std * (tensor.size()[0] // len(self.std))
        for t, m, s in zip(tensor, rep_mean, rep_std):
            t.sub_(m).div_(s)
        return tensor
