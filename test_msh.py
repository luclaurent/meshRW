from meshRW import msh
import os
import numpy
import pickle

if __name__ == "__main__":

    CurrentPath = os.path.dirname(__file__)
    hf = open(os.path.abspath(os.path.join(CurrentPath,
                                              './test_data/debug.h5')), 'rb')
    
    data = pickle.load(hf)
    hf.close()
    nodes = data['n']
    elemsData = data['e']

    dataNodes=numpy.random.rand(nodes.shape[0],nodes.shape[1])
    dataElem=numpy.random.rand(elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0],2)
    dataElemStep=[numpy.random.rand(elemsData['TET4'].shape[0]+elemsData['PRI6'].shape[0],3) for i in range(5)]
    # msh.mshWriter(filename=os.path.abspath(os.path.join(CurrentPath,
    #                                           './test_data/vv.msh')),
    #           nodes=nodes,
    #           elems=[{'connectivity': elemsData[list(elemsData.keys())[0]], 'type':list(elemsData.keys())[0], 'physgrp':[5, 5]},
    #                  {'connectivity': elemsData[list(elemsData.keys())[1]], 'type':list(elemsData.keys())[1], 'physgrp':[6, 6]}],
    #                  fields=[{'data':dataNodes,'type':'nodal','dim':3,'name':'nodal3'},#,'steps':list of steps,'nbsteps':number of steps],
    #                     {'data':dataElem,'type':'elemental' ,'dim':2,'name':'name_2'},
    #                     {'data':dataElemStep,'type':'elemental' ,'dim':3,'name':'alongsteps','nbsteps':5}]#,'steps':list of steps,'nbsteps':number of steps]
    #                     )


    msh.mshReader(filename=os.path.abspath(os.path.join(CurrentPath,'./test_data/vv.msh')))
