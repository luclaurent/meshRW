from meshRW import msh, msh2
import pickle
import numpy
from pathlib import Path

# load current path
CurrentPath = Path(__file__).parent
DataPath = CurrentPath / Path('test_data')
# data file for testing
datafile = DataPath / Path('debug.h5')
# artifacts directory
ArtifactsPath = CurrentPath / Path('artifacts')
ArtifactsPath.mkdir(exist_ok=True)


def test_MSHwriter(self):
    # open data    
    hf = open(datafile, 'rb')
    #
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(
        elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0], 1)
    # generate steps
    dataElemStep = [numpy.random.rand(
        elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0], 3) for i in range(5)]
    # write msh file
    outputfile = ArtifactsPath / Path('build.msh')   
    msh.mshWriter(filename=outputfile,
                    nodes=nodes,
                    elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                            {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                    fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
                            {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}]  # ,'steps':list of steps,'nbsteps':number of steps]
                    )
    assert outputfile.exists()
    
def test_MSH2writer(self):
    # open data
    hf = open(datafile, 'rb')
    data = pickle.load(hf)
    hf.close()
    # extract nodes list
    nodes = data['n']
    # extract elements list and data
    elemsData = data['e']
    # generate data on nodes
    dataNodes = numpy.random.rand(nodes.shape[0], nodes.shape[1])
    # generate data on elements
    dataElem = numpy.random.rand(
        elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0], 2)
    # generate steps
    dataElemStep = [numpy.random.rand(
        elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0], 3) for i in range(5)]
    # write msh file
    outputfile = ArtifactsPath / Path('build2.msh')   
    msh2.mshWriter(filename=outputfile,
                    nodes=nodes,
                    elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                            {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                    fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
                            {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}],  # ,'steps':list of steps,'nbsteps':number of steps]
                    version=2.2)

def test_MSHreader3D(self):
    inputfile = DataPath / Path('mesh3Dref.msh')
    # open file and read it
    msh.mshReader(filename=inputfile)

def test_MSHreader2D(self):
    inputfile = DataPath / Path('mesh3Dref.msh')
    # open file and read it
    msh.mshReader(filename=inputfile)




# # if __name__ == "__main_":

# CurrentPath = os.path.dirname(__file__)
# # hf = open(os.path.abspath(os.path.join(CurrentPath,
# #                                           './test_data/debug.h5')), 'rb')

# # data = pickle.load(hf)
# # hf.close()
# # nodes = data['n']
# # elemsData = data['e']

# # dataNodes=numpy.random.rand(nodes.shape[0],nodes.shape[1])
# # dataElem=numpy.random.rand(elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0],2)
# # dataElemStep=[numpy.random.rand(elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0],3) for i in range(5)]
# # msh.mshWriter(filename=os.path.abspath(os.path.join(CurrentPath,
# #                                           './test_data/vv.msh')),
# #           nodes=nodes,
# #           elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
# #                  {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
# #                  fields=[{'data':dataNodes,'type':'nodal','dim':3,'name':'nodal3'},#,'steps':list of steps,'nbsteps':number of steps],
# #                     {'data':dataElem,'type':'elemental' ,'dim':2,'name':'name_2'},
# #                     {'data':dataElemStep,'type':'elemental' ,'dim':3,'name':'alongsteps','nbsteps':5}]#,'steps':list of steps,'nbsteps':number of steps]
# #                     )


# # msh.mshReader(filename=os.path.abspath(os.path.join(CurrentPath,'./meshRW/test_data/vv.msh')))
# M = msh.mshReader(filename=os.path.abspath(os.path.join(CurrentPath,'meshRW/test_data/mesh2Dref.msh')),dim=2)
# M.getElements(dictFormat = False)
# M.getNodes()