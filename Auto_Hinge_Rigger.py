from maya import cmds

cmds.select(clear=True)

def ArmFunction(isRight=False):
    side = "R_" if isRight else "L_"

    cmds.select(clear=True)
    for getal in range(3):
        print(getal)
        getal = getal+1
        cmds.joint( p=(0, 0, 0)) #Create joint
        cmds.select(f"locator{getal}",f"joint{getal}")
        cmds.parentConstraint()
        cmds.delete(f"joint{getal}" + "_parentConstraint1")
        cmds.select(clear=True)

    #cmds.delete("locator1", "locator2", "locator3") #Delete locators
    cmds.rename("joint1", f"{side}Shoulder_JNT")
    cmds.rename("joint2", f"{side}Elbow_JNT")
    cmds.rename("joint3", f"{side}Wrist_JNT")

    cmds.parent(f"{side}Elbow_JNT", f"{side}Shoulder_JNT") #parent joints
    cmds.parent(f"{side}Wrist_JNT", f"{side}Elbow_JNT")

    cmds.select(f"{side}Shoulder_JNT", f"{side}Elbow_JNT")#Orient joints
    cmds.joint(edit=True, orientJoint="xyz", sao="xup", children=True)
    cmds.select(f"{side}Wrist_JNT")
    cmds.joint(edit=True, orientation = (0,0,0))

    duplicatesA = cmds.duplicate(f"{side}Shoulder_JNT", renameChildren = True) #Duplicate joints
    duplicatesB = cmds.duplicate(f"{side}Shoulder_JNT", renameChildren = True) #Duplicate joints
    duplicatesA.append(f"{side}Shoulder_JNT")
    for nn in duplicatesA:
        newnameA = nn.replace("_JNT1", "_IK_JNT")
        cmds.rename(nn, newnameA)

    for nn in duplicatesB:
        newnameB = nn.replace("_JNT2", "_FK_JNT")
        cmds.rename(nn, newnameB)

    cmds.ikHandle(sj=f"{side}Shoulder_IK_JNT", endEffector=f"{side}Wrist_IK_JNT", priority=2, weight=5, name=f"{side}Arm_IK_HDL") #Create IKhandle
    cmds.rename("effector1", f"{side}Arm_EFF")

    #Create locators as controls ARMS
    cmds.spaceLocator(name = f"{side}Shoulder_FK_CTRL")
    cmds.spaceLocator(name = f"{side}Elbow_FK_CTRL")
    cmds.spaceLocator(name = f"{side}Wrist_FK_CTRL")
    cmds.spaceLocator(name = f"{side}FK_Elbow_LOC")

    cmds.group(f"{side}Shoulder_FK_CTRL" , n=f"{side}Shoulder_FK_Offset")
    cmds.group(f"{side}Elbow_FK_CTRL" , n=f"{side}Elbow_FK_Offset")
    cmds.group(f"{side}Wrist_FK_CTRL" , n=f"{side}Wrist_FK_Offset")
    cmds.group(f"{side}FK_Elbow_LOC" , n=f"{side}FK_Elbow_Offset")

    cmds.parent(f"{side}FK_Elbow_Offset" , f"{side}Elbow_FK_Offset")

    cmds.parent(f"{side}Elbow_FK_Offset" , f"{side}Shoulder_FK_CTRL")
    cmds.parent(f"{side}Wrist_FK_Offset" , f"{side}Elbow_FK_CTRL")

    cmds.spaceLocator(name = f"{side}Wrist_IK_CTRL")
    cmds.group(f"{side}Wrist_IK_CTRL" , n=f"{side}Wrist_IK_Offset")

    cmds.parentConstraint(f"{side}Wrist_IK_JNT",f"{side}Wrist_IK_Offset")
    cmds.delete(f"{side}Wrist_IK_Offset_parentConstraint1")
    cmds.parent(f"{side}Arm_IK_HDL" , f"{side}Wrist_IK_CTRL")

    cmds.addAttr(f"{side}Shoulder_FK_CTRL", longName='IK2FK', min=0, max=1, dv=0, keyable=True) #Add IK/FK attribute

    for i in ["Shoulder_FK", "Elbow_FK", "Wrist_FK"]:
        cmds.parentConstraint(f"{side}{i}_JNT",f"{side}{i}_Offset")
        cmds.delete(f"{side}{i}_Offset_parentConstraint1")
        cmds.parentConstraint(f"{side}{i}_CTRL",f"{side}{i}_JNT")

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

    cmds.spaceLocator(name = f"{side}Arm_PV") #Make PV
    cmds.group(f"{side}Arm_PV" , n=f"{side}Arm_PV_Offset") #Group PV
    position1 = cmds.xform('plane.vtx[1]', query=True, t=True, ws=True)
    cmds.xform(f"{side}Arm_PV_Offset", t=position1) #Movie PV to location

    cmds.poleVectorConstraint( f"{side}Arm_PV", f"{side}Arm_IK_HDL")

    cmds.delete("plane") #Delete plane
    cmds.delete("locator1", "locator2", "locator3") #Delete locators
    cmds.delete("middle")

    #Networks
    if isRight:
        cmds.createNode("network", name="R_FK_Arm_Network")
        cmds.addAttr("R_FK_Arm_Network", ln="R_FK_Shoulder", dataType="string")
        cmds.addAttr("R_FK_Arm_Network", ln="R_FK_Elbow", dataType="string")
        cmds.addAttr("R_FK_Arm_Network", ln="R_FK_Wrist", dataType="string")
        cmds.addAttr("R_FK_Arm_Network", ln="R_FK_Elbow_LOC", dataType="string")

        cmds.createNode("network", name="R_IK_Arm_Network")
        cmds.addAttr("R_IK_Arm_Network", ln="R_IK_Wrist", dataType="string")
        cmds.addAttr("R_IK_Arm_Network", ln="R_Arm_PV", dataType="string")

        cmds.connectAttr("R_Shoulder_FK_CTRL.message" , "R_FK_Arm_Network.R_FK_Shoulder")
        cmds.connectAttr("R_Elbow_FK_CTRL.message" , "R_FK_Arm_Network.R_FK_Elbow")
        cmds.connectAttr("R_Wrist_FK_CTRL.message" , "R_FK_Arm_Network.R_FK_Wrist")
        cmds.connectAttr("R_FK_Elbow_LOC.message" , "R_FK_Arm_Network.R_FK_Elbow_LOC")

        cmds.connectAttr("R_Wrist_IK_CTRL.message" , "R_IK_Arm_Network.R_IK_Wrist")
        cmds.connectAttr("R_Arm_PV.message" , "R_IK_Arm_Network.R_Arm_PV")

    else:
        cmds.createNode("network", name="L_FK_Arm_Network")
        cmds.addAttr("L_FK_Arm_Network", ln="L_FK_Shoulder", dataType="string")
        cmds.addAttr("L_FK_Arm_Network", ln="L_FK_Elbow", dataType="string")
        cmds.addAttr("L_FK_Arm_Network", ln="L_FK_Wrist", dataType="string")
        cmds.addAttr("L_FK_Arm_Network", ln="L_FK_Elbow_LOC", dataType="string")

        cmds.createNode("network", name="L_IK_Arm_Network")
        cmds.addAttr("L_IK_Arm_Network", ln="L_IK_Wrist", dataType="string")
        cmds.addAttr("L_IK_Arm_Network", ln="L_Arm_PV", dataType="string")

        cmds.connectAttr("L_Shoulder_FK_CTRL.message" , "L_FK_Arm_Network.L_FK_Shoulder")
        cmds.connectAttr("L_Elbow_FK_CTRL.message" , "L_FK_Arm_Network.L_FK_Elbow")
        cmds.connectAttr("L_Wrist_FK_CTRL.message" , "L_FK_Arm_Network.L_FK_Wrist")
        cmds.connectAttr("L_FK_Elbow_LOC.message" , "L_FK_Arm_Network.L_FK_Elbow_LOC")

        cmds.connectAttr("L_Wrist_IK_CTRL.message" , "L_IK_Arm_Network.L_IK_Wrist")
        cmds.connectAttr("L_Arm_PV.message" , "L_IK_Arm_Network.L_Arm_PV")


    #Blend
    if isRight:
        cmds.createNode("blendColors", name="R_Shoulder_JNTBC")
        cmds.createNode("blendColors", name="R_Elbow_JNTBC")
        cmds.createNode("blendColors", name="R_Wrist_JNTBC")
        cmds.connectAttr("R_Shoulder_FK_CTRL.IK2FK" , "R_Shoulder_JNTBC.blender")
        cmds.connectAttr("R_Shoulder_FK_CTRL.IK2FK" , "R_Elbow_JNTBC.blender")
        cmds.connectAttr("R_Shoulder_FK_CTRL.IK2FK" , "R_Wrist_JNTBC.blender")
        for nc in ["Shoulder_", "Elbow_", "Wrist_"]:
            cmds.connectAttr(f"R_{nc}FK_JNT.rotate", f"R_{nc}JNTBC.color1")
            cmds.connectAttr(f"R_{nc}IK_JNT.rotate", f"R_{nc}JNTBC.color2")
            cmds.connectAttr(f"R_{nc}JNTBC.output", f"R_{nc}JNT.rotate")

    else:
        cmds.createNode("blendColors", name="L_Shoulder_JNTBC")
        cmds.createNode("blendColors", name="L_Elbow_JNTBC")
        cmds.createNode("blendColors", name="L_Wrist_JNTBC")
        cmds.connectAttr("L_Shoulder_FK_CTRL.IK2FK" , "L_Shoulder_JNTBC.blender")
        cmds.connectAttr("L_Shoulder_FK_CTRL.IK2FK" , "L_Elbow_JNTBC.blender")
        cmds.connectAttr("L_Shoulder_FK_CTRL.IK2FK" , "L_Wrist_JNTBC.blender")
        for nc in ["Shoulder_", "Elbow_", "Wrist_"]:
            cmds.connectAttr(f"L_{nc}FK_JNT.rotate", f"L_{nc}JNTBC.color1")
            cmds.connectAttr(f"L_{nc}IK_JNT.rotate", f"L_{nc}JNTBC.color2")
            cmds.connectAttr(f"L_{nc}JNTBC.output", f"L_{nc}JNT.rotate")

    if isRight:
        for i in ["R_Elbow_FK_CTRL", "R_Wrist_FK_CTRL", "R_Wrist_IK_CTRL", "R_Arm_PV", "R_FK_Elbow_LOC"]:
            cmds.addAttr( i, ln="IK2FK", proxy = "R_Shoulder_FK_CTRL.IK2FK", keyable = True)
    else:
        for i in ["L_Elbow_FK_CTRL", "L_Wrist_FK_CTRL", "L_Wrist_IK_CTRL", "L_Arm_PV", "L_FK_Elbow_LOC"]:
            cmds.addAttr( i, ln="IK2FK", proxy = "L_Shoulder_FK_CTRL.IK2FK", keyable = True)

def LegFunction(isRight=False):
    side = "R_" if isRight else "L_"

    cmds.select(clear=True)
    for getal in range(3):
        print(getal)
        getal = getal+1
        cmds.joint( p=(0, 0, 0)) #Create joint
        cmds.select(f"locator{getal}",f"joint{getal}")
        cmds.parentConstraint()
        cmds.delete(f"joint{getal}" + "_parentConstraint1")
        cmds.select(clear=True)

    #cmds.delete("locator1", "locator2", "locator3") #Delete locators

    cmds.rename("joint1", f"{side}Hip_JNT")
    cmds.rename("joint2", f"{side}Knee_JNT")
    cmds.rename("joint3", f"{side}Ankle_JNT")

    cmds.parent(f"{side}Knee_JNT", f"{side}Hip_JNT") #parent joints
    cmds.parent(f"{side}Ankle_JNT", f"{side}Knee_JNT")

    cmds.select(f"{side}Hip_JNT", f"{side}Knee_JNT")#Orient joints
    cmds.joint(edit=True, orientJoint="xyz", sao="xup", children=True)
    cmds.select(f"{side}Ankle_JNT")
    cmds.joint(edit=True, orientation = (0,0,0))

    duplicatesA = cmds.duplicate(f"{side}Hip_JNT", renameChildren = True) #Duplicate joints
    duplicatesB = cmds.duplicate(f"{side}Hip_JNT", renameChildren = True)
    duplicatesA.append(f"{side}Hip_JNT")
    for nn in duplicatesA:
        newnameA = nn.replace("_JNT1", "_IK_JNT")
        cmds.rename(nn, newnameA)

    for nn in duplicatesB:
        newnameB = nn.replace("_JNT2", "_FK_JNT")
        cmds.rename(nn, newnameB)

    cmds.ikHandle(sj=f"{side}Hip_IK_JNT", endEffector=f"{side}Ankle_IK_JNT", priority=2, weight=5, name=f"{side}Leg_IK_HDL") #Create IKhandle
    cmds.rename("effector1", f"{side}Leg_EFF")

    #Create locators as controls LEGS
    cmds.spaceLocator(name = f"{side}Hip_FK_CTRL")
    cmds.spaceLocator(name = f"{side}Knee_FK_CTRL")
    cmds.spaceLocator(name = f"{side}Ankle_FK_CTRL")
    cmds.spaceLocator(name = f"{side}FK_Knee_LOC")

    cmds.group(f"{side}Hip_FK_CTRL" , n=f"{side}Hip_FK_Offset")
    cmds.group(f"{side}Knee_FK_CTRL" , n=f"{side}Knee_FK_Offset")
    cmds.group(f"{side}Ankle_FK_CTRL" , n=f"{side}Ankle_FK_Offset")
    cmds.group(f"{side}FK_Knee_LOC" , n=f"{side}FK_Knee_Offset")

    cmds.parent(f"{side}Knee_FK_Offset" , f"{side}Hip_FK_CTRL")
    cmds.parent(f"{side}Ankle_FK_Offset" , f"{side}Knee_FK_CTRL")

    cmds.parent(f"{side}FK_Knee_Offset" , f"{side}Knee_FK_Offset")

    cmds.spaceLocator(name = f"{side}Ankle_IK_CTRL")
    cmds.group(f"{side}Ankle_IK_CTRL" , n=f"{side}Ankle_IK_Offset")

    cmds.parentConstraint(f"{side}Ankle_IK_JNT",f"{side}Ankle_IK_Offset")
    cmds.delete(f"{side}Ankle_IK_Offset_parentConstraint1")
    cmds.parent(f"{side}Leg_IK_HDL" , f"{side}Ankle_IK_CTRL")

    cmds.addAttr(f"{side}Hip_FK_CTRL", longName='IK2FK', min=0, max=1, dv=0, keyable=True) #Add IK/FK attribute

    for i in ["Hip_FK", "Knee_FK", "Ankle_FK"]:
        cmds.parentConstraint(f"{side}{i}_JNT",f"{side}{i}_Offset")
        cmds.delete(f"{side}{i}_Offset_parentConstraint1")
        cmds.parentConstraint(f"{side}{i}_CTRL",f"{side}{i}_JNT")

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

    hip = pts[0]
    ankle = pts[-1]
    deltaX = ankle[0] - hip[0]
    deltaY = ankle[1] - hip[1]
    deltaZ = ankle[2] - hip[2]

    half = (deltaX*0.5, deltaY*0.5, deltaZ*0.5)
    mid = (hip[0]+half[0],hip[1]+half[1],hip[2]+half[2])

    cmds.spaceLocator(absolute=True, n="middle", p=(mid))

    cmds.xform('plane.vtx[0]', query=True, t=True, ws=True)
    cmds.xform('plane', rotatePivot=mid, scalePivot=mid)

    cmds.scale( 3, 3, 3, 'plane', absolute=True )#Scale the plane

    cmds.spaceLocator(name = f"{side}Leg_PV") #Make PV
    cmds.group(f"{side}Leg_PV" , n=f"{side}Leg_PV_Offset") #Group PV
    position1 = cmds.xform('plane.vtx[1]', query=True, t=True, ws=True)
    cmds.xform(f"{side}Leg_PV_Offset", t=position1) #Move PV to location

    cmds.poleVectorConstraint( f"{side}Leg_PV", f"{side}Leg_IK_HDL")

    cmds.delete("plane") #Delete plane
    cmds.delete("locator1", "locator2", "locator3") #Delete locators
    cmds.delete("middle")

    #Networks
    if isRight:
        cmds.createNode("network", name="R_FK_Leg_Network")
        cmds.addAttr("R_FK_Leg_Network", ln="R_FK_Hip", dataType="string")
        cmds.addAttr("R_FK_Leg_Network", ln="R_FK_Knee", dataType="string")
        cmds.addAttr("R_FK_Leg_Network", ln="R_FK_Ankle", dataType="string")
        cmds.addAttr("R_FK_Leg_Network", ln="R_FK_Knee_LOC", dataType="string")

        cmds.createNode("network", name="R_IK_Leg_Network")
        cmds.addAttr("R_IK_Leg_Network", ln="R_IK_Ankle", dataType="string")
        cmds.addAttr("R_IK_Leg_Network", ln="R_Leg_PV", dataType="string")

        cmds.connectAttr("R_Hip_FK_CTRL.message" , "R_FK_Leg_Network.R_FK_Hip")
        cmds.connectAttr("R_Knee_FK_CTRL.message" , "R_FK_Leg_Network.R_FK_Knee")
        cmds.connectAttr("R_Ankle_FK_CTRL.message" , "R_FK_Leg_Network.R_FK_Ankle")
        cmds.connectAttr("R_FK_Knee_LOC.message" , "R_FK_Leg_Network.R_FK_Knee_LOC")

        cmds.connectAttr("R_Ankle_IK_CTRL.message" , "R_IK_Leg_Network.R_IK_Ankle")
        cmds.connectAttr("R_Leg_PV.message" , "R_IK_Leg_Network.R_Leg_PV")

    else:
        cmds.createNode("network", name="L_FK_Leg_Network")
        cmds.addAttr("L_FK_Leg_Network", ln="L_FK_Hip", dataType="string")
        cmds.addAttr("L_FK_Leg_Network", ln="L_FK_Knee", dataType="string")
        cmds.addAttr("L_FK_Leg_Network", ln="L_FK_Ankle", dataType="string")
        cmds.addAttr("L_FK_Leg_Network", ln="L_FK_Knee_LOC", dataType="string")

        cmds.createNode("network", name="L_IK_Leg_Network")
        cmds.addAttr("L_IK_Leg_Network", ln="L_IK_Ankle", dataType="string")
        cmds.addAttr("L_IK_Leg_Network", ln="L_Leg_PV", dataType="string")

        cmds.connectAttr("L_Hip_FK_CTRL.message" , "L_FK_Leg_Network.L_FK_Hip")
        cmds.connectAttr("L_Knee_FK_CTRL.message" , "L_FK_Leg_Network.L_FK_Knee")
        cmds.connectAttr("L_Ankle_FK_CTRL.message" , "L_FK_Leg_Network.L_FK_Ankle")
        cmds.connectAttr("L_FK_Knee_LOC.message" , "L_FK_Leg_Network.L_FK_Knee_LOC")

        cmds.connectAttr("L_Ankle_IK_CTRL.message" , "L_IK_Leg_Network.L_IK_Ankle")
        cmds.connectAttr("L_Leg_PV.message" , "L_IK_Leg_Network.L_Leg_PV")

    #Blend
    if isRight:
        cmds.createNode("blendColors", name="R_Hip_JNTBC")
        cmds.createNode("blendColors", name="R_Knee_JNTBC")
        cmds.createNode("blendColors", name="R_Ankle_JNTBC")
        cmds.connectAttr("R_Hip_FK_CTRL.IK2FK" , "R_Hip_JNTBC.blender")
        cmds.connectAttr("R_Hip_FK_CTRL.IK2FK" , "R_Knee_JNTBC.blender")
        cmds.connectAttr("R_Hip_FK_CTRL.IK2FK" , "R_Ankle_JNTBC.blender")
        for nc in ["Hip_", "Knee_", "Ankle_"]:
            cmds.connectAttr(f"R_{nc}FK_JNT.rotate", f"R_{nc}JNTBC.color1")
            cmds.connectAttr(f"R_{nc}IK_JNT.rotate", f"R_{nc}JNTBC.color2")
            cmds.connectAttr(f"R_{nc}JNTBC.output", f"R_{nc}JNT.rotate")

    else:
        cmds.createNode("blendColors", name="L_Hip_JNTBC")
        cmds.createNode("blendColors", name="L_Knee_JNTBC")
        cmds.createNode("blendColors", name="L_Ankle_JNTBC")
        cmds.connectAttr("L_Hip_FK_CTRL.IK2FK" , "L_Hip_JNTBC.blender")
        cmds.connectAttr("L_Hip_FK_CTRL.IK2FK" , "L_Knee_JNTBC.blender")
        cmds.connectAttr("L_Hip_FK_CTRL.IK2FK" , "L_Ankle_JNTBC.blender")
        for nc in ["Hip_", "Knee_", "Ankle_"]:
            cmds.connectAttr(f"L_{nc}FK_JNT.rotate", f"L_{nc}JNTBC.color1")
            cmds.connectAttr(f"L_{nc}IK_JNT.rotate", f"L_{nc}JNTBC.color2")
            cmds.connectAttr(f"L_{nc}JNTBC.output", f"L_{nc}JNT.rotate")

    if isRight:
        for i in ["R_Knee_FK_CTRL", "R_Ankle_FK_CTRL", "R_Ankle_IK_CTRL", "R_Leg_PV", "R_FK_Knee_LOC"]:
            cmds.addAttr( i, ln="IK2FK", proxy = "R_Hip_FK_CTRL.IK2FK", keyable = True)
    else:
        for i in ["L_Knee_FK_CTRL", "L_Ankle_FK_CTRL", "L_Ankle_IK_CTRL", "L_Leg_PV", "L_FK_Knee_LOC"]:
            cmds.addAttr( i, ln="IK2FK", proxy = "L_Hip_FK_CTRL.IK2FK", keyable = True)


def action_button(rightRB, armRB):

    '''
    1. Query arm or leg
    2. Query the side
    3. Call arm or leg, passing in the side
    4. Exit
    '''

    isArm = cmds.radioButton(armRB, query=True, select = True)
    isRight = cmds.radioButton(rightRB, query=True, select = True)

    if isArm:
        ArmFunction(isRight=isRight)
        return

    LegFunction(isRight=isRight)

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
#cmds.separator(horizontal=False, h=50)
cmds.radioCollection()
leftRB = cmds.radioButton( label="Left", select=True) #onCommand = Function
rightRB = cmds.radioButton(label="Right") #, onCommand = RightFuncion)
cmds.separator(horizontal=False, style="none", h=10)
#cmds.separator(horizontal=False, h=20)

cmds.separator(horizontal=False, style="none", h=10)
cmds.separator(horizontal=False, style="none", h=10)
cmds.separator(horizontal=False, style="none", h=10)


cmds.separator(horizontal=False, style="none", h=10)
cmds.button(label='Create', command=lambda x:action_button(rightRB, armRB), align='left')

cmds.showWindow()


