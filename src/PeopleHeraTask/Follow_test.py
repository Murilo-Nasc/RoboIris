#!/usr/bin/env python3

import rclpy
import rclpy.duration
from rclpy.node import Node

from tf2_ros import Buffer, TransformListener
from trajectory_msgs.msg import JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from hera_msgs.action import Follow
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from methods.vision import Vision
from methods.speech import Speech
from methods.navigation import BasicNavigator as Navigation

class Follow(Node):
    def __init__(self):
        super().__init__('follow_node')

        self.vision = Vision()
        self.navigation = Navigation()
        self.speech = Speech()

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self, spin_thread=True)

        self.cb_group = ReentrantCallbackGroup()
        self.follow_client = ActionClient(self, Follow, 'follow_action',
                                        callback_group=self.cb_group)
        
        self.pan_client = ActionClient(self, FollowJointTrajectory,
                                '/camera_controller/follow_joint_trajectory',
                                callback_group=self.cb_group)

        self.last_distance = None
        self.constant_distance_start_time = None
        self.constant_distance_threshold = 0.1  # tolerância de variação em metros
        self.constant_duration_threshold = 10.0  # segundos
        
        self._follow_goal_handle = None

        self.joint_trajectory_client = ActionClient(
            self, FollowJointTrajectory, '/camera_controller/follow_joint_trajectory')

        self.last_cam_position = 0.0
        self.get_logger().info("Apagando arquivos")
        self.vision.erase()

        self.task()

    def waitForNavComplete(self, pose):
        self.navigation.goToPose(pose)
        
        while not self.navigation.isNavComplete():
            if self.navigation.isNavComplete():
                break
    
    def send_pan(self, angle, tilt):
        if not self.pan_client.server_is_ready():
            self.get_logger().warn('Controlador de pan indisponível.')
            return

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = ["pan_to_camera_joint", "tilt_to_connection_rod"]
        pt = JointTrajectoryPoint()
        pt.positions = [float(angle), float(tilt)]
        pt.time_from_start = rclpy.duration.Duration(seconds=1.0).to_msg()
        goal.trajectory.points = [pt]
        self.pan_client.send_goal_async(goal)

    def task(self):
        self.get_logger().info("Starting task")
        self.speech.speak("Starting Navigation and Follow Me task!") 

        #Salvando posição inicial
        #initial_tf = self.tf_buffer.lookup_transform("map", "base_link", rclpy.time.Time())
        #initial_pose = self.navigation.createPoseStampedMsg(initial_tf)
        #self.initial_pose = initial_pose 

        #Esperando porta de entrada abrir
        #time.sleep(2)        
        #self.speech.speak('Waiting to open the door')
        #time.sleep(2)
        #self.navigation.waitForDoor()
    
        #Criando transformadas
        #waypoint1 = self.navigation.get_transform_with_retry("map", "waypoint1")
        #waypoint2 = self.navigation.get_transform_with_retry("map", "waypoint2")

        #Atualizar from rclpy.action import ActionCliento objetivo de navegação
        #waypoint1pose = self.navigation.createPoseStampedMsg(waypoint1)
        #waypoint2pose = self.navigation.createPoseStampedMsg(waypoint2)

        #Indo para Waypoint 1
        #self.speech.speak("Going to Waypoint 1")
        #time.sleep(2)
        #self.waitForNavComplete(waypoint1pose)
        #self.speech.speak("On Waypoint 1")
        #time.sleep(4)

        #Indo para Waypoint 2
        #self.speech.speak("Going to Waypoint 2")
        #time.sleep(2)
        #self.waitForNavComplete(waypoint2pose)
        #self.speech.speak("On Waypoint 2")
        #time.sleep(4)

        ##Preparando para Follow
        #self.follow_client.wait_for_server()
        #self.send_pan(0.0, 0.15)

        goal_msg = Follow.Goal()
        goal_msg.follow_tf = "person_follow"

        time.sleep(3)

        self.vision.save_last_photo("operator")
        
        self.info('Sending follow goal...')
        send_goal_future = self.follow_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        
        rclpy.spin_until_future_complete(self, send_goal_future)
        
        self._follow_goal_handle = send_goal_future.result()
        if not self._follow_goal_handle.accepted:
            self.error('Follow goal rejected')
            return

        self.info('Follow goal accepted. Waiting for the operator to stop and confirm...')
        self.speech.speak("You can start walking now, i will follow, please walk very slowly.")
        get_result_future = self._follow_goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, get_result_future)
        
        result = get_result_future.result().result
        status = get_result_future.result().status

        if status == rclpy.action.GoalStatus.STATUS_CANCELED:
            self.info(f'Follow action was canceled as requested.')
            time.sleep(4)

            #Voltando para Waypoint 2
            #self.speech.speak("Going back to Waypoint 2")
            #time.sleep(2)
            #self.waitForNavComplete(waypoint2pose)
            #self.speech.speak("On Waypoint 2")
            #time.sleep(4)

            #Voltando para posição inicial
            #self.speech.speak("Returning to the initial position")
            #time.sleep(2)
            #self.waitForNavComplete(self.initial_pose)
            #self.speech.speak("Arrived at the initial position")

        else:
            self.warn(f'Follow action finished with an unexpected status: {status}')

def main(args=None):
    rclpy.init(args=args)
    node = Follow()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
