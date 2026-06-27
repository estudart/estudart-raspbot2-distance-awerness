import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Int32MultiArray
from geometry_msgs.msg import Twist

class UltrasonicProcessor(Node):
    def __init__(self):
        super().__init__("ultrasonic_processor")

        self.latest_distance = None
        self.get_logger().info('Starting processor...')

        self.subscription = self.create_subscription(
            Float32,
            "/ultrasonic",
            self.ultrasonic_callback,
            10,
        )

        self.moving_publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            10,
        )

        self.led_publisher_ = self.create_publisher(
            Int32MultiArray,
            '/rgblight',
            10,
        )

        self.timer = self.create_timer(
            0.1,  # 10 Hz
            self.control_loop,
        )

    def ultrasonic_callback(self, msg: Float32):
        self.get_logger().info(f'New message received: {msg.data}')
        self.latest_distance = msg.data
    
    def send_back_command(self):
        msg = Twist()
        msg.linear.x = -0.25
        msg.angular.z = 0.0

        self.moving_publisher_.publish(msg)

    def red_light(self):
        msg = Int32MultiArray()
        msg.data = [255, 0, 0]
        self.led_publisher_.publish(msg)

    def blue_light(self):
        msg = Int32MultiArray()
        msg.data = [0, 0, 255]
        self.led_publisher_.publish(msg)

    def control_loop(self):
        if self.latest_distance is None:
            return

        if self.latest_distance < 20:
            self.move_backward()
        elif self.latest_distance > 40:
            self.move_forward()
            
    def move_backward(self):
        self.red_light()
        self.send_back_command()
        self.get_logger().warning("MOVE BACKWARD")

    def move_forward(self):
        self.blue_light()
        self.get_logger().info("MOVING")


def main(args=None):
    rclpy.init(args=args)

    node = UltrasonicProcessor()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()