#!/usr/bin/env python
#-*- coding:utf-8 -*-

import random
from PySide import QtCore, QtGui

from boid import Boid

class GuiBoid(QtGui.QGraphicsItem, Boid):
    """ Wrap Boid into something that handles graphics too. """
    
    RADIUS = 4.0                # const, boid radius on screen
    DIAMETER = 2*RADIUS         # const
    PENWIDTH = 1.0              # const, penwidth for Qt
    SPEED_INDICATOR_MULT = 4.5  # const, how much to multiply the speed indicator on screen
    
    def __init__(self, position=None, velocity=None, orientation=None):
        """ Initialize the GuiBoid graphical representation of the Boid. """
        QtGui.QGraphicsItem.__init__(self)
        Boid.__init__(self, position, velocity, orientation)
        self.color = self.randomColor()
        self.updateOnGui()
    
    
    def randomColor(self):
        """ Creates and returns a random QColor.
        :rtype: QColor
        """
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return QtGui.QColor(r, g, b)
    
    
    def updateOnGui(self):
        """ Updates the boid on the GUI. """
        self.setRotation(self.orientation.forward.get_angle() + 90)
        self.setPos(self.position.x, self.position.y)
    
    
    def boundingRect(self):
        """ Specifies the bounding rectangle for Qt. """
        # Choose bounding rectangle from
        # max( size of boid, size of line showing direction )
        total = max(GuiBoid.DIAMETER + GuiBoid.PENWIDTH,
                    (GuiBoid.max_speed * GuiBoid.SPEED_INDICATOR_MULT) + GuiBoid.PENWIDTH )
        return QtCore.QRectF(-total, -total, total, total);
    
    
    def paint(self, painter, option, widget):
        """ Specifies the painter method for Qt. """
        # Circle
        painter.setBrush(self.color)
        painter.drawEllipse(-GuiBoid.RADIUS, -GuiBoid.RADIUS,
                            GuiBoid.DIAMETER, GuiBoid.DIAMETER)
        
        # Line showing direction
        painter.setBrush(QtCore.Qt.black)
        painter.drawLine(0, 0, 0, -self.velocity.length * GuiBoid.SPEED_INDICATOR_MULT)
    
    
    def step(self):
        """ Wraps Boid.step() so the GUI is updated after it. """
        Boid.step(self)
        self.updateOnGui()

# EOF

