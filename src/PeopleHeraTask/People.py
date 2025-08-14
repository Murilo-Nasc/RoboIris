#!/usr/bin/env python3

import rclpy
import rclpy.duration
from rclpy.node import Node

import rclpy.time
from tf2_ros import TransformException, Buffer, TransformListener
from geometry_msgs.msg import PoseStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient

import time
import math

from methods.vision import Vision
from methods.speech import Speech


class People(Node):
    def __init__(self):
        super().__init__('people_node')

        self.vision = Vision()
        self.speech = Speech()

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self, spin_thread=True)

        self.host_name = None
        self.host_found = False

        self.joint_trajectory_client = ActionClient(
            self, FollowJointTrajectory, '/camera_controller/follow_joint_trajectory')

        self.last_cam_position = 0.0
        self.get_logger().info("Apagando arquivos")
        self.vision.erase()

        self.task()

    def send_joint_trajectory(self, joint_angle, tilt_angle):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ["pan_to_camera_joint", "tilt_to_connection_rod"]

        point = JointTrajectoryPoint()
        point.positions = [float(joint_angle), float(tilt_angle)]
        point.time_from_start = rclpy.duration.Duration(seconds=1.0).to_msg()

        goal_msg.trajectory.points.append(point)

        self.joint_trajectory_client.wait_for_server()
        self.joint_trajectory_client.send_goal_async(goal_msg)
        self.get_logger().info("Sent goal")

    def compute_rotation_angle(self, transform):
        x = transform.transform.translation.x
        y = transform.transform.translation.y
        z = transform.transform.translation.z

        pan = math.atan2(z, x)
        tilt = math.atan2(y, x)

        return tilt, pan

    def calculate_angle(self, reference, name):
        t_camera = self.tf_buffer.lookup_transform(reference, name, rclpy.time.Time())
        angle, pan = self.compute_rotation_angle(t_camera)
        self.get_logger().info(f"Rotating to angle: {angle:.2f} rad")
        return angle, pan

    def check_for_host(self):
        angles = [0.0, -0.5, 0.5]

        for angle in angles:
            self.send_joint_trajectory(angle, 0.0)
            time.sleep(2)

            recog = self.vision.recog()
            if recog.success and recog.names:
                self.host_name = recog.names[0]
                self.get_logger().info(f"Host detectado: {self.host_name}")
                self.speech.speak(f"Hello {self.host_name}, I will follow you.")
                return True

        self.speech.speak("I couldn't find anyone to follow.")
        return False

    def count_people(self):
        detected = self.vision.check()
        if detected.success:
            crowd_size = len(detected.names)
            self.get_logger().info(f"{crowd_size} pessoas detectadas.")
            self.speech.speak(f"There are {crowd_size} people here.")
            return crowd_size
        return 0

    def find_host(self):
        if not self.host_name:
            self.get_logger().warn("Host não foi definido ainda.")
            return False

        try:
            angle, pan = self.calculate_angle("camera_link", self.host_name)
            self.send_joint_trajectory(angle, pan)
            self.speech.speak(f"I found {self.host_name}")
            return True
        except Exception as e:
            self.get_logger().warn(f"Não foi possível localizar o host: {e}")
            self.speech.speak("I cannot find the host.")
            return False

    def task(self):
        self.get_logger().info("Iniciando identificação do host...")
        found = self.check_for_host()

        if not found:
            return

        self.count_people()
        time.sleep(1)

        self.get_logger().info("Buscando o host novamente para centralizar...")
        self.find_host()


def main(args=None):
    rclpy.init(args=args)
    node = People()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
