import pickle
from pathlib import Path
import pytest
import numpy
from meshRW import msh, msh2

# load current path
CurrentPath = Path(__file__).parent
DataPath = CurrentPath / Path('test_data')
# data file for testing
datafile = DataPath / Path('debug.h5')
# artifacts directory
ArtifactsPath = CurrentPath / Path('artifacts')
ArtifactsPath.mkdir(exist_ok=True)


def test_MSHwriter():
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
                            {'data': dataElem, 'type': 'elemental', 'dim': 1, 'name': 'name_2'},
                            {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}]  # ,'steps':list of steps,'nbsteps':number of steps]
                    )
    assert outputfile.exists()

@pytest.mark.parametrize("append", [True,False])
@pytest.mark.parametrize("version", [2.2,4])
def test_MSH2writer(append,version):
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
    outputfile = ArtifactsPath / Path('build{}-app{}.msh'.format(version,append))
    msh2.mshWriter(filename=outputfile,
                    nodes=nodes,
                    elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                            {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                    fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                            {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
                            {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}],  # ,'steps':list of steps,'nbsteps':number of steps]
                    version=version,                    
                    append=append)
       
    assert outputfile.exists()

def test_MSHreader3D():
    inputfile = DataPath / Path('mesh3Dref.msh')
    # open file and read it
    mesh = msh.mshReader(filename=inputfile)
    assert mesh.getNodes().shape == (21050,3)
    assert mesh.getTags() == [5, 6]
    assert mesh.getElements().get('TET4').shape == (96925, 4)
    assert mesh.getElements().get('PRI6').shape == (1667,6)
    assert mesh.getElements(type='TET4').shape == (96925, 4)
    assert mesh.getElements(type='PRI6').shape == (1667, 6)
    assert mesh.getElements(tag=5).get('TET4').shape == (96925, 4)
    assert mesh.getElements(tag=6).get('PRI6').shape == (1667,6)
    assert mesh.getElements(tag=6).get('TET4') is None
    assert mesh.getElements(tag=5).get('PRI6') is None
    assert len(mesh.getElements(tag=6, type='TET4')) == 0
    assert len(mesh.getElements(tag=5, type='PRI6')) == 0

def test_MSHreader2D():
    inputfile = DataPath / Path('mesh2Dref.msh')
    # open file and read it
    mesh = msh.mshReader(filename=inputfile)
    assert mesh.getNodes().shape == (7480,3)
    assert mesh.getTags() == [2, 4, 1, 15, 5, 27]
    assert mesh.getElements().get('LIN2').shape == (52, 2)
    assert mesh.getElements().get('TRI3').shape == (14614,3)
    assert mesh.getElements(type='LIN2').shape == (52,2)
    assert mesh.getElements(type='TRI3').shape == (14614, 3)
    assert mesh.getElements(tag=2, type='LIN2').shape == (52,2)
    assert mesh.getElements(tag=4, type='LIN2').shape == (52,2)
    assert mesh.getElements(tag=1, type='TRI3').shape == (14614,3)
    assert mesh.getElements(tag=15, type='TRI3').shape == (14156,3)
    assert mesh.getElements(tag=5, type='TRI3').shape == (458,3)
    assert mesh.getElements(tag=27, type='TRI3').shape == (458,3)
    assert len(mesh.getElements(tag=5, type='LIN2')) == 0
    assert len(mesh.getElements(tag=27, type='LIN2')) == 0




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
