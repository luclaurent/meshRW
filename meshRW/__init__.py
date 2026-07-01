"""Top-level package metadata for meshRW.

The package exposes mesh readers/writers for legacy Gmsh (``.msh``) and
VTK/VTU outputs used by ParaView workflows.
"""

import importlib
import sys

__version__ = '1.6.0'


# Backward-compatible module aliases for legacy imports.
sys.modules.setdefault(
	f'{__name__}.writerClass',
	importlib.import_module('.writerclass', __name__),
)
sys.modules.setdefault(
	f'{__name__}.configMESH',
	importlib.import_module('.config_mesh', __name__),
)
