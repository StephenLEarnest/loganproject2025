from PyQt5.QtCore import QTimer
from FourBarLinkage_Model import FourBarLinkageModel
from PyQt5.QtGui import QPen, QTransform, QBrush
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem
import matplotlib.pyplot as plt
import math


class FourBarLinkage_Controller:
    def __init__(self, view):
        self.view = view
        self.model = FourBarLinkageModel()

        # Setup scene with tighter frame and zoom
        self.scene = self.view.gv_Main.scene()
        if self.scene is None:
            self.scene = QGraphicsScene(-100, -100, 200, 200)
            self.view.gv_Main.setScene(self.scene)
        else:
            self.scene.setSceneRect(-100, -100, 200, 200)

        self.view.gv_Main.resetTransform()
        self.view.gv_Main.scale(2.5, 2.5)  # Zoom in for clarity

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

        # Connect GUI input angle change to simulation start
        self.view.nud_InputAngle.valueChanged.connect(self.start_simulation)

        # Geometry
        self.ground_length = 100  # distance between fixed pivots A and B

        # Initialize linkage graphics
        self.init_linkage_graphics()

    def init_linkage_graphics(self):
        pen_black = QPen(Qt.black, 3)
        pen_blue = QPen(Qt.blue, 4)
        pen_red = QPen(Qt.red, 3, Qt.DashLine)
        pen_green = QPen(Qt.darkGreen, 3, Qt.DashDotLine)

        # Ground link (fixed)
        self.ground_link = self.scene.addLine(0, 0, self.ground_length, 0, pen_black)

        # Input, coupler, output links
        self.input_link = self.scene.addLine(0, 0, 0, 0, pen_blue)
        self.coupler_link = self.scene.addLine(0, 0, 0, 0, pen_black)
        self.output_link = self.scene.addLine(0, 0, 0, 0, pen_black)

        # Spring and dashpot (shown as lines)
        self.spring = self.scene.addLine(0, 0, 0, 0, pen_red)
        self.dashpot = self.scene.addLine(0, 0, 0, 0, pen_green)

        # Mark fixed pivots with small black circles
        for x in [0, self.ground_length]:
            pivot = QGraphicsEllipseItem(x - 3, -3, 6, 6)
            pivot.setBrush(QBrush(Qt.black))
            self.scene.addItem(pivot)

    def start_simulation(self):
        min_angle = self.view.nud_InputAngle.minimum()
        max_angle = self.view.nud_InputAngle.maximum()
        start_angle = self.view.nud_InputAngle.value()

        self.model.set_limits(min_angle, max_angle)
        self.model.reset_state(start_angle)
        self.timer.start(50)

    def update_simulation(self):
        done = self.model.step()
        theta_deg = self.model.get_theta()
        theta_rad = math.radians(theta_deg)

        # Link lengths from GUI
        L1 = self.view.nud_Link1Length.value() or 50  # input link
        L2 = 100  # coupler link (fixed)
        L3 = self.view.nud_Link3Length.value() or 50  # output link
        L4 = self.ground_length  # fixed base

        # Ground joints
        A = (0, 0)
        B = (L4, 0)

        # Point C: input link endpoint
        Cx = A[0] + L1 * math.cos(theta_rad)
        Cy = A[1] + L1 * math.sin(theta_rad)
        C = (Cx, Cy)

        # Vector from C to B
        dx = B[0] - Cx
        dy = B[1] - Cy
        d = math.hypot(dx, dy)
        if d > (L2 + L3):
            d = L2 + L3

        # Angle to B and solve triangle CBD
        a = L2
        b = L3
        c = d
        if d == 0:
            return
        try:
            angle_CBD = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
        except ValueError:
            angle_CBD = 0

        phi = math.atan2(dy, dx) + angle_CBD
        Dx = B[0] - L3 * math.cos(phi)
        Dy = B[1] - L3 * math.sin(phi)
        D = (Dx, Dy)

        # Update linkage graphics
        self.input_link.setLine(A[0], A[1], C[0], C[1])
        self.output_link.setLine(B[0], B[1], D[0], D[1])
        self.coupler_link.setLine(C[0], C[1], D[0], D[1])

        # Spring and dashpot center points
        mid_coupler = ((C[0] + D[0]) / 2, (C[1] + D[1]) / 2)
        mid_output = ((B[0] + D[0]) / 2, (B[1] + D[1]) / 2)
        self.spring.setLine(mid_coupler[0], mid_coupler[1], mid_output[0], mid_output[1])
        self.dashpot.setLine(mid_coupler[0], mid_coupler[1], mid_output[0], mid_output[1])

        # Update label
        self.view.lbl_OutputAngle_Val.setText(f"{theta_deg:.2f}°")

        if done:
            self.timer.stop()
            self.show_plot()

    def show_plot(self):
        t, theta = self.model.get_history()
        plt.plot(t, theta)
        plt.xlabel("Time (s)")
        plt.ylabel("Input Angle (deg)")
        plt.title("Input Angle vs. Time")
        plt.grid(True)
        plt.show()
