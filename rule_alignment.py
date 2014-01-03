#!/usr/bin/env python
#-*- coding:utf-8 -*-

from rule import Rule
from vec2d import Vec2d

class RuleAlignment(Rule):
    """ Calculates the alignment as per Reynolds. """
    
    weight = 0.38       # static, (note: w/o normalization, 0.3 works)
    name = "Alignment"  # static
    
    def consult(self, boid, neighborhood, window_width, window_height):
        if neighborhood.avg_velocity.length != 0:
            return (neighborhood.avg_velocity - boid.velocity)
        else:
            return Vec2d(0, 0)

# EOF

