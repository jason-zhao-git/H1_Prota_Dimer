# run simulation of a protein.
import numpy as np
import pandas as pd
import os
import sys
import simtk.openmm as mm
import simtk.openmm.app as app
import simtk.unit as unit

from openabc.forcefields.parsers import MOFFParser, MRGdsDNAParser
from openabc.forcefields import MOFFMRGModel
from openabc.utils.insert import insert_molecules
# set simulation platform
platform_name = 'CUDA'

print('Successful import')

# start from predicted PDB
h1_parser = MOFFParser.from_atomistic_pdb('H1_AF.pdb', 'H1_CA.pdb')
prota_parser = MOFFParser.from_atomistic_pdb('ProTa_AF.pdb', 'ProTa_CA.pdb')

# Loop here to remove some native pairs
old_native_pairs = h1_parser.native_pairs.copy()
new_native_pairs = pd.DataFrame(columns=old_native_pairs.columns)
globular_domain = np.arange(23, 96)
for i, row in old_native_pairs.iterrows():
    a1, a2 = int(row['a1']), int(row['a2'])
    if a1 > a2:
        a1, a2 = a2, a1
    flag1 = ((a1 in globular_domain) and (a2 in globular_domain))
    if flag1:
        new_native_pairs.loc[len(new_native_pairs.index)] = row
h1_parser.native_pairs = new_native_pairs
h1_parser.parse_exclusions() # update exclusions based on the new native pairs

old_native_pairs = prota_parser.native_pairs.copy()
new_native_pairs = pd.DataFrame(columns=old_native_pairs.columns)

prota_parser.native_pairs = new_native_pairs
prota_parser.parse_exclusions()

# check interaction parameters

print(h1_parser.native_pairs)
print(prota_parser.native_pairs)

# prepare initial configuration with n1 H1 and n2 ProTa
a, b, c = 14, 14, 14
n1, n2 = 1, 1
if not os.path.exists('start.pdb'):
    insert_molecules('H1_CA.pdb', 'tmp.pdb', n_mol=n1, box=[a, b, c])
    insert_molecules('ProTa_CA.pdb', 'start.pdb', n_mol=n2, existing_pdb='tmp.pdb', box=[a, b, c])

# set up protein model
protein = MOFFMRGModel()
# add protein to model
protein.append_mol(h1_parser)
protein.append_mol(prota_parser)

# setup initial topology
combined_topology = app.PDBFile('start.pdb').getTopology()
protein.create_system(combined_topology, box_a=a, box_b=b, box_c=c, remove_cmmotion=True)

# setup variables necessary for simulations
salt_concentration = 165*unit.millimolar
temperature = 300*unit.kelvin
# add force terms to simulation
protein.add_protein_bonds(force_group=1)
protein.add_protein_angles(force_group=2)
protein.add_protein_dihedrals(force_group=3)
protein.add_native_pairs(force_group=4)
protein.add_contacts(force_group=5)
protein.add_elec_switch(salt_concentration, temperature, force_group=6)
# save initial system
protein.save_system('H1_Prota_system.xml')
# setup integrator
friction_coeff = 1/unit.picosecond
timestep = 5*unit.femtosecond
integrator = mm.LangevinMiddleIntegrator(temperature, friction_coeff, timestep)
# setup initial coordinates
init_coord = app.PDBFile('start.pdb').getPositions()

# setup simulation
protein.set_simulation(integrator, platform_name, init_coord=init_coord)
# perform energy minimization
protein.simulation.minimizeEnergy()
output_interval = 20000
output_dcd = 'output.dcd'
# Run short simulation
protein.add_reporters(output_interval, output_dcd)
protein.simulation.reporters.append(app.checkpointreporter.CheckpointReporter('checkpoint.cpt',output_interval))
protein.simulation.reporters.append(app.StateDataReporter('data.csv', output_interval, step=True, potentialEnergy=True, temperature=True, volume=True, density=True, speed=True, time=True))

protein.simulation.context.setVelocitiesToTemperature(temperature)
protein.simulation.step(400000000)


