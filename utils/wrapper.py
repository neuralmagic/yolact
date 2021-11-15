import contextlib

import torch
from layers import Detect
from yolact import FastMaskIoUNet
deepsparse_available = None
with contextlib.suppress(ImportError):
    from deepsparse import compile_model
    deepsparse_available = True


class DeepsparseWrapper:
    def __init__(self, filepath, cfg):
        if deepsparse_available:
            self.engine = compile_model(filepath, batch_size=1)
        self.detect = Detect(cfg.num_classes, bkg_label=0, top_k=cfg.nms_top_k,
                             conf_thresh=cfg.nms_conf_thresh,
                             nms_thresh=cfg.nms_thresh)
        self.maskiou_net = FastMaskIoUNet()

    def __call__(self, inputs):
        batch = inputs.cpu().numpy()
        outs = self.engine.mapped_run([batch])
        keys = ['loc', 'conf', 'mask', 'priors', 'proto']
        outs = dict(zip(keys, map(torch.from_numpy ,outs.values())))
        return self.detect(outs, self)
