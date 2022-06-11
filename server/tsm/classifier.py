import json
import numpy as np

from PIL import Image

import torch
import tvm
import tvm.relay
import tvm.contrib.graph_runtime as graph_runtime

from tsm.utility import Utility


class Classifier:
    def __init__(self, result_callback,
                 file_tvm_lib=f'tsm/model/tvm_lib.tar',
                 file_tvm_param=f'tsm/model/tvm_param.param',
                 file_tvm_graph=f'tsm/model/tvm_graph.json',
                 file_gesture='tsm/model/gesture.json'):
        self.device = tvm.gpu()
        self.tvm_graph = graph_runtime.create(
            open(file_tvm_graph, 'rt').read(),
            tvm.module.load(file_tvm_lib),
            self.device
        )
        tvm_params = tvm.relay.load_param_dict(
            bytearray(open(file_tvm_param, 'rb').read()))
        for name, value in tvm_params.items():
            self.tvm_graph.set_input(name, value)
        self.t_buffer = (tvm.nd.empty((1, 3, 56, 56), ctx=self.device),
                         tvm.nd.empty((1, 4, 28, 28), ctx=self.device),
                         tvm.nd.empty((1, 4, 28, 28), ctx=self.device),
                         tvm.nd.empty((1, 8, 14, 14), ctx=self.device),
                         tvm.nd.empty((1, 8, 14, 14), ctx=self.device),
                         tvm.nd.empty((1, 8, 14, 14), ctx=self.device),
                         tvm.nd.empty((1, 12, 14, 14), ctx=self.device),
                         tvm.nd.empty((1, 12, 14, 14), ctx=self.device),
                         tvm.nd.empty((1, 20, 7, 7), ctx=self.device),
                         tvm.nd.empty((1, 20, 7, 7), ctx=self.device))
        self.history = [2]
        self.history_logit = []
        self.transform = Utility.get_transform()
        gesture_dict = json.load(open(file_gesture, 'r'))
        self.gesture_type = gesture_dict['type']
        self.result_callback = result_callback

    def classify_callback(self, cam_dict):
        image = cam_dict['new']
        image = self.transform([Image.fromarray(image).convert('RGB')])
        input_var = torch.autograd.Variable(
            image.view(1, 3, image.size(1), image.size(2)))
        img_nd = tvm.nd.array(input_var.detach().numpy(), ctx=self.device)
        inputs = (img_nd,) + self.t_buffer
        for index, value in enumerate(inputs):
            self.tvm_graph.set_input(index, value)
        self.tvm_graph.run()
        outputs = tuple(self.tvm_graph.get_output(index)
                        for index in range(len(inputs)))
        feat, self.t_buffer = outputs[0], outputs[1:]
        self.history_logit.append(feat.asnumpy())
        self.history_logit = self.history_logit[-12:]
        avg_logit = sum(self.history_logit)
        index = np.argmax(avg_logit, axis=1)[0]
        index, self.history = Utility.refine_output(index, self.history)
        gesture = self.gesture_type[index]
        self.result_callback(gesture)
