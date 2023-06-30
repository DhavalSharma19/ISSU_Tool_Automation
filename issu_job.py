import re
import os
import sys
import argparse
import time

from pyats import aetest
from pyats.easypy import run
from pyats.datastructures.logic import Or
from pyats import topology

from pprint import pprint
from time import sleep 

def main():
      ''' Main function '''

      # Find the location of the script in relation to the job file, used for autoeasy execution
      testscript = '/ws/dhavshar-bgl/script/dhaval_script/issu_verification_test_script.py'
    
      run(testscript = testscript)
