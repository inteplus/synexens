#!/usr/bin/python3

import synexens as s
from mt import cv, np


def main():
    with s.Device() as device:
        print(device.info)
        device.resolution = s.SYRESOLUTION_640_480
        device.stream_on(s.SYSTREAMTYPE_DEPTHIR)
        while True:
            frame = device.get_last_frame_data()
            if frame is None:
                continue
            depth_image = frame[s.SYFRAMETYPE_DEPTH]
            color_image = device.get_depth_color(depth_image)
            cv.imshow("color", color_image)
            depth_image = (depth_image // 32).astype(np.uint8)
            cv.imshow("depth", depth_image)
            ir_image = frame[s.SYFRAMETYPE_IR]
            ir_image = (ir_image // 8).astype(np.uint8)
            cv.imshow("infrared", ir_image)
            k = cv.waitKey(1)
            if k == 27 or k == ord("q"):
                break


if __name__ == "__main__":
    main()
