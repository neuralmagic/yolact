import contextlib

import torch

with contextlib.suppress(ModuleNotFoundError):
    from deepsparse import compile_model
    from deepsparse.utils import generate_random_inputs

from layers import Detect
from yolact import FastMaskIoUNet


class DeepsparseWrapper:
    def __init__(self, filepath, cfg, num_cores=None, warm_up_iterations=0,
                 batch_size=1):
        self.engine = compile_model(filepath, batch_size=batch_size,
                                    num_cores=num_cores)
        self.detect = Detect(cfg.num_classes, bkg_label=0, top_k=cfg.nms_top_k,
                             conf_thresh=cfg.nms_conf_thresh,
                             nms_thresh=cfg.nms_thresh)
        self.maskiou_net = FastMaskIoUNet()
        if warm_up_iterations:
            print(f"Running {warm_up_iterations} warm up iterations")
        for _ in range(warm_up_iterations):
            inputs = generate_random_inputs(filepath, batch_size)
            self(inputs)

    def __call__(self, inputs):
        if torch.is_tensor(inputs):
            inputs = inputs.cpu().numpy()
        batch = inputs
        if not isinstance(inputs, list):
            batch = [inputs]
        outs = self.engine.mapped_run(batch)
        keys = ['loc', 'conf', 'mask', 'priors', 'proto']
        outs = dict(zip(keys, map(torch.from_numpy, outs.values())))
        return self.detect(outs, self)
