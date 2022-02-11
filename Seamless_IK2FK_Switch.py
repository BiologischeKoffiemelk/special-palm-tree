from maya import cmds

def Snap():
#check if selected is in which network /is selected part of arm network or leg network
#if in arm network, run arm part
#if in leg network, run leg part.

#raise error

    for object in cmds.ls(sl=1):
        network_connection = cmds.listConnections(object, source=False, destination=True, type='network')
        print(network_connection)
        if not network_connection:
            continue
        if network_connection[0] in  ["R_FK_Arm_Network", "R_IK_Arm_Network", "L_FK_Arm_Network","L_IK_Arm_Network"]:

            key = cmds.currentTime(query=True) - 1

            ctrlname = cmds.ls( selection=True )[0]
            if ctrlname[:2]=="R_": #if selected control has "R_" run right side
                side = "R_"
            else:
                side = "L_"

            switch = cmds.getAttr(f"{side}Shoulder_FK_CTRL.IK2FK")
            if switch == 0:
                #match FK to IK
                cmds.matchTransform(f"{side}Shoulder_FK_CTRL", f"{side}Shoulder_IK_JNT")
                cmds.matchTransform(f"{side}Elbow_FK_CTRL", f"{side}Elbow_IK_JNT")
                cmds.matchTransform(f"{side}Wrist_FK_CTRL", f"{side}Wrist_IK_JNT")
                cmds.matchTransform(f"{side}FK_Elbow_LOC", f"{side}Arm_PV")

            else:# switch == 1:
                #match IK to FK
                cmds.matchTransform(f"{side}Wrist_IK_CTRL", f"{side}Wrist_FK_JNT")
                cmds.matchTransform(f"{side}Arm_PV", f"{side}FK_Elbow_LOC")


            #Set keyframes on the right frames
            IK_arm = cmds.listConnections(f"{side}IK_Arm_Network")
            cmds.select(IK_arm)
            cmds.setKeyframe()
            cmds.setKeyframe(time = key)

            FK_arm = cmds.listConnections(f"{side}FK_Arm_Network")
            cmds.select(FK_arm)
            cmds.setKeyframe()
            cmds.setKeyframe(time = key)


            #Set keyframes on the right attr value
            if cmds.getAttr(f"{side}Shoulder_FK_CTRL.IK2FK") == 0:
                cmds.setAttr(f"{side}Shoulder_FK_CTRL.IK2FK", 1)
                cmds.setKeyframe()
                print('A')
            else:
                cmds.setAttr(f"{side}Shoulder_FK_CTRL.IK2FK", 0)
                cmds.setKeyframe()
                print('B')

        else: #LEGS

            key = cmds.currentTime(query=True) - 1

            ctrlname = cmds.ls( selection=True )[0]
            if ctrlname[:2]=="R_": #if selected control has "R_" run right side
                side = "R_"
            else:
                side = "L_"

            switch = cmds.getAttr(f"{side}Hip_FK_CTRL.IK2FK")
            if switch == 0:
                #match FK to IK
                cmds.matchTransform(f"{side}Hip_FK_CTRL", f"{side}Hip_IK_JNT")
                cmds.matchTransform(f"{side}Knee_FK_CTRL", f"{side}Knee_IK_JNT")
                cmds.matchTransform(f"{side}Ankle_FK_CTRL", f"{side}Ankle_IK_JNT")
                cmds.matchTransform(f"{side}FK_Knee_LOC", f"{side}Leg_PV")

            else:# switch == 1:
                #match IK to FK
                cmds.matchTransform(f"{side}Ankle_IK_CTRL", f"{side}Ankle_FK_JNT")
                cmds.matchTransform(f"{side}Leg_PV", f"{side}FK_Knee_LOC")


            #Set keyframes on the right frames
            IK_arm = cmds.listConnections(f"{side}IK_Leg_Network")
            cmds.select(IK_arm)
            cmds.setKeyframe()
            cmds.setKeyframe(time = key)

            FK_arm = cmds.listConnections(f"{side}FK_Leg_Network")
            cmds.select(FK_arm)
            cmds.setKeyframe()
            cmds.setKeyframe(time = key)


            #Set keyframes on the right attr value
            if cmds.getAttr(f"{side}Hip_FK_CTRL.IK2FK") == 0:
                cmds.setAttr(f"{side}Hip_FK_CTRL.IK2FK", 1)
                cmds.setKeyframe()
                print('A')
            else:
                cmds.setAttr(f"{side}Hip_FK_CTRL.IK2FK", 0)
                cmds.setKeyframe()
                print('B')

Snap()
