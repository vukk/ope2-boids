#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function

__docs__ = """Boids.

Usage:
  boids.py run [--amount=<int>] [(--width=<int> --height=<int>)]
               [--numviews=<int>]
               [--separation=<float>] [--alignment=<float>] [--cohesion=<float>]
               [--boid-view-angle=<int>]
               [--boid-mass=<float>] [--boid-max-force=<float>]
               [--boid-normal-speed=<float>] [--boid-max-speed=<float>]
  boids.py preset (normal|wonky|wacky|racers|testing)
  boids.py --help
  boids.py --version

Options:
  --help                        Show this screen.
  --version                     Show version.
  -a --amount=<int>             Amount of boids
  -w --width=<int>              Window width
  -h --height=<int>             Window height
  -n --numviews=<int>           Number of views (gives n x n grid)
  -s --separation=<float>       Weight for the separation rule
  -l --alignment=<float>        Weight for the alignment rule
  -c --cohesion=<float>         Weight for the cohesion rule
  --boid-view-angle=<int>       Boid's view angle on both sides, 180 is full circle
  --boid-mass=<float>           Mass of the boid
  --boid-max-force=<float>      Force when applying rules
  --boid-normal-speed=<float>   Boids' target normal speed
  --boid-max-speed=<float>      Boids' target max speed

"""

__greeting__ = """
     **               **      **        
    /**              //      /**        
    /**       ******  **     /**  ******
    /******  **////**/**  ****** **//// 
    /**///**/**   /**/** **///**//***** 
    /**  /**/**   /**/**/**  /** /////**
    /****** //****** /**//****** ****** 
    /////    //////  //  ////// //////  
"""

from docopt.docopt import docopt

import sys, random, gc, itertools

from PySide import QtCore, QtGui

from vec2d import Vec2d
from neighborhood import Neighborhood
from boid import Boid
from gui_boid import GuiBoid

from rule_separation import RuleSeparation
from rule_cohesion import RuleCohesion
from rule_alignment import RuleAlignment

VERSION = '0x03'
UPDATE_RATE = 30 # msecs

class Engine(QtGui.QMainWindow):
    """ Engine for the boids simulation. """
    
    boid_count = 100        # static
    window_width = 700      # static
    window_height = 500     # static
    num_views = 1           # static
    
    def __init__(self):
        """ Initializes the Engine. """
        super(Engine, self).__init__()
        
        # CLI stuff
        self.initCli()
        
        # Init stuff
        self.boids = None # list for boids
        self.rules = None # list for rules
        
        self.view = None # QGraphicsView
        self.grid = None # Qt layout grid
        self.guiAreas = [] # list holding the gui area elements
        self.layoutEdit = None # Qt editing layout
        
        self.setWindowTitle('Boids ' + VERSION)
        
        # Seed pseudorandomnumgen with current time in seconds
        random.seed(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))
        
        # Init bunch of stuff
        self.initGraphicsScene()
        self.initOrReloadBoidsAndRules()
        self.initGraphicsViewGrid(Engine.num_views)
        
        # Show the main window on the screen
        self.show()
        
        # Initialize timer after bringing up the main window
        self.initTimer()
    
    
    def initCli(self):
        """ Apply CLI arguments and print the greeting. """
        # Get CLI options
        argv = QtCore.QCoreApplication.instance().arguments()
        argv = map( str , argv)
        del(argv[0])
        args = docopt(__docs__, argv=argv, version='Boids ' + VERSION)
        
        # CLI options
        if args['run']:
            self.cliArgsApply(args)
        
        # Presets
        if args['preset']:
            if args['wonky']:
                self.preset_wonky()
            if args['wacky']:
                self.preset_wacky()
            if args['racers']:
                self.preset_racers()
            if args['testing']:
                self.preset_testing()
            elif args['normal']:
                pass
        
        # Print the greeting
        print(__greeting__)
        print("                          Version " + VERSION + "\n")
    
    
    def initOrReloadBoidsAndRules(self):
        """ Initializes (or reloads) the boids and rules.
        
        Initializes the boids and rules by clearing the old boids and
        the graphicsscene.
        """
        self.scene.clear()
        del(self.boids)
        del(self.rules)
        self.boids = []
        self.rules = []
        self.initBoids(self.boid_count)
        self.initRules()
    
    
    def initTimer(self):
        """ Initializes the timer that calls engine loop. """
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(UPDATE_RATE) # msecs
    
    
    def initGraphicsViewGrid(self, numViews):
        """ Initializes the graphics views.
        
        numViews = 1 gives just one window
        numViews = 2 gives a 2x2 grid of views
        numViews = N gives a NxN grid of views
        
        :param numViews: the number of views to show at once
        :type numViews: int
        """
        grid = QtGui.QGridLayout()
        self.grid = grid
        
        # VIEWS
        
        combs = itertools.product(xrange(numViews), xrange(numViews))
        
        for c in combs:
            (x, y) = c
            
            view = QtGui.QGraphicsView(self.scene)
            view.setSceneRect(QtCore.QRectF(self.scene.sceneRect()))
            view.setRenderHint(QtGui.QPainter.Antialiasing)
            #view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
            view.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
            
            self.view = view # We only need the last one...
            grid.addWidget(view, x, y)
        
        # END VIEWS
        
        # BUTTONS & AREAS
        
        layoutEdit = QtGui.QHBoxLayout()
        # Add layout as the bottom of the grid, spanning whole width
        # layout, int row, int column, int rowSpan, int columnSpan
        grid.addLayout(layoutEdit, numViews, 0, 1, -1)
        self.layoutEdit = layoutEdit
        
        # The Reset button
        buttonReset = QtGui.QPushButton("Reset")
        buttonReset.clicked.connect(self.resetScene)
        layoutEdit.addWidget(buttonReset)
        
        # Create areas to edit the rule weights
        for rule in self.rules:
            label   = QtGui.QLabel(rule.name + ":")
            area    = QtGui.QLineEdit(str(rule.weight), parent=None)
            #                  double bottom, double top, int decimals
            area.setValidator( QtGui.QDoubleValidator(0.0, 1000.0, 4) )
            layoutEdit.addWidget(label)
            layoutEdit.addWidget(area)
            self.guiAreas.append( (area, rule) )
        
        # The Update button
        buttonUpdate = QtGui.QPushButton("Update")
        buttonUpdate.setDefault(True)
        buttonUpdate.clicked.connect(self.updateFromUserInput)
        layoutEdit.addWidget(buttonUpdate)
        
        # Some spacing between the buttons and areas
        layoutEdit.setSpacing(10)
        
        # END BUTTONS & AREAS
        
        # Set grid as the main layout
        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(grid)
        
        # No margins or spacing in the grid
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        # ... or in the main window
        mainWidget.setContentsMargins(0, 0, 0, 0)
        
        # Set widget containing grid as the central widget
        self.setCentralWidget(mainWidget)
        
        # Let Qt do its thing and then update the window size
        QtCore.QTimer.singleShot(0, self.updateWindowSize)
    
    
    def updateWindowSize(self):
        """ Set window so everything fits. """
        self.resize(self.sizeHint())
        # Fix width if necessary, some Qt weirdness
        if self.geometry().width() >= Engine.window_width * Engine.num_views + 20:
            self.resize(Engine.window_width * Engine.num_views + 4, self.geometry().height())
    
    
    #@QtCore.Slot()
    def resizeEvent(self, _we):
        """ Resize window event handler. """
        # Ignore for grid views
        if Engine.num_views != 1:
            return
        
        # Let Qt update and try to avoid any possible infinite recursion
        QtCore.QTimer.singleShot(0, self.resizeWindowActually)
    
    
    def resizeWindowActually(self):
        # Ignore for grid views
        if Engine.num_views != 1:
            return
        
        qrect = self.view.geometry()
        Engine.window_width = qrect.width()
        Engine.window_height = qrect.height()
        print("!!! Resizing window to", Engine.window_width, Engine.window_height, "!!!")
        self.scene.setSceneRect(0, 0, Engine.window_width, Engine.window_height)
        self.view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    
    
    @QtCore.Slot()
    def updateFromUserInput(self):
        """ Update rule weights (etc.) as given by the user. """
        # Chech that the areas have acceptable input
        for (area, rule) in self.guiAreas:
            if not area.hasAcceptableInput():
                return
        
        # Update all the rules
        for (area, rule) in self.guiAreas:
            type(rule).weight = float(area.text())
        
        # Print the new weights
        for rule in self.rules:
            print("Rule", rule.name, "now has weight\t", str(type(rule).weight))
    
    
    @QtCore.Slot()
    def resetScene(self):
        """ Reset the whole graphicsscene ie. clear it and add new boids. """
        print("!!! Resetting scene !!!")
        self.initOrReloadBoidsAndRules()
        gc.collect()
    
    
    def initGraphicsScene(self):
        """ Initialize the graphicsscene. """
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, Engine.window_width, Engine.window_height)
    
    
    def initRules(self):
        """ Initialize the rules. """
        self.rules.append(RuleSeparation())
        self.rules.append(RuleAlignment())
        self.rules.append(RuleCohesion())
        
        for rule in self.rules:
            print("Rule {0} has weight \t{1}".format(rule.name, type(rule).weight))
    
    
    def initBoids(self, amount):
        """ Initialize boids with random parameters.
        
        :param amount: number of boids to initialize
        :type amount: int
        """
        for i in xrange(amount):
            boid = GuiBoid()
            self.boids.append(boid)
            self.scene.addItem(boid)
    
    
    def loop(self): # modify, this is called with a timer?
        """ Main loop of the engine, moves things forward.
        
        Calculates the neighborhoods for each boid, then calculates the force to
        apply given by the rules and applies it.
        Lastly moves the boids forward on the screen.
        """
        
        w = Engine.window_width
        h = Engine.window_height
        
        # n²
        for b1 in self.boids:
            
            # Initialize neighborhood
            hood = Neighborhood(b1, Engine.window_width, Engine.window_height, rules=self.rules)
            
            # Loop all boids, add to neighborhood if distance is short enough
            for b2 in self.boids:
                if b2 == b1:
                    continue # skip adding the boid itself to its neighborhood
                
                dist_sqrd = b1.position.get_dist_sqrd_toroidal(
                    b2.position, Engine.window_width, Engine.window_height
                    )
                
                # OK to compare squared distances
                if dist_sqrd <= Neighborhood.max_distance:
                    # Check view angle condition
                    # angle is now between -180 and 180
                    vect_ab = (- b1.position + b2.position)
                    angle = b1.orientation.forward.get_angle_between(vect_ab)
                    if angle >= -b1.view_angle and angle <= b1.view_angle:
                        hood.add(b2)
            
            # Calculate weighted force
            force = Vec2d(0, 0)
            for rule in self.rules:
                w = Engine.window_width
                h = Engine.window_height
                # Normalize all vectors returned by rules and add them to total
                force += (type(rule).weight * rule.consult(b1, hood, w, h).normalized())
            
            # Apply weighted force
            b1.move(force, w, h)
        
        # endloop b1
        
        # Step all boids forward on the screen
        for b1 in self.boids:
            b1.step()
    
    
    def cliArgsApply(self, args):
        # Apply CLI options
        if args['--amount']:
            Engine.boid_count = int(args['--amount'])
        
        if args['--width'] and args['--height']:
            Engine.window_width = int(args['--width'])
            Engine.window_height = int(args['--height'])
        
        if args['--numviews']:
            Engine.num_views = int(args['--numviews'])
        
        if args['--separation']:
            RuleSeparation.weight = float(args['--separation'])
        if args['--alignment']:
            RuleAlignment.weight = float(args['--alignment'])
        if args['--cohesion']:
            RuleCohesion.weight = float(args['--cohesion'])
        
        if args['--boid-view-angle']:
            Boid.view_angle = int(args['--boid-view-angle'])
        if args['--boid-mass']:
            Boid.mass = float(args['--boid-mass'])
        if args['--boid-max-force']:
            Boid.max_force = float(args['--boid-max-force'])
        if args['--boid-normal-speed']:
            Boid.normal_speed = float(args['--boid-normal-speed'])
            Boid.cap_min_speed = Boid.normal_speed*Boid.CAP_MIN_SPEED_MULTIPLIER
        if args['--boid-max-speed']:
            Boid.max_speed = float(args['--boid-max-speed'])
            Boid.cap_max_speed = Boid.max_speed*Boid.CAP_MAX_SPEED_MULTIPLIER
    
    
    def preset_wonky(self):
        # Apply preset
        Engine.boid_count = 90
        Engine.window_width = 1000
        Engine.window_height = 800
        Engine.num_views = 1
        RuleSeparation.weight = 0.4
        RuleAlignment.weight = 0.4
        RuleCohesion.weight = 0.4
        Boid.view_angle = 180
        Boid.mass = 2.0
        Boid.max_force = 10.0
        Boid.normal_speed = 4.0
        Boid.max_speed = 12.0
    
    def preset_wacky(self):
        # Apply preset
        Engine.boid_count = 90
        Engine.window_width = 1000
        Engine.window_height = 800
        Engine.num_views = 1
        RuleSeparation.weight = 0.8
        RuleAlignment.weight = 0.4
        RuleCohesion.weight = 0.8
        Boid.view_angle = 120
        Boid.mass = 2.5
        Boid.max_force = 10.0
        Boid.normal_speed = 6.0
        Boid.max_speed = 10.0
    
    def preset_racers(self):
        # Apply preset
        Engine.boid_count = 90
        Engine.window_width = 1000
        Engine.window_height = 800
        Engine.num_views = 1
        RuleSeparation.weight = 1.6
        RuleAlignment.weight = 3.2
        RuleCohesion.weight = 3.2
        Boid.view_angle = 60
        Boid.mass = 5.0
        Boid.max_force = 10.0
        Boid.normal_speed = 7.2
        Boid.max_speed = 16.0
    
    def preset_testing(self):
        # Apply preset
        Engine.boid_count = 80
        Engine.window_width = 1000
        Engine.window_height = 800
        Engine.num_views = 1
        RuleSeparation.weight = 4.6
        RuleAlignment.weight = 2.0
        RuleCohesion.weight = 4.88
        Boid.view_angle = 90
        Boid.mass = 3.0
        Boid.max_force = 5.0
        Boid.normal_speed = 4.2
        Boid.max_speed = 4.0
    
    
    @staticmethod
    def randPosition():
        """ Return a random position.
        :rtype: Vec2d
        """
        x = random.randint(20, Engine.window_width - 20)
        y = random.randint(20, Engine.window_height - 20)
        
        return Vec2d(x, y)
    
    
    @staticmethod
    def randForce():
        """ Returns a random force.
        :rtype: Vec2d
        """
        x = random.uniform(-GuiBoid.normal_speed, GuiBoid.normal_speed)
        y = random.uniform(-GuiBoid.normal_speed, GuiBoid.normal_speed)
        
        # For divbyzero in vector calcs
        if x == 0 and y == 0:
            return randForce()
        
        return Vec2d(x, y)

# EOF

