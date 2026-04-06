#!/usr/bin/env python3
"""
slam.py - Entry point for the SLAM map visualiser.

Usage (from inside the slam/ directory):
    source ../env/bin/activate
    python3 slam.py

The SLAM visualiser connects to the LIDAR source, builds an occupancy map
using BreezySLAM, and displays it in a windowed custom UI.

Settings are in settings.py. Edit that file to change map size, scan quality,
or display options.

Requirements
------------
    pyrplidar   - installed by setup_environment.sh (Sensor Mini-Project)
    breezyslam  - installed by install_slam.sh (this studio)
    matplotlib  - required for the custom UI
"""

import sys
import os

# Ensure this directory is on the module search path so that relative imports
# (e.g. 'import settings') work correctly when the file is run as a script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_custom import run

if __name__ == '__main__':
    run()
