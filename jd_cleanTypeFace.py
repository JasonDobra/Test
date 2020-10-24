import maya.cmds as mc

selectedFace = mc.ls(sl=1)

for s in selectedFace:
    mc.polyExtrudeFacet(s, offset=0.2, divisions=2)
    mc.polyTriangulate()