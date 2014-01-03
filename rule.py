#!/usr/bin/env python
#-*- coding:utf-8 -*-

import abc

class Rule(object):
    """ A rule abstract class. """
    
    __metaclass__ = abc.ABCMeta
    
    weight = 1.0                # static
    name = "Default rule name"  # static
    
    
    @abc.abstractmethod
    def consult(self, boid, neighborhood, window_width, window_height):
        """ Rule consulting method. """
    
    
    @staticmethod
    @abc.abstractmethod
    def inject(state, boid, neighbor, width, height):
        """ Inject your own calculations to Neighborhood's calculating loop.
        
        This is because we do not wish to loop many times, so we can
        inject functions to the one calculation loop.
        Return value is the new state.
        """
    
    
    @staticmethod
    @abc.abstractmethod
    def inject_default_state():
        """ Should return the default state for the injection. """
    
    
    def get_inject_state(self, neighborhood):
        return neighborhood.get_inject_state(self.name)

# EOF

