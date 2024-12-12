import unittest
from . import msh, vtk, msh2, vtk2
import pickle
import numpy
import os

# load current path
CurrentPath = os.path.dirname(__file__)


class TestMSH(unittest.TestCase):

    def test_MSHwriter(self):
        # open data
        hf = open(os.path.abspath(os.path.join(CurrentPath,
                                               './test_data/debug.h5')), 'rb')
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
        msh.mshWriter(filename=os.path.abspath(os.path.join(CurrentPath,
                                                            './test_data/build.msh')),
                      nodes=nodes,
                      elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                             {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                      fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                              {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
                              {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}]  # ,'steps':list of steps,'nbsteps':number of steps]
                      )
        
    def test_MSH2writer(self):
        # open data
        hf = open(os.path.abspath(os.path.join(CurrentPath,
                                               './test_data/debug.h5')), 'rb')
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
        msh2.mshWriter(filename=os.path.abspath(os.path.join(CurrentPath,
                                                            './test_data/build.msh')),
                      nodes=nodes,
                      elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                             {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                      fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                                {'data': dataElem, 'type': 'elemental', 'dim': 2, 'name': 'name_2'},
                              {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}],  # ,'steps':list of steps,'nbsteps':number of steps]
                      version=2.2)

    def test_MSHreader3D(self):
        # open fiel and read it
        msh.mshReader(filename=os.path.abspath(
            os.path.join(CurrentPath, './test_data/mesh3Dref.msh')))

    def test_MSHreader2D(self):
        # open fiel and read it
        msh.mshReader(filename=os.path.abspath(
            os.path.join(CurrentPath, './test_data/mesh2Dref.msh')))

    def test_VTKwriter(self):
        # open data
        hf = open(os.path.abspath(os.path.join(CurrentPath,
                                               './test_data/debug.h5')), 'rb')
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
        vtk.vtkWriter(filename=os.path.abspath(os.path.join(CurrentPath,
                                                            './test_data/build.vtk')),
                      nodes=nodes,
                      elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
                             {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
                      fields=[{'data': dataNodes, 'type': 'nodal', 'dim': 3, 'name': 'nodal3'},  # ,'steps':list of steps,'nbsteps':number of steps],
                              {'data': dataElem, 'type': 'elemental',
                               'dim': 2, 'name': 'name_2'},
                              {'data': dataElemStep, 'type': 'elemental', 'dim': 3, 'name': 'alongsteps', 'nbsteps': 5}]  # ,'steps':list of steps,'nbsteps':number of steps]
                      )


if __name__ == '__main__':
    unittest.main()
