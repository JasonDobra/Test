import maya.cmds as mc
import sys

#makes a parentconstraint using matrix nodes
#better for performance time

if mc.window("matrixConstraintWindow", exists=True):
    mc.deleteUI("matrixConstraintWindow")
    
mc.window("matrixConstraintWindow", title="jd_MatrixConstraint", wh=(200, 200))

mc.columnLayout(adj=True)
mc.text(l="This tool: Is a alternative constraint solution\nDesigned to be better for performance times")
mc.text(l="To use: Use it like a Maya parentConstraint\n", al="center")

mc.separator()
mc.button(l="Matrix Constraint", command="runConstraintFunction()")
mc.checkBox('moBox', l='Maintain offset:', en=1, v=1)
mc.text('')
mc.checkBox('transBox', l='Translate:', en=1, v=1)
mc.checkBox('rotBox', l='Rotate:', en=1, v=1)   
mc.checkBox('scaleBox', l='Scale:', en=1, v=1)  
    
mc.showWindow("matrixConstraintWindow")

def runConstraintFunction():
    
    transChecked = mc.checkBox('transBox', q=1, v=1)
    rotChecked = mc.checkBox('rotBox', q=1, v=1)   
    scaleChecked = mc.checkBox('scaleBox',  q=1, v=1) 
    
    sel = mc.ls(sl=1)
    selSize = len(sel)
    
    driver = sel[0]
    driven = sel[1]
    
    if selSize < 2:
        mc.error('Error: Target list was empty or contained no valid targets.')
       
    if selSize == 2:
        matrixConstaint(driver, driven, transChecked, rotChecked, scaleChecked)
    if selSize == 3:
        matrixBlendConstaint(driver, driven, transChecked, rotChecked, scaleChecked)
    if selSize > 3:
        mc.error('Error: Too many objects selected')       

def matrixConstaint(driver, driven, transChecked, rotChecked, scaleChecked):

    maintainOffset = mc.checkBox('moBox', q=1, v=1)
    
    if maintainOffset:
        tempLoc = mc.spaceLocator()
        mc.matchTransform(tempLoc, driven)
    
    multMatrix = mc.createNode('multMatrix', n='{0}{1}'.format(driven, '_MTX'))
    wtAddMatrix = mc.createNode('wtAddMatrix', n='{0}{1}'.format(driven, '_wtMTX'))
    decomMatrix = mc.createNode('decomposeMatrix', n='{0}{1}'.format(driven, '_DCM'))
    orientPMA = mc.createNode('plusMinusAverage', n='{0}{1}'.format(driven, '_Off_PMA'))
    
    mc.connectAttr('{0}{1}'.format(driver, '.worldMatrix[0]'), '{0}{1}'.format(multMatrix, '.matrixIn[1]'), f=1)
    
    if maintainOffset:
        mc.connectAttr('{0}{1}'.format(tempLoc[0], '.worldInverseMatrix[0]'), '{0}{1}'.format(multMatrix, '.matrixIn[2]'), f=1)
    
    
    #holding an offset
    
        deleteMeMatrix = mc.createNode('multMatrix')
        mc.connectAttr('{0}{1}'.format(driven, '.worldMatrix[0]'), '{0}{1}'.format(deleteMeMatrix, '.matrixIn[0]'))
        mc.connectAttr('{0}{1}'.format(driver, '.worldInverseMatrix[0]'), '{0}{1}'.format(deleteMeMatrix, '.matrixIn[1]'))
        
    #gathers the offset matrix data
        matrixData = mc.getAttr('{0}{1}'.format(deleteMeMatrix, '.matrixSum'))
    
    
    #print(matrixData)
        mc.setAttr('{0}{1}'.format(multMatrix, '.matrixIn[0]'), matrixData, type='matrix')
        mc.delete(deleteMeMatrix, tempLoc)
    
    #connects to decompose matrix
   
    
    mc.connectAttr('{0}{1}'.format(multMatrix, '.matrixSum'), '{0}{1}'.format(decomMatrix, '.inputMatrix'))
   
    if transChecked: 
        mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputTranslate'), '{0}{1}'.format(driven, '.translate'))
    if scaleChecked:
        mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputScale'), '{0}{1}'.format(driven, '.scale'))
    if cmds.ls(driven, type='joint'):
        if rotChecked:
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(driven, '.jointOrient'))
           
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(orientPMA, '.input3D[0]'))
            mc.connectAttr('{0}{1}'.format(driven, '.jointOrient'), '{0}{1}'.format(orientPMA, '.input3D[1]'))
            mc.setAttr('{0}{1}'.format(orientPMA, '.operation'), 2)
            mc.connectAttr('{0}{1}'.format(orientPMA, '.output3D'), '{0}{1}'.format(driven, '.rotate'))
            mc.connectAttr('{0}{1}'.format(driven, '.rotateOrder'), '{0}{1}'.format(decomMatrix, '.inputRotateOrder'))
            
    else:
        if rotChecked:
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(driven, '.rotate'))
        
    mc.connectAttr(driven + '.parentInverseMatrix', multMatrix + '.matrixIn[2]')
    
    mc.select(driver, driven)
    sys.stdout.write('Result :' +  driven + '_matrixConstraint')

def matrixBlendConstaint(driver, driven, transChecked, rotChecked, scaleChecked):

    maintainOffset = mc.checkBox('moBox', q=1, v=1)
    
    sel = mc.ls(sl=1)
    driver1 = sel[0]
    driver2 = sel[1]
    driven = sel[2]
    
    tempLoc = mc.spaceLocator()
    mc.matchTransform(tempLoc, driven)
    
    driverControl = mc.addAttr(driven, ln='parentWeight', at='double', min=0, max=1, dv=0.5, k=1)
    
    #nodes
    multMatrix1 = mc.createNode('multMatrix', n='{0}{1}'.format(driven, '_W0_MTX'))
    multMatrix2 = mc.createNode('multMatrix', n='{0}{1}'.format(driven, '_W1_MTX'))
    wtAddMatrix = mc.createNode('wtAddMatrix', n='{0}{1}'.format(driven, '_wtMTX'))
    decomMatrix = mc.createNode('decomposeMatrix', n='{0}{1}'.format(driven, '_DCM'))
    offsetMatrix = mc.createNode('multMatrix', n='{0}{1}'.format(driven, '_Off_MTX'))
    orientPMA = mc.createNode('plusMinusAverage', n='{0}{1}'.format(driven, '_Off_PMA'))
    
    
    
    #connecting nodes
    mc.connectAttr('{0}{1}'.format(driver1, '.worldMatrix[0]'), '{0}{1}'.format(multMatrix1, '.matrixIn[1]'), f=1)
    mc.connectAttr('{0}{1}'.format(driver2, '.worldMatrix[0]'), '{0}{1}'.format(multMatrix2, '.matrixIn[1]'), f=1)
    
    
    #connects to wtAddmatrix
    mc.connectAttr('{0}{1}'.format(multMatrix1, '.matrixSum'), '{0}{1}'.format(wtAddMatrix, '.wtMatrix[0].matrixIn'))
    mc.connectAttr('{0}{1}'.format(multMatrix2, '.matrixSum'), '{0}{1}'.format(wtAddMatrix, '.wtMatrix[1].matrixIn'))
    
    #connects to offsetMatrix 
    mc.connectAttr('{0}{1}'.format(wtAddMatrix, '.matrixSum'), '{0}{1}'.format(offsetMatrix, '.matrixIn[0]'))
    mc.connectAttr('{0}{1}'.format(driven, '.parentInverseMatrix[0]'), '{0}{1}'.format(offsetMatrix, '.matrixIn[1]'))
    
    
    mc.connectAttr('{0}{1}'.format(offsetMatrix, '.matrixSum'), '{0}{1}'.format(decomMatrix, '.inputMatrix'))
    
    
    
    
    #holding an offset
    
    deleteMeMatrix1 = mc.createNode('multMatrix')
    deleteMeMatrix2 = mc.createNode('multMatrix')
    
    mc.connectAttr('{0}{1}'.format(driven, '.worldMatrix[0]'), '{0}{1}'.format(deleteMeMatrix1, '.matrixIn[0]'))
    mc.connectAttr('{0}{1}'.format(driver1, '.worldInverseMatrix[0]'), '{0}{1}'.format(deleteMeMatrix1, '.matrixIn[1]'))
    
    mc.connectAttr('{0}{1}'.format(driven, '.worldMatrix[0]'), '{0}{1}'.format(deleteMeMatrix2, '.matrixIn[0]'))
    mc.connectAttr('{0}{1}'.format(driver2, '.worldInverseMatrix[0]'), '{0}{1}'.format(deleteMeMatrix2, '.matrixIn[1]'))
    
    #gathers the offset matrix data
    matrixData1 = mc.getAttr('{0}{1}'.format(deleteMeMatrix1, '.matrixSum'))
    matrixData2 = mc.getAttr('{0}{1}'.format(deleteMeMatrix2, '.matrixSum'))
    
    #print(matrixData)
    mc.setAttr('{0}{1}'.format(multMatrix1, '.matrixIn[0]'), matrixData1, type='matrix')
    mc.setAttr('{0}{1}'.format(multMatrix2, '.matrixIn[0]'), matrixData2, type='matrix')
    
    mc.delete(deleteMeMatrix1, deleteMeMatrix2, tempLoc)
    
    #connect driver weight
    mc.connectAttr('{0}{1}'.format(driven, '.parentWeight'), '{0}{1}'.format(wtAddMatrix, '.wtMatrix[0].weightIn'))
    #in order to blend we will need a reverse node
    reverseNode = mc.createNode('reverse', n='{0}{1}'.format(driven, '_RVS'))
    mc.connectAttr('{0}{1}'.format(driven, '.parentWeight'), '{0}{1}'.format(reverseNode, '.inputX'))
    mc.connectAttr('{0}{1}'.format(reverseNode, '.outputX'), '{0}{1}'.format(wtAddMatrix, '.wtMatrix[1].weightIn'))

    if transChecked:
        mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputTranslate'), '{0}{1}'.format(driven, '.translate'))
    if scaleChecked:
        mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputScale'), '{0}{1}'.format(driven, '.scale'))
    
    if cmds.ls(driven, type='joint'):
        if rotChecked:
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(driven, '.jointOrient'))
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(orientPMA, '.input3D[0]'))
            mc.connectAttr('{0}{1}'.format(driven, '.jointOrient'), '{0}{1}'.format(orientPMA, '.input3D[1]'))
            mc.setAttr('{0}{1}'.format(orientPMA, '.operation'), 2)
            mc.connectAttr('{0}{1}'.format(orientPMA, '.output3D'), '{0}{1}'.format(driven, '.rotate'))
            mc.connectAttr('{0}{1}'.format(driven, '.rotateOrder'), '{0}{1}'.format(decomMatrix, '.inputRotateOrder'))
    
    else:
        if rotChecked:
            mc.connectAttr('{0}{1}'.format(decomMatrix, '.outputRotate'), '{0}{1}'.format(driven, '.rotate'))
    
        
    
    mc.select(driver1, driver2, driven)
    
    sys.stdout.write('Result :' +  driven + '_matrixBlendConstraint')
    if not maintainOffset:
        mc.warning('Maintain Offset flag will be ignored')
    

    


