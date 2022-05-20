from maya import cmds
import math


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

    cmds.delete("locator1", "locator2", "locator3")

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
    def getVector(p2, p1):
        return [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]

    def getLength(v):
        return math.sqrt(v[0]**2.0 + v[1]**2.0 + v[2]**2.0)

    # All points.
    p1 = cmds.xform(f"{directionString}{hingeRoot}_JNT", q = True, ws = True, t = True)
    p2 = cmds.xform(f"{directionString}{hinge}_JNT", q = True, ws = True, t = True)
    p3 = cmds.xform(f"{directionString}{hingeEnd}_JNT", q = True, ws = True, t = True)

    # All vectors.
    p12 = getVector(p2, p1)
    p23 = getVector(p3, p2)
    p13 = getVector(p3, p1)

    # All lengths.
    p12_m = getLength(p12)
    p23_m = getLength(p23)
    p13_m = getLength(p13)

    # Semi Perimeter and Heron's formula for altitude
    sp = (p12_m + p23_m + p13_m) / 2.0
    altitude = (2 * (math.sqrt((sp * (sp - p12_m) * (sp - p23_m) * (sp - p13_m))))) / p13_m
    angle_radians = math.acos((p12[0] * p13[0] + p12[1] * p13[1] + p12[2] * p13[2]) / (p12_m * p13_m))
    angle_degrees = angle_radians * (180 / math.pi)

    # Distance from p1 to perpendicular height: simple because this is a right triangle.
    missing_side = p12_m * math.cos(angle_radians)

    # Normalize since we will multiply by the p13 vector.
    normalized = missing_side / p13_m
    delta = [x * normalized for x in p13]

    # Add to our original p1 point.
    position = [p1[0] + delta[0], p1[1] + delta[1], p1[2] + delta[2]]
    cmds.spaceLocator(name= "point", p = position)

    # Set PV position directly using the new point to find vector.
    projectionVector = getVector(p2, position)#[p2[0] - position[0], p2[1] - position[1], p2[2] - position[2]]
    projectionVector_m = getLength(projectionVector)#math.sqrt(projectionVector[0]**2.0 + projectionVector[1]**2.0 + projectionVector[2]**2.0)
    distance = 5.0 / projectionVector_m
    projectedVector = [x * distance for x in projectionVector]
    pv = [p2[0] + projectedVector[0], p2[1] + projectedVector[1], p2[2] + projectedVector[2]]
    cmds.spaceLocator(name =f"{directionString}{limb}_PV",p = pv)

    #Set pivot to right location
    obj=f"{directionString}{limb}_PV"
    center=cmds.objectCenter(obj, gl = True)
    print(center)
    cmds.xform(obj, pivots = center)

    cmds.poleVectorConstraint( f"{directionString}{limb}_PV", f"{directionString}{limb}_IK_HDL")

    cmds.delete("point")

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

