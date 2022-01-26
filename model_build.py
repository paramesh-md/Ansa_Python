# PYTHON script
import os
import ansa
from ansa import utils
from ansa import base
from ansa import constants
from ansa import batchmesh
from ansa import connections
import numpy as np
from ansa import guitk
from ansa import mesh

      
def window():

	win = guitk.BCWindowCreate("My_Tools", guitk.constants.BCOnExitDestroy)
	guitk.BCWindowShowTitleBarButtons(win, guitk.constants.BCMinimizeButton | guitk.constants.BCMaximizeButton)
    pid_list  = []
	guitk.BCPushButtonCreate(win, "Pick PIDS", RunFunc, pid_list)
	guitk.BCPushButtonCreate(win, "Connections", ConnectionFunc, win)
	guitk.BCPushButtonCreate(win, "RBE2", SpiderFunc, win)
	dbb = guitk.BCDialogButtonBoxCreate(win)
        
	guitk.BCWindowSetInitSize(win, 240, 160)
	guitk.BCWindowSetSaveSettings(win, False)
        
	guitk.BCWindowSetAcceptFunction(win, acceptFunc, None)
	guitk.BCWindowSetRejectFunction(win, rejectFunc, None)
        
	guitk.BCShow(win)
	
	
def RunFunc(b,data):
        ret = base.PickEntities(constants.ABAQUS, "SHELL_SECTION")
        for r in ret:
        	data.append(r)
        return 0
        
def ConnectionFunc(b, win):
	conn()
	base.RedrawAll()
	return 0

def SpiderFunc(b, win):
	CreateSpider()
	base.RedrawAll()
	return 0
        
def acceptFunc(win, data):
        #values = RunFunc()
        print(data)
        return 1
        
def rejectFunc(win, data):
	mesh.EraseMesh()
	solids = base.CollectEntities(constants.NASTRAN, None, "SOLID")
	spider = base.CollectEntities(constants.NASTRAN, None, "RBE2")
	base.DeleteEntity(solids)
	base.DeleteEntity(spider)
	
	print("Reject")
	return 1


#============================================================================
def main():
	# Need some documentation? Run this with F5
	
	window()
	#run()
	#conn()
	#CreateSpider()
	
def run():
	mesh_file = utils.SelectOpenFile(0, 'mpar files (*.ansa_mpar)')
	print(mesh_file[0])
	mesh_scen = batchmesh.GetNewMeshingScenario('Meshing_Scenario1' , 'PIDS')
	print(mesh_scen._name)
	parts = base.CollectEntities (ansa.constants.NASTRAN, None, 'PSHELL')
	ret_val = batchmesh.AddPartToMeshingScenario (parts, mesh_scen)
	session = batchmesh.GetSessionsFromMeshingScenario(mesh_scen)
	mesh_params = batchmesh.ReadSessionMeshParams(session[0], mesh_file[0])
	status = batchmesh.RunMeshingScenario(mesh_scen, 10)
	

def conn():
	conn_list = []
	width = 3
	prop1 = base.PickEntities(constants.NASTRAN, "PSHELL")
	prop2 = base.PickEntities(constants.NASTRAN, "PSHELL")
	curves = base.PickEntities(constants.NASTRAN, "CURVE")
	part_list = ["#"+str(prop1[0]._id), "#"+str(prop2[0]._id)]
	print("prop1 = ", prop1, "prop2 = ", prop2, curves)
	
	
	for curve in curves:
		cnctn = connections.CreateConnectionLine("SeamLine_Type", curve, curve._id, part_list,)
		base.SetEntityCardValues(constants.NASTRAN, cnctn,{"W":width})
		conn_list.append(cnctn)
	connections.RealizeConnections(conn_list,{'SeamLine_HEXA_CONTACT_PSOLID_ID': '', 'SeamLine_Type': 'HEXA-CONTACT', 'SeamLine_HEXA_CONTACT_DistributionOffLen': '0.000000', 'SeamLine_HEXA_CONTACT_DistFromPerim': '', 'SeamLine_HEXA_CONTACT_DistributionIndex': '1', 'SeamLine_HEXA_CONTACT_FailIfJACOBIAN': '', 'SeamLine_HEXA_CONTACT_NumOfStripes': '1', 'SeamLine_HEXA_CONTACT_FailIfNormalAngle': '', 'SeamLine_HEXA_CONTACT_SpecifyGap': '0.000000', 'SeamLine_HEXA_CONTACT_SearchDist': '', 'SeamLine_HEXA_CONTACT_LimitWidth': 'n', 'SeamLine_HEXA_CONTACT_DistributionOnLen': '0.000000', 'SeamLine_HEXA_CONTACT_StepLengthIndex': '1', 'SeamLine_HEXA_CONTACT_SingleContact': 'n', 'SeamLine_HEXA_CONTACT_ContactId': '', 'SeamLine_HEXA_CONTACT_NumOfLayers': '1', 'SeamLine_HEXA_CONTACT_ForceOff': 'n', 'SeamLine_HEXA_CONTACT_Contacts': 'y', 'SeamLine_HEXA_CONTACT_StepLength': '', 'SeamLine_HEXA_CONTACT_FailIfAspect': '', 'SeamLine_HEXA_CONTACT_DoNotMove': 'n', 'SeamLine_HEXA_CONTACT_ForceOn': 'n'})
	
	
def GetCoordinates(node):
	node = base.GetEntityCardValues(constants.NASTRAN, node, ("NID","X1","X2","X3"))
	x = node["X1"]
	y = node["X2"]
	z = node["X3"]
	#arr = [x,y,z]
	return [x,y,z]
	
def centroid(all_coords):
	cog = np.mean (all_coords, axis=0)
	return cog
	
	
def CreateSpider():
	
	nodes = base.PickEntities(constants.NASTRAN, "GRID")
	node_ids = []
	all_coords = []
	for node in nodes:
		node_ids.append(node._id)
		coord = GetCoordinates(node)
		all_coords.append(coord)
	cog = centroid(all_coords)
	#master = base.Newpoint(cog[0], cog[1], cog[2] )
	master_n = base.CreateEntity(constants.NASTRAN, "GRID", { "X1": cog[0], "X2":cog[1], "X3":cog[2] } )
	print(master_n)
	base.BranchEntity("RBE2",  [master_n._id]+node_ids, "add")
	



if __name__ == '__main__':
	main()
