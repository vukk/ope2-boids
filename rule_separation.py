#!/usr/bin/env python
#-*- coding:utf-8 -*-

from rule import Rule
from vec2d import Vec2d

class RuleSeparation(Rule):
    """ Calculates the separation as per Reynolds. """
    
    weight = 0.55       # static, (note: w/o normalization 1.0 works)
    name = "Separation" # static
    
    def consult(self, boid, neighborhood, window_width, window_height):
        return self.get_inject_state(neighborhood)
    
    
    @staticmethod
    def inject(state, boid, one_neighbor, window_width, window_height):
        """ Calculate repulsion, wrapped in a toroid.
        
        :param boid: the boid
        :type boid: Boid
        :param one_boid: one of the boids in the neighborhood
        :type one_boid: Boid
        :param w: window width
        :type w: int
        :param h: window height
        :type h: int
        """
        repulsion = state
        diff = boid.position.toroidal_sub(one_neighbor.position, window_width, window_height)
        if diff.length != 0:
            repulsion += diff.normalized() * (1/diff.length)
        return repulsion
    
    
    @staticmethod
    def inject_default_state():
        return Vec2d(0,0)

# EOF

