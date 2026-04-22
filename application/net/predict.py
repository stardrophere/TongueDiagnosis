import queue
import tempfile
import threading
from contextlib import contextmanager

import torch
from PIL import Image
import numpy as np
from segment_anything import SamPredictor, sam_model_registry
from yolov5 import load

from application.net.model.resnet import ResNetPredictor


@contextmanager
def temporary_torch_load_kwargs(**default_kwargs):
    """
    Provide backwards-compatible torch.load defaults while loading legacy checkpoints.
    This is applied only during model initialization so we don't change runtime behavior elsewhere.
    """
    original_torch_load = torch.load

    def compatible_torch_load(*args, **kwargs):
        for key, value in default_kwargs.items():
            kwargs.setdefault(key, value)
        return original_torch_load(*args, **kwargs)

    torch.load = compatible_torch_load
    try:
        yield
    finally:
        torch.load = original_torch_load


class TonguePredictor:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,
                 yolo_path='application/net/weights/yolov5.pt',
                 sam_path='application/net/weights/sam_vit_b_01ec64.pth',
                 resnet_path=[
                     'application/net/weights/tongue_color.pth',
                     'application/net/weights/tongue_coat_color.pth',
                     'application/net/weights/thickness.pth',
                     'application/net/weights/rot_and_greasy.pth'
                 ]
                 ):
        if self._initialized:
            return
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        yolo_device = 0 if self.device.type == "cuda" else "cpu"
        with temporary_torch_load_kwargs(weights_only=False):
            self.yolo = load(yolo_path, device=yolo_device)
        self.sam = sam_model_registry["vit_b"](checkpoint=sam_path)
        self.sam.to(device=self.device)
        self.resnet = ResNetPredictor(resnet_path, device=self.device)
        print(f"TonguePredictor using device: {self.device}")
        self.queue = queue.Queue()
        self.worker_thread = None
        TonguePredictor._initialized = True

    def start_worker(self):
        """
        启动单例预测 worker。
        由于应用生命周期内可能多次获取 `TonguePredictor()` 实例，这里要保证线程只启动一次。
        """
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.worker_thread = threading.Thread(
            target=self.main,
            name="tongue-predict-worker",
            daemon=True,
        )
        self.worker_thread.start()

    def __predict(self, img, record_id, fun):
        predict_img = Image.open(img)
        self.yolo.eval()
        print("Tongue positioning")
        with torch.no_grad():
            pred = self.yolo(predict_img)
        if len(pred.xyxy[0]) < 1:
            fun(event_id=record_id,
                tongue_color=None,
                coating_color=None,
                tongue_thickness=None,
                rot_greasy=None,
                code=201)
            print("The picture is not legal and has no tongue.")
            return
        elif len(pred.xyxy[0]) > 1:
            fun(event_id=record_id,
                tongue_color=None,
                coating_color=None,
                tongue_thickness=None,
                rot_greasy=None,
                code=202)
            print("The picture is not legal. There are too many tongues.")
            return
        print("Tongue segmentation")
        with torch.no_grad():
            x1, y1, x2, y2 = (
                pred.xyxy[0][0, 0].item(), pred.xyxy[0][0, 1].item(), pred.xyxy[0][0, 2].item(),
                pred.xyxy[0][0, 3].item())
            predictor = SamPredictor(sam_model=self.sam)
            predictor.set_image(np.array(predict_img))
            masks, _, _ = predictor.predict(box=np.array([x1, y1, x2, y2]))
            original_img = np.array(predict_img)
            masks = np.transpose(masks, (1,2,0))
            pred = original_img * masks
            result = Image.fromarray(pred).crop((x1, y1, x2, y2)).convert("RGB")
            result = np.array(result)
        result = self.resnet.predict(result)
        print("Tongue analysis")
        predict_result = {
            "code": 0,
            'tongue_color': result[0],
            'tongue_coat_color': result[1],
            'thickness': result[2],
            'rot_and_greasy': result[3]
        }
        fun(event_id=record_id,
            tongue_color=result[0],
            coating_color=result[1],
            tongue_thickness=result[2],
            rot_greasy=result[3],
            code=1)
        return predict_result

    def predict(self, img, record_id, fun):
        try:
            img.seek(0)
            tmpfile = tempfile.SpooledTemporaryFile()
            content = img.read()
            tmpfile.write(content)
            tmpfile.seek(0)
            self.queue.put((tmpfile, record_id, fun))
            img.seek(0)
            return {"code": 0}
        except Exception as e:
            return {"code": 3}

    def main(self):
        """
        常驻预测 worker 主循环。
        旧实现通过 `queue.empty()` 忙等，会持续空转占用 CPU；现在改为阻塞式 `queue.get()`。
        """
        while True:
            img, record_id, fun = self.queue.get()
            try:
                self.__predict(img, record_id, fun)
            except Exception as e:
                print(e)
                fun(event_id=record_id,
                    tongue_color=None,
                    coating_color=None,
                    tongue_thickness=None,
                    rot_greasy=None,
                    code=203)
            finally:
                img.close()
