import os
import numpy as np
import pandas as pd
import sys
import shutil

sim_log = [ i for i in open('data.csv').readlines() ]
if len(sim_log) > 3:
    shutil.copyfile('data.csv', 'data_csv_log.csv')