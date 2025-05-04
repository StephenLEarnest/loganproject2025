import numpy as np

class FourBarLinkageModel:
    def __init__(self):
        self.theta = 45.0
        self.omega = 0.0
        self.k = 0.1       # spring stiffness
        self.c = 0.05      # damping coefficient
        self.eq_angle = 0.0
        self.min_angle = -90.0
        self.max_angle = 90.0
        self.time = 0.0
        self.dt = 0.05
        self.t_history = []
        self.theta_history = []
        self.dashpot_force = 0.0  # store damping torque

    def set_limits(self, min_angle, max_angle):
        self.min_angle = min_angle
        self.max_angle = max_angle

    def reset_state(self, start_angle=45):
        self.theta = start_angle
        self.omega = 0.0
        self.time = 0.0
        self.t_history.clear()
        self.theta_history.clear()

    def step(self, dt=None):
        if dt is None:
            dt = self.dt

        torque_spring = -self.k * (self.theta - self.eq_angle)
        torque_damping = -self.c * self.omega
        self.dashpot_force = torque_damping

        alpha = torque_spring + torque_damping
        self.omega += alpha * dt
        self.theta += self.omega * dt
        self.time += dt

        if self.theta < self.min_angle:
            self.theta = self.min_angle
            self.omega = 0.0
        elif self.theta > self.max_angle:
            self.theta = self.max_angle
            self.omega = 0.0

        self.t_history.append(self.time)
        self.theta_history.append(self.theta)

        close = abs(self.omega) < 1e-2 and abs(self.theta - self.eq_angle) < 1
        return close

    def get_history(self):
        return self.t_history, self.theta_history

    def get_theta(self):
        return self.theta

    def get_dashpot_force(self):
        return self.dashpot_force
