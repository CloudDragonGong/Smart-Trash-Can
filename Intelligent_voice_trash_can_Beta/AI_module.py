import random
import numpy as np
import onnxruntime as ort
from PIL import Image
import cv2

# 必要的图像处理函数-填充、缩放、尺寸调整
def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, r, (dw, dh)


class AIModule:
    def __init__(self, load_path='best.onnx', cuda=True):
        self.img = None  # img
        self.session = None  # model
        self.providers = None  # devices
        self.load_path = load_path
        self.cuda = False
        self.names = ['cipian', 'eluanshi', 'tudou', 'bailuobo', 'huluobo',
                      'yilaguan', 'bottle', 'battery', 'medician']
        self.colors = {name: [random.randint(0, 255) for _ in range(3)] for i, name in enumerate(self.names)}

    def LoadModel(self):
        print("模型开始加载")
        self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.cuda else ['CPUExecutionProvider']
        # session是模型
        self.session = ort.InferenceSession(self.load_path, providers=self.providers)
        # 标签对应颜色
        print("模型加载结束")

    def img_process(self, img):
        self.img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = self.img.copy()
        image, ratio, dwdh = letterbox(image, auto=False)
        image = image.transpose((2, 0, 1))
        image = np.expand_dims(image, 0)
        image = np.ascontiguousarray(image)

        im = image.astype(np.float32)
        im /= 255
        return im, image, ratio, dwdh

    def get_preds(self, im):
        outname = [i.name for i in self.session.get_outputs()]

        inname = [i.name for i in self.session.get_inputs()]

        inp = {inname[0]: im}
        # ONNX inference
        outputs = self.session.run(outname, inp)[0]
        print(outputs)

        return outputs

    def Module(self, frame):
        im, image, ratio, dwdh = self.img_process(frame)
        outputs = self.get_preds(im)
        print(f'the length is {len(outputs)}')
        if len(outputs) == 0:
            return None
        return self.gar_sort(outputs, ratio, dwdh)

    def gar_sort(self, outputs, ratio, dwdh):
        ori_images = [self.img.copy()]

        for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
            image = ori_images[int(batch_id)]
            box = np.array([x0, y0, x1, y1])  # 框的位置坐标
            box -= np.array(dwdh * 2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            cls_id = int(cls_id)  # 类别id
            print(cls_id)
            score = round(float(score), 3)
            name = self.names[cls_id]  # id对应的类别
            print(name)
            color = self.colors[name]
            name += ' ' + str(score)  # 类别+概率score
            # 画框
            cv2.rectangle(image, box[:2], box[2:], color, 2)
            cv2.putText(image, name, (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [225, 255, 255], thickness=2)

        cv2.imwrite('img/image_anchor_frame.jpg', ori_images[0])
        pred_id = int(outputs[0][5]) + 1
        print(self.names[pred_id - 1])
        if pred_id == 1 or pred_id == 2:
            flag = 0
        elif pred_id >= 3 and pred_id <= 5:
            flag = 1
        elif pred_id >= 6 and pred_id <= 7:
            flag = 2
        elif pred_id >= 8 and pred_id <= 9:
            flag = 3
        else:
            flag = None
        print("分类完成")
        return flag, len(outputs)

if __name__ == '__main__':
    module = AIModule(load_path=r'E:\repository\model\best.onnx',cuda=False)
    module.LoadModel()
    img_path = r'E:\repository\Smart-Trash-Can\img\WIN_20230901_17_21_19_Pro.jpg'
    img = cv2.imread(img_path)
    result = module.Module(img)

    # 显示图像
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(result)