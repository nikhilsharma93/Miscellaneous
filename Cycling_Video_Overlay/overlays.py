import cv2
import numpy as np


class BarOverlay(object):
    def __init__(
        self,
        ht,
        wd,
        x1,
        y1,
        name,
        min_val,
        max_val,
        border_clr,
        bar_clr,
        border_wd_percent,
        bg_clr=(0, 0, 0),
        opacity=0.75,
    ):
        self.ht = ht
        self.wd = wd
        self.x1 = x1
        self.y1 = y1
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.bar_clr = bar_clr
        self.border_clr = border_clr
        self.border_wd = int(wd * border_wd_percent)
        self.bg_x11 = self.x1 - self.border_wd - 20
        self.bg_x12 = self.x1 + self.wd + self.border_wd + 220
        self.bg_y11 = self.y1 - self.border_wd - 50
        self.bg_y12 = self.y1 + self.ht + self.border_wd + 30
        self.bg = np.zeros(
            (self.bg_y12 - self.bg_y11, self.bg_x12 - self.bg_x11, 3), dtype="uint8"
        )
        self.opacity = opacity
        for idx, clr in enumerate(bg_clr):
            self.bg[..., idx].fill(clr)

    def add_border(self, img):
        img = cv2.copyMakeBorder(
            img,
            self.border_wd,
            self.border_wd,
            self.border_wd,
            self.border_wd,
            cv2.BORDER_CONSTANT,
            value=self.border_clr,
        )
        return img

    def add_overlay(self, base_img, current_val):
        # Add slight background
        base_img[
            self.bg_y11 : self.bg_y12, self.bg_x11 : self.bg_x12
        ] = cv2.addWeighted(
            base_img[self.bg_y11 : self.bg_y12, self.bg_x11 : self.bg_x12],
            self.opacity,
            self.bg,
            1 - self.opacity,
            0,
        )
        # Fill with current_val
        fill_wd = int(current_val / self.max_val * self.wd)
        base_img = cv2.rectangle(
            base_img,
            (self.x1, self.y1),
            (self.x1 + fill_wd, self.y1 + self.ht),
            self.bar_clr,
            -1,
        )
        # Add border
        y11 = self.y1 - self.border_wd
        y12 = self.y1 + self.ht + self.border_wd
        x11 = self.x1 - self.border_wd
        x12 = self.x1 + self.wd + self.border_wd
        base_img[y11:y12, x11:x12] = self.add_border(
            base_img[self.y1 : self.y1 + self.ht, self.x1 : self.x1 + self.wd]
        )
        # Add name
        base_img = cv2.putText(
            base_img,
            self.name,
            (x12 + 50, y11),
            cv2.FONT_HERSHEY_DUPLEX,
            1.3,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        # Add value
        base_img = cv2.putText(
            base_img,
            str(int(current_val)),
            (x12 + 25, y12 - 5),
            cv2.FONT_HERSHEY_DUPLEX,
            3,
            (255, 255, 255),
            3,
            cv2.LINE_AA,
        )
        return base_img


class GaugeOverlay(object):
    def __init__(
        self,
        scale,
        x1,
        y1,
        name,
        min_val,
        max_val,
        dial_file_id,
        display_dtype,
        gauge_clr,
        bg_clr=(0, 0, 0),
        opacity=0.9,
    ):
        self.scale = scale
        self.x1 = x1
        self.y1 = y1
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.min_angle = -130
        self.max_angle = 75
        self.display_dtype = display_dtype
        """
        self.bg_x11 = self.x1 - self.border_wd - 20
        self.bg_x12 = self.x1 + self.wd + self.border_wd + 220
        self.bg_y11 = self.y1 - self.border_wd - 50
        self.bg_y12 = self.y1 + self.ht + self.border_wd + 30
        self.bg = np.zeros(
            (self.bg_y12 - self.bg_y11, self.bg_x12 - self.bg_x11, 3), dtype="uint8"
        )
        self.opacity = opacity
        for idx, clr in enumerate(bg_clr):
            self.bg[..., idx].fill(clr)
        """
        self.dial_img = cv2.imread(dial_file_id, -1)
        self.dial_img_ht, self.dial_img_wd = self.dial_img.shape[:2]
        dial_new_size_ht = int(self.dial_img_ht * scale)
        dial_new_size_wd = int(self.dial_img_wd * scale)
        self.dial_img = cv2.resize(self.dial_img, (dial_new_size_wd, dial_new_size_ht))
        # self.base_cx = int(580 * scale)
        # self.base_cy = int(780 * scale)
        self.base_cx = int(197 * scale)
        self.base_cy = int(261 * scale)
        self.dial_img_ht, self.dial_img_wd = self.dial_img.shape[:2]
        # Find shift required
        self.x11_dial = self.x1 - self.base_cx
        self.x12_dial = self.x11_dial + self.dial_img_wd
        self.y11_dial = self.y1 - self.base_cy
        self.y12_dial = self.y11_dial + self.dial_img_ht
        self.gauge = cv2.imread(gauge_file_id, -1)
        self.gauge_img_ht, self.gauge_img_wd = self.gauge.shape[:2]
        self.gauge = cv2.resize(
            self.gauge, (int(self.gauge_img_wd * 1.5), int(self.gauge_img_ht * 1.5))
        )
        # Apply gauge color
        # gauge_yxs = np.where(self.gauge[..., 0] < 255)
        # for i in range(3):
        #     self.gauge[gauge_yxs[0], gauge_yxs[1], i] = gauge_clr[i]
        self.gauge_img_ht, self.gauge_img_wd = self.gauge.shape[:2]
        self.x11_gauge = self.x1 - 240
        self.x12_gauge = self.x11_gauge + self.gauge_img_wd
        self.y11_gauge = self.y1 - 240
        self.y12_gauge = self.y11_gauge + self.gauge_img_ht

    def rotate_image(self, img, angle, pivot):
        def _rotate_image(image, angle):
            image_center = tuple(np.array(image.shape[1::-1]) / 2)
            rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
            result = cv2.warpAffine(
                image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR
            )
            return result

        padX = [img.shape[1] - pivot[0], pivot[0]]
        padY = [img.shape[0] - pivot[1], pivot[1]]
        imgP = np.pad(img, [padY, padX, [0, 0]], "constant", constant_values=0)
        imgR = _rotate_image(imgP, angle)
        return imgR[padY[0] : -padY[1], padX[0] : -padX[1]]

    def add_overlay(self, base_img, current_val):
        # Add gauge
        self.gauge_mask = np.where(self.gauge[..., -1] < 127, 0, 255).astype("uint8")
        base_img[self.y11_gauge : self.y12_gauge, self.x11_gauge : self.x12_gauge][
            self.gauge_mask > 0
        ] = self.gauge[..., :3][self.gauge_mask > 0]
        # Find angle
        current_angle = self.min_angle + (current_val / self.max_val) * (
            self.max_angle - self.min_angle
        )
        rot_img = self.rotate_image(
            self.dial_img, -current_angle, (self.base_cx, self.base_cy)
        )
        rot_img_mask = np.where(rot_img[..., -1] < 127, 0, 255).astype("uint8")
        # Find area to insert
        base_img[self.y11_dial : self.y12_dial, self.x11_dial : self.x12_dial][
            rot_img_mask > 0
        ] = rot_img[..., :3][rot_img_mask > 0]
        # Add name
        base_img = cv2.putText(
            base_img,
            self.name,
            (self.x1 - self.dial_img_wd // 2, self.y1 + self.dial_img_ht // 2),
            cv2.FONT_HERSHEY_DUPLEX,
            2,
            (255, 255, 255),
            3,
            cv2.LINE_AA,
        )
        # Add value
        if self.display_dtype == "float":
            display_val = str(round(current_val, 1))
        else:
            display_val = str(int(current_val))
        base_img = cv2.putText(
            base_img,
            display_val,
            (self.x1 + self.dial_img_wd // 5 - 100, self.y1 + 150),
            cv2.FONT_HERSHEY_DUPLEX,
            3,
            (255, 255, 255),
            3,
            cv2.LINE_AA,
        )
        return base_img
