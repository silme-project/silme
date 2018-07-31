#!/usr/bin/python
# Original Author : https://github.com/benediktkr at /ncpoc
# Modified by CVSC

import os
import hashlib

def generate_nodeid():
    return hashlib.sha256(os.urandom(256/8)).hexdigest()
