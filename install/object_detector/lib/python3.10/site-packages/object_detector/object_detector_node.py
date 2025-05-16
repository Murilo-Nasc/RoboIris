#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import torch
import numpy as np
from pathlib import Path

class ObjectDetectorNode(Node):
    def __init__(self):
        super().__init__('object_detector_node')
        self.bridge = CvBridge()

        # Carrega o modelo YOLOv5 (você pode usar 'yolov5s.pt', 'yolov5m.pt', etc.)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.conf = 0.5  # confiança mínima

        # Subscrição ao tópico de imagem
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Inferência
        results = self.model(frame)

        # Anotação da imagem
        annotated = results.render()[0]

        # Mostra o resultado
        cv2.imshow("YOLO Detection", annotated)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

