#!/usr/bin/env python
#-*- coding:utf-8 -*-

import engine
from orientation import Orientation

class Boid(object):
    """ An object representing one boid. """
    
    CAP_MIN_SPEED_MULTIPLIER = 0.01 # const
    CAP_MAX_SPEED_MULTIPLIER = 1.5  # const
    
    mass = 10.5             # static
    max_force = 5.0         # static
    normal_speed = 1.8      # static
    max_speed = 3.4         # static
    cap_min_speed = normal_speed*CAP_MIN_SPEED_MULTIPLIER   # static
    cap_max_speed = max_speed*CAP_MAX_SPEED_MULTIPLIER      # static
    view_angle = 120 # static, on both sides, 180 = full circle
    
    def __init__(self, position = None, velocity = None, orientation = None):
        """ Initializes the boid.
        
        :param position: Position, random if not given
        :type position: Vec2d
        :param velocity: Velocity, random if not given
        :type velocity: Vec2d
        :param orientation: Orientation, random if not given
        :type orientation: Orientation
        """
        
        if position == None:
            position = engine.Engine.randPosition()
        
        if velocity == None:
            velocity = engine.Engine.randForce()
        
        if orientation == None:
            orientation = Orientation.new()
        
        self.position = position
        self.velocity = velocity
        self.orientation = orientation
    
    
    def move(self, force, window_width, window_height):
        """ Applies forces and realigns the boid.
        
        NOTE: Does not actually MOVE the boid
              ie. apply velocity to current position,
              use step() for that.
        
        :param force: Position, random if not given
        :type force: Vec2d
        :param window_width: Width of the window
        :type window_width: int
        :param window_height: Height of the window
        :type window_height: int
        """
        self.apply_force(force)
        self.realign()
        self.wrap_around(window_width, window_height)
    
    
    def realign(self):
        """ Realigns the boid.
        
        In Reynolds:
        new_forward = normalize (velocity)
        approximate_up = normalize (approximate_up)      // if needed
        new_side = cross (new_forward, approximate_up)
        new_up = cross (new_forward, new_side)
        """
        if self.velocity.length != 0:
            new_forward = self.velocity.normalized()
            new_side = new_forward.perpendicular()
            self.orientation = Orientation(new_forward, new_side)
    
    
    def step(self):
        """ Moves the boid, applies current velocity to the position. """
        self.position = self.position + self.velocity
    
    
    def wrap_around(self, width, height):
        """ Wraps the boid in a toroid.
        
        :param width: Width of the window
        :type width: int
        :param height: Height of the window
        :type height: int
        """
        if self.position.x < 0 or self.position.x > width:
            self.position.x = self.position.x % width
        if self.position.y < 0 or self.position.y > height:
            self.position.y = self.position.y % height
    
    
    def apply_force(self, force):
        """ Applies given force to the boid.
        
        In Reynolds:
        steering_force = truncate (steering_direction, max_force)
        acceleration = steering_force / mass
        velocity = truncate (velocity + acceleration, max_speed)
        
        :param force: force to apply
        :type force: Vec2d
        :returns: the new velocity
        :rtype: Vec2d
        """
        
        # Cap applied force
        if force.length >= Boid.max_force:
            force.length = Boid.max_force
        
        # Calc and apply acceleration
        acceleration = force / Boid.mass
        self.velocity += acceleration
        
        # Keep velocity in limits
        if self.velocity.length >= Boid.max_speed:
            self.velocity *= 0.98 # smoothly decrease speed
        
        if self.velocity.length <= Boid.normal_speed:
            self.velocity *= 1.02 # smoothly increase speed
        
        if self.velocity.length >= Boid.cap_max_speed:
            self.velocity.length = Boid.cap_max_speed
        
        if Boid.cap_min_speed >= self.velocity.length:
            self.velocity.length = Boid.cap_min_speed
        
        return self.velocity


# EOF

