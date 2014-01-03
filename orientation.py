#!/usr/bin/env python
#-*- coding:utf-8 -*-

from vec2d import Vec2d
from collections import namedtuple

Orientation2d = namedtuple('Orientation2d', 'forward side')

class Orientation(Orientation2d):
    """ An orientation as per Reynolds. """
    
    @staticmethod
    def new():
        return Orientation(Vec2d(0, 1), Vec2d(1, 0))
    
    def __init__(self, forward_or_pair = (Vec2d(0, 1), Vec2d(1, 0)), side = None):
        """ Init Orientation """
        if side == None:
            super(type(self), self).__init__(forward_or_pair[0], forward_or_pair[1])
        else:
            super(type(self), self).__init__(forward_or_pair, side)

# EOF

