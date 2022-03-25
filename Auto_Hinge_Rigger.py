from maya import cmds

cmds.select(clear=True)

def CreateHinge(directionString, limbStringList):
    hingeRoot = limbStringList[0]
    hinge = limbStringList[1]
    hingeEnd = limbStringList[2]
    limb = limbStringList[3]


    for i in range(3):
        i = i+1
        cmds.joint( p=(0, 0, 0)) #Create joint
        cmds.parentConstraint("locator"+str(i),"joint"+str(i))
        cmds.delete("joint"+str(i) + "_parentConstraint1")
        cmds.select(clear=True)

    cmds.rename("joint1", f"{directionString}{hingeRoot}")
    cmds.rename("joint2", f"{directionString}{hinge}")
    cmds.rename("joint3", f"{directionString}{hingeEnd}")

    cmds.parent(f"{directionString}{hinge}", f"{directionString}{hingeRoot}") #parent joints
    cmds.parent(f"{directionString}{hingeEnd}", f"{directionString}{hinge}")

    cmds.select(f"{directionString}{hingeRoot}", f"{directionString}{hinge}")#Orient joints
    cmds.joint(edit=True, orientJoint="xyz", sao="xup", children=True)
    cmds.select(f"{directionString}{hingeEnd}")
    cmds.joint(edit=True, orientation = (0,0,0))

    duplicatesA = cmds.duplicate(f"{directionString}{hingeRoot}", renameChildren = True) #Duplicate joints
    duplicatesB = cmds.duplicate(f"{directionString}{hingeRoot}", renameChildren = True) #Duplicate joints
    duplicatesA.append(f"{directionString}{hingeRoot}")
    for nn in duplicatesA:
        newnameA = nn.replace("1", "_IK_JNT")
        cmds.rename(nn, newnameA)

    for nn in duplicatesB:
        newnameB = nn.replace("2", "_FK_JNT")
        cmds.rename(nn, newnameB)

    cmds.rename(f"{directionString}{hingeRoot}", f"{directionString}{hingeRoot}_JNT")
    cmds.rename(f"{directionString}{hinge}", f"{directionString}{hinge}_JNT")
    cmds.rename(f"{directionString}{hingeEnd}", f"{directionString}{hingeEnd}_JNT")

    cmds.ikHandle(sj=f"{directionString}{hingeRoot}_IK_JNT", endEffector=f"{directionString}{hingeEnd}_IK_JNT", priority=2, weight=5, name=f"{directionString}{limb}_IK_HDL") #Create IKhandle
    cmds.rename("effector1", f"{directionString}{limb}_EFF")

    #Create locators as controls ARMS
    cmds.spaceLocator(name = f"{directionString}{hingeRoot}_FK_CTRL")
    cmds.spaceLocator(name = f"{directionString}{hinge}_FK_CTRL")
    cmds.spaceLocator(name = f"{directionString}{hingeEnd}_FK_CTRL")
    cmds.spaceLocator(name = f"{directionString}FK_{hinge}_LOC")

    cmds.group(f"{directionString}{hingeRoot}_FK_CTRL" , n=f"{directionString}{hingeRoot}_FK_Offset")
    cmds.group(f"{directionString}{hinge}_FK_CTRL" , n=f"{directionString}{hinge}_FK_Offset")
    cmds.group(f"{directionString}{hingeEnd}_FK_CTRL" , n=f"{directionString}{hingeEnd}_FK_Offset")
    cmds.group(f"{directionString}FK_{hinge}_LOC" , n=f"{directionString}FK_{hinge}_Offset")

    cmds.parent(f"{directionString}FK_{hinge}_Offset" , f"{directionString}{hinge}_FK_Offset")

    cmds.parent(f"{directionString}{hinge}_FK_Offset" , f"{directionString}{hingeRoot}_FK_CTRL")
    cmds.parent(f"{directionString}{hingeEnd}_FK_Offset" , f"{directionString}{hinge}_FK_CTRL")

    cmds.spaceLocator(name = f"{directionString}{hingeEnd}_IK_CTRL")
    cmds.group(f"{directionString}{hingeEnd}_IK_CTRL" , n=f"{directionString}{hingeEnd}_IK_Offset")

    cmds.parentConstraint(f"{directionString}{hingeEnd}_IK_JNT",f"{directionString}{hingeEnd}_IK_Offset")
    cmds.delete(f"{directionString}{hingeEnd}_IK_Offset_parentConstraint1")
    cmds.parent(f"{directionString}{limb}_IK_HDL", f"{directionString}{hingeEnd}_IK_CTRL")

    cmds.addAttr(f"{directionString}{hingeRoot}_FK_CTRL", longName='IK2FK', min=0, max=1, dv=0, keyable=True) #Add IK/FK attribute

    for i in [f"{hingeRoot}_FK", f"{hinge}_FK", f"{hingeEnd}_FK"]:
        cmds.parentConstraint(f"{directionString}{i}_JNT",f"{directionString}{i}_Offset")
        cmds.delete(f"{directionString}{i}_Offset_parentConstraint1")
        cmds.parentConstraint(f"{directionString}{i}_CTRL",f"{directionString}{i}_JNT")

    #PV creator
    pts = []

    cmds.select("locator1", "locator2", "locator3")

    cmds.select( cmds.listRelatives( type = 'locator', fullPath = True, allDescendents = True ) )
    cmds.select( cmds.listRelatives( parent = True, fullPath = True ) )
    sel = cmds.ls (type = 'transform', orderedSelection = True )

    for loc in sel:
        coords = cmds.xform (loc, query=True, worldSpace=True, pivots=True)[0:3]
        pts.append(coords)

    cmds.polyCreateFacet(name = "plane", p = pts) #Create triangular plane

    shoulder = pts[0]
    wrist = pts[-1]
    deltaX = wrist[0] - shoulder[0]
    deltaY = wrist[1] - shoulder[1]
    deltaZ = wrist[2] - shoulder[2]

    half = (deltaX*0.5, deltaY*0.5, deltaZ*0.5)
    mid = (shoulder[0]+half[0],shoulder[1]+half[1],shoulder[2]+half[2])

    cmds.spaceLocator(absolute=True, n="middle", p=(mid))

    cmds.xform('plane.vtx[0]', query=True, t=True, ws=True)
    cmds.xform('plane', rotatePivot=mid, scalePivot=mid)

    cmds.scale( 4, 4, 4, 'plane', absolute=True )#Scale the plane

    cmds.spaceLocator(name = f"{directionString}{limb}_PV") #Make PV
    cmds.group(f"{directionString}{limb}_PV" , n=f"{directionString}{limb}_PV_Offset") #Group PV
    position1 = cmds.xform('plane.vtx[1]', query=True, t=True, ws=True)
    cmds.xform(f"{directionString}{limb}_PV_Offset", t=position1) #Move PV to location

    cmds.poleVectorConstraint( f"{directionString}{limb}_PV", f"{directionString}{limb}_IK_HDL")

    cmds.delete("plane") #Delete plane
    cmds.delete("locator1", "locator2", "locator3") #Delete locators
    cmds.delete("middle")

    #Networks
    cmds.createNode("network", name=f"{directionString}FK_{limb}_Network")
    cmds.addAttr(f"{directionString}FK_{limb}_Network", ln=f"{directionString}FK_{hingeRoot}", dataType="string")
    cmds.addAttr(f"{directionString}FK_{limb}_Network", ln=f"{directionString}FK_{hinge}", dataType="string")
    cmds.addAttr(f"{directionString}FK_{limb}_Network", ln=f"{directionString}FK_{hingeEnd}", dataType="string")
    cmds.addAttr(f"{directionString}FK_{limb}_Network", ln=f"{directionString}FK_{hinge}_LOC", dataType="string")

    cmds.createNode("network", name=f"{directionString}IK_{limb}_Network")
    cmds.addAttr(f"{directionString}IK_{limb}_Network", ln=f"{directionString}IK_{hingeEnd}", dataType="string")
    cmds.addAttr(f"{directionString}IK_{limb}_Network", ln=f"{directionString}{limb}_PV", dataType="string")

    cmds.connectAttr(f"{directionString}{hingeRoot}_FK_CTRL.message" , f"{directionString}FK_{limb}_Network.{directionString}FK_{hingeRoot}")
    cmds.connectAttr(f"{directionString}{hinge}_FK_CTRL.message" , f"{directionString}FK_{limb}_Network.{directionString}FK_{hinge}")
    cmds.connectAttr(f"{directionString}{hingeEnd}_FK_CTRL.message" , f"{directionString}FK_{limb}_Network.{directionString}FK_{hingeEnd}")
    cmds.connectAttr(f"{directionString}FK_{hinge}_LOC.message" , f"{directionString}FK_{limb}_Network.{directionString}FK_{hinge}_LOC")

    cmds.connectAttr(f"{directionString}{hingeEnd}_IK_CTRL.message" , f"{directionString}IK_{limb}_Network.{directionString}IK_{hingeEnd}")
    cmds.connectAttr(f"{directionString}{limb}_PV.message" , f"{directionString}IK_{limb}_Network.{directionString}{limb}_PV")

    #Blend
    cmds.createNode("blendColors", name=f"{directionString}{hingeRoot}_JNTBC")
    cmds.createNode("blendColors", name=f"{directionString}{hinge}_JNTBC")
    cmds.createNode("blendColors", name=f"{directionString}{hingeEnd}_JNTBC")
    cmds.connectAttr(f"{directionString}{hingeRoot}_FK_CTRL.IK2FK" , f"{directionString}{hingeRoot}_JNTBC.blender")
    cmds.connectAttr(f"{directionString}{hingeRoot}_FK_CTRL.IK2FK" , f"{directionString}{hinge}_JNTBC.blender")
    cmds.connectAttr(f"{directionString}{hingeRoot}_FK_CTRL.IK2FK" , f"{directionString}{hingeEnd}_JNTBC.blender")
    for nc in [f"{hingeRoot}_", f"{hinge}_", f"{hingeEnd}_"]:
        cmds.connectAttr(f"{directionString}{nc}FK_JNT.rotate", f"{directionString}{nc}JNTBC.color1")
        cmds.connectAttr(f"{directionString}{nc}IK_JNT.rotate", f"{directionString}{nc}JNTBC.color2")
        cmds.connectAttr(f"{directionString}{nc}JNTBC.output", f"{directionString}{nc}JNT.rotate")

    for i in [f"{directionString}{hinge}_FK_CTRL", f"{directionString}{hingeEnd}_FK_CTRL", f"{directionString}{hingeEnd}_IK_CTRL", f"{directionString}{limb}_PV", f"{directionString}FK_{hinge}_LOC"]:
            cmds.addAttr( i, ln="IK2FK", proxy = f"{directionString}{hingeRoot}_FK_CTRL.IK2FK", keyable = True)


def action_button(rightRB, armRB):

    '''
    Create an object based on...
    '''

    armJointNames = ["Shoulder", "Elbow", "Wrist", "Arm"]
    legJointNames = ["Hip", "Knee", "Ankle", "Leg"]
    isArm = cmds.radioButton(armRB, query=True, select = True)
    isRight = cmds.radioButton(rightRB, query=True, select = True)
    directionString = "R_" if isRight else "L_"
    limbStringList = armJointNames if isArm else legJointNames
    CreateHinge(directionString, limbStringList)

#Create window
if cmds.window("Hinge_Window", exists=True):
    cmds.deleteUI("Hinge_Window", window=True )

window = cmds.window("Hinge_Window", title="Hinge_Window", widthHeight=(450, 200))
cmds.columnLayout(adjustableColumn=True)
cmds.rowColumnLayout(numberOfColumns = 3, columnWidth=[(2,75), (2,75), (2,75)])

cmds.radioCollection()
armRB = cmds.radioButton( label="Arm", select=True) #onCommand) = ArmFunction)
legRB = cmds.radioButton( label="Leg" ) #onCommand = Function
cmds.separator(horizontal=False, style="none", h=10)

cmds.radioCollection()
leftRB = cmds.radioButton( label="Left", select=True) #onCommand = Function
rightRB = cmds.radioButton(label="Right") #, onCommand = RightFuncion)
cmds.separator(horizontal=False, style="none", h=10)

cmds.separator(horizontal=False, style="none", h=10)
cmds.separator(horizontal=False, style="none", h=10)
cmds.separator(horizontal=False, style="none", h=10)


cmds.separator(horizontal=False, style="none", h=10)
cmds.button(label='Create', command=lambda x:action_button(rightRB, armRB), align='left')

cmds.showWindow()
