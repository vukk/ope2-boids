#!/usr/bin/env python
#-*- coding:utf-8 -*-

from inspect import isfunction

from vec2d import Vec2d
from gui_boid import GuiBoid

class Neighborhood(object):
    """ Represents a neighborhood for a boid. """
    
    RADIUS_MULTIPLIER = 5.0 # const
    max_distance = (GuiBoid.DIAMETER * RADIUS_MULTIPLIER)**2 # static, squared!
    
    @property
    def avg_velocity(self):
        self._calculate()
        return self._avg_velocity
    
    @property
    def avg_position(self):
        self._calculate()
        return self._avg_position
    
    
    def __init__(self, whose, window_width, window_height, rules, neighboring_boids = None, avg_velocity = None, avg_position = None):
        """
        :param whose: the boid whose neighborhood this is
        :type whose: Boid
        :param neighboring_boids: list of neighboring boids (default: [])
        :type neighboring_boids: list of Boid
        :param avg_velocity: precalculated average velocity
        :type avg_velocity: Vec2d
        :param avg_position: precalculated average position
        :type avg_position: Vec2d
        """
        
        if neighboring_boids == None:
            neighboring_boids = []
        
        # if avg_velocity and position are not given, then we have to calc
        # them when accessed, this is done by setting self.updated = True
        if avg_velocity == None or avg_position == None:
            self.updated = True
        
        self.whose = whose
        self.window_width = window_width
        self.window_height = window_height
        self.boids = neighboring_boids
        self._avg_velocity = avg_velocity
        self._avg_position = avg_position
        
        self._lambdas = {}
        self._lambda_state = {}
        
        # Gather all functions to be injected
        if rules != None:
            for rule in rules:
                try:
                    # If the function exists
                    if isfunction(rule.inject):
                        # Try to access the attribute that tells as if the
                        # method is abstract
                        rule.inject.__isabstractmethod__
                except AttributeError:
                    # The method is not abstract, add to lambdas
                    self._lambdas[rule.name] = rule.inject
                    self._lambda_state[rule.name] = rule.inject_default_state()
                except NameError:
                    # The method does not exist
                    pass
    
    
    def get_inject_state(self, name):
        self._calculate()
        return self._lambda_state[name]
    
    
    def add(self, boid):
        """ Add a boid to the neighborhood.
        
        :param boid: boid to add
        :type boid: Boid
        """
        self.boids.append(boid)
        self.updated = True
    
    
    def _calculate(self):
        """ Calculate the averages, position and velocity, and inject fios. """
        if self.updated == False:
            return # No need to calculate
        
        sum_vel = Vec2d()
        sum_pos = Vec2d()
        
        # Loop all boids in neighborhood
        for b in self.boids:
            sum_vel += b.velocity
            sum_pos += b.position
            # Call all injected functions
            for name, fun in self._lambdas.items():
                self._lambda_state[name] = fun(
                    self._lambda_state[name],
                    self.whose, b, self.window_width, self.window_height
                )
        
        length = len(self.boids)
        if length != 0:
            self._avg_velocity = sum_vel/length
            self._avg_position = sum_pos/length
            self._avg_position = Vec2d(
                self._avg_position.x % self.window_width,
                self._avg_position.y % self.window_height
                )
        else:
            self._avg_velocity = Vec2d(0, 0)
            self._avg_position = Vec2d(0, 0)
        
        self.updated = False

# EOF

