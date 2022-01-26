# PYTHON script
import os
import ansa
import math
from ansa import base
from ansa import constants

class beam:
	
	def __init__(self,ConnObj):
		self.mass  = 0
		self.id = ConnObj._id
		self.name = ConnObj._name
		length = base.GetEntityCardValues(constants.ABAQUS,ConnObj, ('length',))
		pid = base.GetEntityCardValues(constants.ABAQUS,ConnObj, ('PID',))	
		self.pid = pid['PID']
		self.length = float(length['length'])
		
	def calcmass(self):
		prop = base.GetEntity(constants.ABAQUS, "BEAM_SECTION", self.pid)
		mid = base.GetEntityCardValues(constants.ABAQUS, prop, ('MID',))	
		mat = base.GetEntity(constants.ABAQUS, "MATERIAL", int(mid['MID']))
		ret = base.GetEntityCardValues(constants.ABAQUS, prop,('RADIUS',))
		ret_mat = base.GetEntityCardValues(constants.ABAQUS, mat,('DENS',))
		radius = float(ret['RADIUS'])
		density = float(ret_mat['DENS'])
		area = math.pi*radius**2
		volume = area*self.length
		self.mass = density*volume					
	
	def output(self):
		return 'Mass of Beam = ' +str(self.mass)
	

def main():
	total_mass = 0
	beams  = base.PickEntities(constants.ABAQUS, "BEAM",)
	for b in beams:
		mybeam = beam(b)
		mybeam.calcmass()
		print(mybeam.mass)
		total_mass = total_mass + mybeam.mass
	print(total_mass)


	

if __name__ == '__main__':
	main()
