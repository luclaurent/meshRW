"""
This file is part of the meshRW package
---
This file contains the default
declaration of the keywords 
used to declare/manipulate a mesh in Python
----
Luc Laurent - luc.laurent@lecnam.net -- 2021
"""

DFLT_MESH: str = 'connectivity'
DFLT_TYPE_ELEM: str = 'type'
DFLT_PHYS_GRP: str = 'physgrp'
DFLT_FIELD_DATA: str = 'data'
DFLT_FIELD_TYPE: str = 'type'
DFLT_FIELD_TYPE_NODAL: str = 'nodal'
DFLT_FIELD_TYPE_ELEMENT: str = 'elemental'
DFLT_FIELD_TYPE_NODAL_SCALAR: str = 'nodal_scalar'
DFLT_FIELD_TYPE_ELEMENT_SCALAR: str = 'elemental_scalar'
DFLT_FIELD_DIM: str = 'dim'
DFLT_FIELD_NAME: str = 'name'
DFLT_FIELD_STEPS: str = 'steps'
DFLT_FIELD_NBSTEPS: str = 'nbsteps'
DFLT_FIELD_NUMENTITIES: str = 'numentities'

DFLT_NEW_PHYSGRP_NUM: int = 1000
DFLT_NEW_PHYSGRP_GLOBAL_NUM: int = 10000
