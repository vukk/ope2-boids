#!/usr/bin/env python
#-*- coding:utf-8 -*-

from rule import Rule
from vec2d import Vec2d

class RuleCohesion(Rule):
    """ Calculates the cohesion as per Reynolds. """
    
    weight = 0.6        # static, (note: w/o normalization, 0.01 works)
    name = "Cohesion"   # static
    
    def consult(self, boid, neighborhood, window_width, window_height):
        if neighborhood.avg_position.length != 0:
            return neighborhood.avg_position.toroidal_sub(
                boid.position, window_width, window_height
                )
        else:
            return Vec2d(0, 0)

# EOF

