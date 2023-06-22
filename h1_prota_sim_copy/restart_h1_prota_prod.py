# run simulation of a protein.
import os
import numpy as np
import pandas as pd
import sys
import shutil
import simtk.openmm as mm
import simtk.openmm.app as app
import simtk.unit as unit

from openabc.forcefields.parsers import MOFFParser, MRGdsDNAParser
from openabc.forcefields import MOFFMRGModel

num_steps=400000000
output_interval=20000
dt=5

out_dcd='output.dcd'


# set simulation platform
platform_name = 'CUDA'
properties={'CudaPrecision':'mixed'}

print('Successful import')

system_xml = 'H1_Prota_system.xml'
with open(system_xml, 'r') as f:
    system = mm.XmlSerializer.deserialize(f.read())

top = app.PDBFile('start.pdb').getTopology()

# initiate simulation
# setup integrator
friction_coeff = 1/unit.picosecond
timestep = dt*unit.femtosecond
temperature = 300*unit.kelvin
integrator = mm.LangevinMiddleIntegrator(temperature, friction_coeff, timestep)
platform = mm.Platform.getPlatformByName(platform_name)
simulation = app.Simulation(top, system, integrator, platform,properties)

restart = False
time_so_far = 0
# check if checkpoint exists
if os.path.isfile('checkpoint.cpt'):
    restart = True
    print('Loading a restart...')
    simulation.loadCheckpoint('checkpoint.cpt')
    #simulation.loadState('checkpnt.xml')
    # find out how many steps to run left
    sim_log = [ i for i in open('data.csv').readlines() ]
    last_line = sim_log[-1]
    time_so_far = float(last_line.split(',')[1]) # how much time run so far
    num_steps -= int(round(time_so_far) / (dt/1000))
    print('num_steps: '+str(num_steps))
    if num_steps==0:
        print('Simulation complete. Closing...')
        exit(73)
# add dcd. Append if available
simulation.reporters.append(app.DCDReporter(out_dcd, output_interval, append=restart))
# Append state reporter
simulation.reporters.append(app.StateDataReporter('data.csv', output_interval, step=True, time=True, potentialEnergy=True, temperature=True, volume=True, density=True, speed=True))
# Append checkpoint file
simulation.reporters.append(app.CheckpointReporter('checkpoint.cpt', output_interval))
print('Running Production...')
simulation.step(num_steps)


