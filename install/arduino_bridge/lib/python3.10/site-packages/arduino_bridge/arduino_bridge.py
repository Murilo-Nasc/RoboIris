#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import time

class ArduinoBridge(Node):
    def __init__(self):
        super().__init__('arduino_bridge')
        try:
            self.serial = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=115200,
                timeout=1,
                write_timeout=1
            )
            time.sleep(2)  # Espera inicialização
            self.get_logger().info("Conexão serial estabelecida!")
        except Exception as e:
            self.get_logger().error(f"Falha ao conectar: {str(e)}")
            raise
        
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        self.latest_cmd = Twist()
    
    def cmd_vel_callback(self, msg):
        self.latest_cmd = msg
        try:
            cmd_str = f"{msg.linear.x:.2f},{msg.angular.z:.2f}\n"
            self.serial.write(cmd_str.encode('utf-8'))
            self.get_logger().debug(f"Enviado: {cmd_str.strip()}")
        except Exception as e:
            self.get_logger().warn(f"Erro ao enviar: {str(e)}")

def main():
    rclpy.init()
    node = ArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Interrupção por usuário")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()