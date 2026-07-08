from abaqus import *
from abaqusConstants import *
Mdb()
m = mdb.models['Model-1']
attrs = [a for a in dir(m) if 'Output' in a or 'output' in a]
print('\n'.join(sorted(attrs)))
