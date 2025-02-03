# -*- coding: utf-8 -*-
"""
<One of the file associated with the Program to compute lower extremity Shrine Gait Model kinematics and kinetics>
Copyright (C) 2023  <Prabhav Saraswat>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
# Gait Model Coordinate Systems for Segment and Joints

Created on Mon Feb 19 15:57:33 2018
Last Update: 26 Aug, 2024

@author: psaraswat
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

VersionNumber = 'Py3_v1.3'

import numpy as np
import Py3_MathModules as math


def TechCS_Trunk_Newington(C7, LCLV, RCLV, LASIS, RASIS, SACR):
                
    # Intialize Matrix and array 
    # If . is not placed after zero, values will be truncated to integers
    ETrunkTech =  np.matrix([[0. for m in range(3)] for n in range(3)])
    PelvicCenterLab = np.array([0.,0.,0.])
    ShouldersCenterLab = np.array([0.,0.,0.])
    
    # Determine Pelvic Coordinate System
    epy = math.ComputeUnitVecFromPts(RASIS, LASIS)
    ed3 = math.ComputeUnitVecFromPts(RASIS, SACR)
    epz = np.cross(epy,ed3)
    epz = epz/np.linalg.norm(epz)
    epx = np.cross(epy,epz)
    
    #Determine Center of the Pelvic Cluster
    d3 = np.linalg.norm(SACR - RASIS)
    beta = np.arccos(np.dot(ed3,epy))
    d2 = d3 * np.sin(beta)
    
    PelvicCenterLab = (RASIS + LASIS)/2 - 0.5 * d2 * epx
    
    # Compute Shoulder Coordinate System
    esy = math.ComputeUnitVecFromPts(RCLV, LCLV)
    ed3 = math.ComputeUnitVecFromPts(RCLV, C7)
    esz = np.cross(esy,ed3)
    esz = esz/np.linalg.norm(esz)
    esx = np.cross(esy,esz)
    
    # Determine Center of Shoulder Cluster
    d3 = np.linalg.norm(C7 - RCLV)
    beta = np.arccos(np.dot(ed3,esy))
    d2 = d3 * np.sin(beta)
    
    ShouldersCenterLab = (RCLV + LCLV)/2 - 0.5 * d2 * esx
    
    # Compute Trunk Coordinate System
    etz = ShouldersCenterLab - PelvicCenterLab

    etz = etz/np.linalg.norm(etz)
    etx = np.cross(esy,etz)
    etx = etx/np.linalg.norm(etx)
    ety = np.cross(etz,etx)
    
    ETrunkTech = np.column_stack((etx,ety,etz))
    
    return([ETrunkTech, PelvicCenterLab, ShouldersCenterLab])
    
    
def TechCS_Pelvis_Newington(LASIS, RASIS, SACR):
    
    epy = math.ComputeUnitVecFromPts(RASIS, LASIS)
    ed3 = math.ComputeUnitVecFromPts(RASIS, SACR)
    epz = np.cross(epy,ed3)
    epz = epz/np.linalg.norm(epz)
    epx = np.cross(epy,epz)            
    
    EPelvisTech = np.column_stack((epx,epy,epz))
    MidASISLab = (LASIS + RASIS) /2
    
    return([EPelvisTech, MidASISLab])

def AnatCS_Pelvis_Delp(LASIS, RASIS, SACR, PelvicTiltOffset):
    MidASISLab = (LASIS + RASIS) /2
    
    ey = math.ComputeUnitVecFromPts(RASIS, LASIS)
    ed3 = math.ComputeUnitVecFromPts(SACR,  MidASISLab)
    ez = np.cross(ed3,ey)
    ez = ez/np.linalg.norm(ez)
    ex = np.cross(ey,ez)            
    
    EPelvisAnat = np.column_stack((ex,ey,ez))
    
    # Rotate CS around Y axis by PelviTiltOffset
    EPelvisAnat = math.RotateCSaroundYaxis(EPelvisAnat,PelvicTiltOffset)
    
    return([EPelvisAnat, MidASISLab])
    
def JointCenterModel_Hip_Newington(Side, MarkerDiameter, ASISdist, ASIStoGTdist, LeftLegLength, RightLegLength, RASIS, LASIS, EPelvisTech, MidASISLab):
    
    #Constants in degrees
    ThetaConst = 28.42
    PelvisTiltConst = 18.0    

    # Convert to radians
    ThetaConstRadians = ThetaConst * np.pi /180
    PelvisTiltConstRadians = PelvisTiltConst * np.pi /180
    
    LongerLegLength = max(LeftLegLength, RightLegLength)
    #estimate ASIStoGTDist based on regression relationship if necessary
    if ASIStoGTdist == 0:
            ASIStoGTdist = 0.12876 * float(LongerLegLength) - 48.56 
    
    C = float(LongerLegLength) * 0.115 - 15.33
        
    #define hip center relative to a neutral (flat) pelvis
    HipInPelvisCoorsTemp = np.array([0.,0.,0.])
    HipInPelvisCoorsTemp[0] = -(float(ASIStoGTdist) + float(MarkerDiameter)/2)
    if Side == 'Right':
        HipInPelvisCoorsTemp[1] = C * np.sin(ThetaConstRadians) - (float(ASISdist)/2) 
    if Side == 'Left':
        HipInPelvisCoorsTemp[1] = -C * np.sin(ThetaConstRadians) + (float(ASISdist)/2) 
    HipInPelvisCoorsTemp[2] = -C * np.cos(ThetaConstRadians)
    
    #rotate to account for mean pelvic tilt of study group
    HipCenterPelvis = np.array([0.,0.,0.])
    HipCenterPelvis[0] = np.cos(PelvisTiltConstRadians) * HipInPelvisCoorsTemp[0] - np.sin(PelvisTiltConstRadians) * HipInPelvisCoorsTemp[2]
    HipCenterPelvis[1] = HipInPelvisCoorsTemp[1]
    HipCenterPelvis[2] = np.sin(PelvisTiltConstRadians) * HipInPelvisCoorsTemp[0] + np.cos(PelvisTiltConstRadians) * HipInPelvisCoorsTemp[2]
    
    #compute hip location relative to lab origin and expressed relative to lab coordinate system
    HipCenterLab = math.TransformPointIntoLabCoors(HipCenterPelvis, EPelvisTech, MidASISLab)
    
    return([HipCenterPelvis, HipCenterLab])
    
    
def JointCenterModel_Hip_Harrington(Side, ASISdist, RASIS, LASIS, SACR, EPelvisTech, MidASISLab):
    
    #PelvicWidth = np.linalg.norm(LASIS-RASIS)
    PelvicWidth = ASISdist
    PelvicDepth = np.linalg.norm((LASIS+RASIS)/2 - SACR)
    
    #define hip center relative to a pelvis coordinate syste (Origin at MidASIS)
    HipCenterPelvis = np.array([0.,0.,0.])
    
    # Single Linear Regression Equations
    HipCenterPelvis[0] = -0.24 * PelvicDepth - 9.9
    if Side == 'Right':
        HipCenterPelvis[1] =  -0.33*PelvicWidth - 7.3
    if Side == 'Left':
        HipCenterPelvis[1] =  +0.33*PelvicWidth + 7.3
    HipCenterPelvis[2] = -0.30*PelvicWidth -10.9
    
    # Two Variable Regression Equations
#    HipCenterPelvis[0] = -0.24 * PelvicDepth - 9.9
#    if Side == 'Right':
#        HipCenterPelvis[1] =  -0.28*PelvicDepth - 0.16*PelvicWidth - 7.9
#    if Side == 'Left':
#        HipCenterPelvis[1] =  +0.28*PelvicDepth + 0.16*PelvicWidth + 7.9
#    HipCenterPelvis[2] = -0.16*PelvicWidth - 0.04*LongerLegLength - 7.1
    
    
    #compute hip location relative to lab origin and expressed relative to lab coordinate system
    HipCenterLab = math.TransformPointIntoLabCoors(HipCenterPelvis, EPelvisTech, MidASISLab)
    
    return([HipCenterPelvis, HipCenterLab])
    
def JointCenterModel_Hip_Harrington2(Side, ASISdist, LeftLegLength, RightLegLength, RASIS, LASIS, SACR, EPelvisTech, MidASISLab):
    
    #PelvicWidth = np.linalg.norm(LASIS-RASIS)
    PelvicWidth = ASISdist
    PelvicDepth = np.linalg.norm((LASIS+RASIS)/2 - SACR)
    LongerLegLength = max(LeftLegLength, RightLegLength)
    
    #define hip center relative to a pelvis coordinate syste (Origin at MidASIS)
    HipCenterPelvis = np.array([0.,0.,0.])
    
    # Single Linear Regression Equations
#    HipCenterPelvis[0] = -0.24 * PelvicDepth - 9.9
#    if Side == 'Right':
#        HipCenterPelvis[1] =  -0.33*PelvicWidth - 7.3
#    if Side == 'Left':
#        HipCenterPelvis[1] =  +0.33*PelvicWidth + 7.3
#    HipCenterPelvis[2] = -0.30*PelvicWidth -10.9
    
    # Two Variable Regression Equations
    HipCenterPelvis[0] = -0.24 * PelvicDepth - 9.9
    if Side == 'Right':
        HipCenterPelvis[1] =  -0.28*PelvicDepth - 0.16*PelvicWidth - 7.9
    if Side == 'Left':
        HipCenterPelvis[1] =  +0.28*PelvicDepth + 0.16*PelvicWidth + 7.9
    HipCenterPelvis[2] = -0.16*PelvicWidth - 0.04*LongerLegLength - 7.1
    
    
    #compute hip location relative to lab origin and expressed relative to lab coordinate system
    HipCenterLab = math.TransformPointIntoLabCoors(HipCenterPelvis, EPelvisTech, MidASISLab)
    
    return([HipCenterPelvis, HipCenterLab])
    
def ComputeVirtualKneeMarker_Newington(Side, MarkerDiameter, UpperKADMarker, LateralKADMarker, LowerKADMarker):
    
    R1 = UpperKADMarker - LowerKADMarker
    R2 = LateralKADMarker - LowerKADMarker
    R3 = UpperKADMarker - LateralKADMarker
    ClusterCenter = (UpperKADMarker + LateralKADMarker + LowerKADMarker)/3
    
    # 'unit vector perpendicular to marker cluster plane pointing from virtual marker to center of cluster triad
    ETA = np.cross(R1,R2)
    ETA = ETA / np.linalg.norm(ETA)
    if Side == 'Left':
        ETA = -ETA

    # distance from Clsuter Center to virtual knee reference point  = (R1+R2+R3)*SQRT(6)/18
    R1Magnitude = np.linalg.norm(R1)
    R2Magnitude = np.linalg.norm(R2)
    R3Magnitude = np.linalg.norm(R3)
    MarkerToCenterVectorMagnitude = (R1Magnitude + R2Magnitude + R3Magnitude) * np.sqrt(6) /18 #0.1360828  

    VirtualKneeMarker = ClusterCenter - MarkerToCenterVectorMagnitude * ETA
    
    #adjust for added thickness (16mm) of commercially-available knee fixture
    E4 = math.ComputeUnitVecFromPts(LateralKADMarker,VirtualKneeMarker)
    VirtualKneeMarker = VirtualKneeMarker + (16 - float(MarkerDiameter)/2)* E4
        
    return VirtualKneeMarker   

def TechCS_Thigh_Newington(Side, HipCenter, ThighMarker, VirtualKneeMarker):
    
    ethz = math.ComputeUnitVecFromPts(VirtualKneeMarker, HipCenter)
    
    #Intermediate Vector from Knee to Thigh Marker
    R1 = math.ComputeUnitVecFromPts(VirtualKneeMarker, ThighMarker)
    
    if Side == 'Right':
        ethx = np.cross(ethz, R1)
        ethx = ethx /np.linalg.norm(ethx)
    if Side == 'Left':
        ethx = np.cross(R1, ethz)
        ethx = ethx /np.linalg.norm(ethx)
    
    ethy = np.cross(ethz, ethx)
    
    EThighTech = np.column_stack((ethx,ethy,ethz))
    
    return EThighTech    

def JointCenterModel_Knee_Newington(Side, MarkerDiameter, KneeWidth, VirtualKneeMarker, LateralKADMarker):
    
    E1= math.ComputeUnitVecFromPts(LateralKADMarker, VirtualKneeMarker)
    KneeCenter = VirtualKneeMarker + (float(KneeWidth)/2 + float(MarkerDiameter)/2) * E1 
    
    return KneeCenter        

def TechCS_Shank_Newington(Side, KneeCenter, TibialMarker, LateralAnkle):
    
    esz = math.ComputeUnitVecFromPts(LateralAnkle, KneeCenter)
    R1 = math.ComputeUnitVecFromPts(LateralAnkle, TibialMarker)
    
    if Side == 'Right':
        esx = np.cross(esz, R1)
    if Side == 'Left':
        esx = np.cross(R1, esz)
    esx = esx /np.linalg.norm(esx)
    esy = np.cross(esz, esx)
    
    EShankTech = np.column_stack((esx,esy,esz))
    
    return EShankTech

def JointCenterModel_Ankle_Newington(Side, MarkerDiameter, AnkleWidth, LateralAnkle, MedialAnkle):
    
    E1 = math.ComputeUnitVecFromPts(LateralAnkle, MedialAnkle)
    AnkleCenterLab = LateralAnkle + (float(AnkleWidth)/2 + float(MarkerDiameter)/2) * E1
    
    return AnkleCenterLab

def ComputeVirtualHeelMarkerLab(PlantigradeCheck, SujectShodCheck, SoleThickness ,AnkleCenterLab, ToeMarker, HeelMarker):

    VirtualHeelMarkerLab = np.array([0.,0.,0.])
    if PlantigradeCheck == '1':
        VirtualHeelMarkerLab[0] = AnkleCenterLab[0]
        VirtualHeelMarkerLab[1] = AnkleCenterLab[1]
        VirtualHeelMarkerLab[2] = ToeMarker[2]
        if SujectShodCheck == '1':
            VirtualHeelMarkerLab[2] = VirtualHeelMarkerLab[2] + float(SoleThickness)
            #print('Shod')
        #print(' plantigrade')
    if PlantigradeCheck == '0':
       # establish heel reference point:  adjust location of heel reference such that it provides the same sagittal result,
       # but is aligned with the ankle center with respect to the transverse orientation of the foot.
       # that is, project ankle center into a reference plane formed by the heel-toe vector and y-axis of lab.
       # this projected ankle center becomes the virtual heel marker. 
       
       #compute a temporary foot coor system that contains the reference plane
       ex = math.ComputeUnitVecFromPts(HeelMarker, ToeMarker)
       LabY = np.array([0.,1.,0.]) # Lab Y axis
       ez = np.cross(ex,LabY)
       ez = ez/ np.linalg.norm(ez)
       ey = np.cross(ez,ex)
       ey = ey/ np.linalg.norm(ey)
       Etemp = np.column_stack((ex,ey,ez))
       
       #Compute Virtual Heel by Transforming ankle center into this temporaray coordinate system
       VirtualHeelMarkerTemp = math.TransformPointIntoMovingCoors(AnkleCenterLab, Etemp, HeelMarker)
       VirtualHeelMarkerTemp[2] =0
       if SujectShodCheck == '1':
           VirtualHeelMarkerTemp[2] = float(SoleThickness)
           #print('Shod')
       #print(' Nonplantigrade')
       #Transform VirtualHeel Marker back to Lab Coordinate system
       VirtualHeelMarkerLab = math.TransformPointIntoLabCoors(VirtualHeelMarkerTemp, Etemp, HeelMarker)
        
    return VirtualHeelMarkerLab

def TechCS_Foot_Newington(Side, KneeCenterLab, AnkleCenterLab, ToeMarker):
    
    eztemp = math.ComputeUnitVecFromPts(AnkleCenterLab, KneeCenterLab)
    ex = math.ComputeUnitVecFromPts(AnkleCenterLab, ToeMarker)
    ey = np.cross(eztemp,ex)
    ey = ey/ np.linalg.norm(ey)
    ez = np.cross(ex,ey)
    ez = ez/ np.linalg.norm(ez)
    
    EFootTech = np.column_stack((ex,ey,ez))
    
    return EFootTech

def AnatCS_Thigh_Newington(Side, HipCenterLab, VirtualKneeMarkerLab, KneeCenterLab):
    
    ez = math.ComputeUnitVecFromPts(KneeCenterLab, HipCenterLab)
    R1 = math.ComputeUnitVecFromPts(KneeCenterLab, VirtualKneeMarkerLab)
    
    if Side == 'Left':
        ex = np.cross(R1, ez)
    if Side == 'Right':
        ex = np.cross(ez, R1)
    
    ex = ex/ np.linalg.norm(ex)
    ey = np.cross(ez, ex)
    
    EThighAnat = np.column_stack((ex,ey,ez))
    
    return EThighAnat

def AnatCS_Thigh_Delp(Side, HipCenterLab, KneeMarkerLab, KneeCenterLab, ThighRotation):
    
    etz = math.ComputeUnitVecFromPts(KneeCenterLab, HipCenterLab)
    R1 = math.ComputeUnitVecFromPts(KneeCenterLab, KneeMarkerLab)
    
    if Side == 'Left':
        etx = np.cross(R1, etz)
    if Side == 'Right':
        etx = np.cross(etz, R1)
    
    etx = etx/ np.linalg.norm(etx)
    ety = np.cross(etz, etx)
    
    # Rotate CS around Z axis by ThighRotation
    ThighRotationValue = float(ThighRotation.split(' ')[0])
    if ThighRotation.split(' ')[1] == 'Ext':
        ThighRotationDirection = +1
    else:
        ThighRotationDirection = -1
    
    if Side == 'Left':
        angle = -ThighRotationDirection * ThighRotationValue
    if Side == 'Right':
        angle =  ThighRotationDirection * ThighRotationValue
    
    
    ex = etx * np.cos(angle*np.pi/180) + ety * -np.sin(angle*np.pi/180)
    ey = etx * np.sin(angle*np.pi/180) + ety *  np.cos(angle*np.pi/180)
    ez = etz 
    ############################################
    
    EThighAnat = np.column_stack((ex,ey,ez))
    
    return EThighAnat

def AnatCS_Shank_Proximal_Newington(Side, KneeCenterLab, VirtualKneeMarkerLab, AnkleCenterLab):
    
    ez = math.ComputeUnitVecFromPts(AnkleCenterLab,KneeCenterLab)
    R1 = math.ComputeUnitVecFromPts(KneeCenterLab, VirtualKneeMarkerLab)
    
    if Side == 'Left':
        ex = np.cross(R1, ez)
    if Side == 'Right':
        ex = np.cross(ez, R1)
    
    ex = ex/ np.linalg.norm(ex)
    ey = np.cross(ez,ex) 
    
    EShankProximalAnat = np.column_stack((ex,ey,ez))
    
    return EShankProximalAnat

def AnatCS_Shank_Distal_VCM(Side, KneeCenterLab, AnkleCenterLab, LateralAnkleMarker):
    
    ez = math.ComputeUnitVecFromPts(AnkleCenterLab,KneeCenterLab)
    
    if Side == 'Left':
        R1 = math.ComputeUnitVecFromPts(AnkleCenterLab, LateralAnkleMarker)
    if Side == 'Right':
        R1 = math.ComputeUnitVecFromPts(LateralAnkleMarker, AnkleCenterLab)
    
    ex = np.cross(R1, ez)
    ex = ex/ np.linalg.norm(ex)
    ey = np.cross(ez,ex) 
    
    EShankDistalAnat = np.column_stack((ex,ey,ez))
    
    return EShankDistalAnat

def AnatCS_Shank_Delp(Side, KneeCenterLab, AnkleCenterLab, LateralAnkleMarker,ShankRotation):
    
    esz = math.ComputeUnitVecFromPts(AnkleCenterLab,KneeCenterLab)
    
    if Side == 'Left':
        R1 = math.ComputeUnitVecFromPts(AnkleCenterLab, LateralAnkleMarker)
    if Side == 'Right':
        R1 = math.ComputeUnitVecFromPts(LateralAnkleMarker, AnkleCenterLab)
    
    esx = np.cross(R1, esz)
    esx = esx/ np.linalg.norm(esx)
    esy = np.cross(esz,esx) 
    
    # Rotate CS around Z axis by ShankRotation
    ShankRotationValue = float(ShankRotation.split(' ')[0])
    if ShankRotation.split(' ')[1] == 'Ext':
        ShankRotationDirection = +1
    else:
        ShankRotationDirection = -1
    
    if Side == 'Left':
        angle = -ShankRotationDirection * ShankRotationValue
    if Side == 'Right':
        angle =  ShankRotationDirection * ShankRotationValue
    
    
    ex = esx * np.cos(angle*np.pi/180) + esy * -np.sin(angle*np.pi/180)
    ey = esx * np.sin(angle*np.pi/180) + esy *  np.cos(angle*np.pi/180)
    ez = esz 
    ############################################
    
    EShankDistalAnat = np.column_stack((ex,ey,ez))
    
    return EShankDistalAnat
 
def AnatCS_Foot_Newington(Side, LateralAnkleMarker, AnkleCenterLab, ToeMarker, VirtualHeelMarkerLab):
    
    ex = math.ComputeUnitVecFromPts(VirtualHeelMarkerLab, ToeMarker)
    
    if Side == 'Left':
        R1= math.ComputeUnitVecFromPts(AnkleCenterLab, LateralAnkleMarker)
    if Side == 'Right':
        R1= math.ComputeUnitVecFromPts(LateralAnkleMarker, AnkleCenterLab)
    
    ez = np.cross(ex, R1)
    ez = ez/ np.linalg.norm(ez)
    ey = np.cross(ez,ex)
    
    EFootAnat = np.column_stack((ex,ey,ez))
    
    return EFootAnat

def AnatCS_Foot_ShrineGaitModel(Side, KneeCenterLab, AnkleCenterLab, ToeMarker, VirtualHeelMarkerLab):
    
    ex = math.ComputeUnitVecFromPts(VirtualHeelMarkerLab, ToeMarker)
    
    eztemp = math.ComputeUnitVecFromPts(AnkleCenterLab, KneeCenterLab)
    
    ey = np.cross(eztemp,ex)
    ey = ey/ np.linalg.norm(ey)
    ez = np.cross(ex,ey)
    ez = ez/ np.linalg.norm(ez)
    
    EFootAnat = np.column_stack((ex,ey,ez))
    
    return EFootAnat

def Compute_TibialTorsion(Side, EShankProximalAnat, LateralAnkleMarker, MedialAnkleMarker): 
    
    if Side == 'Left':
        AnkleAxis = math.ComputeUnitVecFromPts(MedialAnkleMarker, LateralAnkleMarker)
    if Side == 'Right':
        AnkleAxis = math.ComputeUnitVecFromPts(LateralAnkleMarker, MedialAnkleMarker)
    
    # transform ankle axis into shank coordinate system
    AnkleAxisTransformed = math.TransformVectorIntoMovingCoors(AnkleAxis, EShankProximalAnat)

    # determine unit vector in the xy plane of the shank coordinate system
    AnkleAxisTransformed[2] = 0
    AnkleAxisTransformed = AnkleAxisTransformed / np.linalg.norm(AnkleAxisTransformed)
    
    # determine angle between transformed ankle axis and the y-axis of the proximal shank coordinate system
    if Side == 'Left':
        TibialTorsion = -np.arcsin(AnkleAxisTransformed[0]) * 180 / np.pi
    if Side == 'Right':
        TibialTorsion = np.arcsin(AnkleAxisTransformed[0]) * 180 / np.pi
    
    return TibialTorsion

def Compute_ThighRotation(Side, EPelvisAnat, LateralKneeeMarker, KneeCenter): 
    
    if Side == 'Left':
        KneeAxis = math.ComputeUnitVecFromPts(KneeCenter, LateralKneeeMarker)
    if Side == 'Right':
        KneeAxis = math.ComputeUnitVecFromPts(LateralKneeeMarker, KneeCenter)
    
    # transform ankle axis into shank coordinate system
    KneeAxisTransformed = math.TransformVectorIntoMovingCoors(KneeAxis, EPelvisAnat)

    # determine unit vector in the xy plane of the shank coordinate system
    KneeAxisTransformed[2] = 0
    KneeAxisTransformed = KneeAxisTransformed / np.linalg.norm(KneeAxisTransformed)
    
    # determine angle between transformed ankle axis and the y-axis of the proximal shank coordinate system
    if Side == 'Left':
        ThighRotation = -np.arcsin(KneeAxisTransformed[0]) * 180 / np.pi
    if Side == 'Right':
        ThighRotation = np.arcsin(KneeAxisTransformed[0]) * 180 / np.pi
    
    return ThighRotation

def TechCS_Hindfoot_mSHCG(Side, LateralCalcaneusMarker, MedialCalcaneusMarker, HeelMarker):
    
    CCAL = (LateralCalcaneusMarker + MedialCalcaneusMarker) /2 
    ex = math.ComputeUnitVecFromPts(HeelMarker, CCAL)
    
    if Side == 'Left':
        R1 = math.ComputeUnitVecFromPts(MedialCalcaneusMarker, LateralCalcaneusMarker)
    if Side == 'Right':
        R1 = math.ComputeUnitVecFromPts(LateralCalcaneusMarker, MedialCalcaneusMarker)
    
    ez = np.cross(ex,R1)
    ez = ez/ np.linalg.norm(ez)
    ey = np.cross(ez,ex)
    
    EHindfootTech = np.column_stack((ex,ey,ez))
    
    return EHindfootTech

def TechCS_Forefoot_mSHCG(Side, MT1B, MT1H, MT5H):
    
    ex = math.ComputeUnitVecFromPts(MT1B, MT1H)
    
    if Side == 'Left':
        R1 = math.ComputeUnitVecFromPts(MT1H, MT5H)
    if Side == 'Right':
        R1 = math.ComputeUnitVecFromPts(MT5H, MT1H)
    
    ez = np.cross(ex,R1)
    ez = ez/ np.linalg.norm(ez)
    ey = np.cross(ez,ex)
    
    EForefootTech = np.column_stack((ex,ey,ez))
    return EForefootTech

def TechCS_Hallux_mSHCG(Side, HLX, MTP1, TOE):
    
    ex = math.ComputeUnitVecFromPts(MTP1, HLX)
    
    if Side == 'Left':
        R1 = math.ComputeUnitVecFromPts(MTP1, TOE)
    if Side =='Right':
        R1 = math.ComputeUnitVecFromPts(TOE, MTP1)
    
    ez = np.cross(ex,R1)
    ez = ez/ np.linalg.norm(ez)
    ey = np.cross(ez,ex)
    
    EHalluxTech = np.column_stack((ex,ey,ez))
    
    return EHalluxTech        
    
def AnatCS_Hindfoot_mSHCG(Side, LCAL, MCAL, HEEL, CALPT, 
                          HindfootVarus, CalcanealPitch, HindfootProgression, HindFootValgusIsNegative):

    # Create hindfoot CS reflecting the A/P (x) hindfoot orientation and plantar surface
    CCAL = (LCAL + MCAL) /2 
    HindfootProgressionVector = math.ComputeUnitVecFromPts(HEEL, CCAL)
    ProjectedHindfootProgressionVector = np.array([HindfootProgressionVector[0],HindfootProgressionVector[1],0.])
    
    eSagittalx = ProjectedHindfootProgressionVector/ np.linalg.norm(ProjectedHindfootProgressionVector)
    R1 = np.array([0.,0.,1.])
    eSagittaly = np.cross(R1,eSagittalx)
    eSagittaly = eSagittaly/ np.linalg.norm(eSagittaly)
    eSagittalz = np.cross(eSagittalx,eSagittaly)
    
    EHindfootSagittal = np.column_stack((eSagittalx,eSagittaly,eSagittalz))
    EHindfootSagittal_Origin = np.array([HEEL[0],HEEL[1],0])
    
    # Compute Hindfoot Angles
    if HindfootProgression == '':
        HindfootProgressionAngle = np.arctan2(HindfootProgressionVector[1],HindfootProgressionVector[0])
    else:
        if Side == 'Left':
            HindfootProgressionAngle = -(np.pi/180) * float(HindfootProgression)
        else:
            HindfootProgressionAngle = (np.pi/180) * float(HindfootProgression)
    
    # If Calcaneal Pitch is entered, then do not use CALPT marker
    if CalcanealPitch == '':
        # Compute projection of CALPT on HindfootSagittal Plane
        CALPT_EHindfootSagittal = math.TransformPointIntoMovingCoors(CALPT, EHindfootSagittal, EHindfootSagittal_Origin)
        HindfootInclineAngle = np.arctan(CALPT_EHindfootSagittal[2]/CALPT_EHindfootSagittal[0]) * 180 / np.pi
        # Use Regression equation to estimate actual cacaneal pitch

        # Previous equation with 10-20 subjects
        #HindfootPitchAngle = 0.9826* HindfootInclineAngle - 18.87
        
        # Equations with larger sample size
        if HindfootInclineAngle == 0: # If CALPT marker is absent, set calcaneal pitch to zero.
            HindfootPitchAngle = 0.
        else:
            HindfootPitchAngle = 0.776* HindfootInclineAngle - 11.6
        
        
        # Convert to radians
        HindfootPitchAngle = -HindfootPitchAngle * np.pi/180
    else:
        # Positive Rotation is negative inclination
        HindfootPitchAngle = -float(CalcanealPitch) *np.pi/ 180
     
    # Positive is Valgus    
    if Side == 'Left':
        if HindFootValgusIsNegative == False:
            HindfootVarusAngle = float(HindfootVarus) *np.pi/ 180
        else:
            HindfootVarusAngle = -float(HindfootVarus) *np.pi/ 180
    if Side =='Right':
        if HindFootValgusIsNegative == False:
            HindfootVarusAngle = -float(HindfootVarus) *np.pi/ 180
        else:
            HindfootVarusAngle = float(HindfootVarus) *np.pi/ 180
            
    # Final Coordinate System is defined by Rotation/Flexion/Abduction Sequence [Rzyx]
    # alpha = Rot(x) = HindfootVarusAngle, beta = Rot(y) = HindfootPitchAngle, gamma = Rot(z) = HindfootProgressionAngle
    alpha = HindfootVarusAngle
    beta  = HindfootPitchAngle
    gamma = HindfootProgressionAngle
    #print alpha*180/np.pi, beta*180/np.pi, gamma*180/np.pi
    
    # ZYX sequence
    ex = np.array([np.cos(beta)*np.cos(gamma), np.cos(beta)*np.sin(gamma), -np.sin(beta)])
    ey = np.array([np.sin(alpha)*np.sin(beta)*np.cos(gamma) - np.cos(alpha)*np.sin(gamma), 
                   np.sin(alpha)*np.sin(beta)*np.sin(gamma) + np.cos(alpha)*np.cos(gamma), np.sin(alpha)*np.cos(beta)])
    ez = np.array([np.sin(alpha)*np.sin(gamma) + np.cos(alpha)*np.sin(beta)*np.cos(gamma),
                   np.cos(alpha)*np.sin(beta)*np.sin(gamma) - np.sin(alpha)*np.cos(gamma), np.cos(alpha)*np.cos(beta)])
    
    # YXZ sequence [https://en.wikipedia.org/wiki/Euler_angles]
#    ex = np.array([np.cos(beta)*np.cos(gamma) + np.sin(beta)*np.sin(alpha)*np.sin(gamma), np.cos(alpha)*np.sin(gamma), 
#                   np.cos(beta)*np.sin(alpha)*np.sin(gamma) - np.cos(gamma)*np.sin(beta)])
#    ey = np.array([np.cos(gamma)*np.sin(beta)*np.sin(alpha) - np.cos(beta)*np.sin(gamma), np.cos(alpha)*np.cos(gamma),
#                   np.cos(beta)*np.cos(gamma)*np.sin(alpha) + np.sin(beta)*np.sin(gamma)])
#    ez = np.array([np.cos(alpha)*np.sin(beta), -np.sin(alpha), np.cos(beta)*np.cos(alpha)])
    
    EHindfootAnat = np.column_stack([ex,ey,ez])

    #print Side, 'Hindfoot'
    #print EHindfootAnat
    
    return EHindfootAnat

def AnatCS_Forefoot_mSHCG(Side, MT23B, MT23H, MT1BM, MT1HM,
                          FirstMetatarsalPitch):
    
    # Sagittal Plane
    ForefootProgressionVector = MT23H - MT23B
    ProjectedForefootProgressionVector = np.array([ForefootProgressionVector[0],ForefootProgressionVector[1],0.])
    
    eSagittalx = ProjectedForefootProgressionVector/ np.linalg.norm(ProjectedForefootProgressionVector)
    R1 = np.array([0.,0.,1.])
    eSagittaly = np.cross(R1,eSagittalx)
    eSagittaly = eSagittaly/ np.linalg.norm(eSagittaly)
    eSagittalz = np.cross(eSagittalx,eSagittaly)
    
    EForefootSagittal = np.column_stack((eSagittalx,eSagittaly,eSagittalz))
    #EForefootSagittal_Origin = np.array([0.,0.,0.])
    
    # If FirstMetatarsal Pitch is entered, then do not use markers
    if FirstMetatarsalPitch == '':
        ForefootPitchVectorLab = MT1HM - MT1BM
        ForefootPitchVectorEForefootSagittal = math.TransformVectorIntoMovingCoors(ForefootPitchVectorLab,EForefootSagittal)
        ProjectedForefootPitchVectorEForefootSagittal = np.array([ForefootPitchVectorEForefootSagittal[0],0,ForefootPitchVectorEForefootSagittal[2]])
        ex = math.TransformVectorIntoLabCoors(ProjectedForefootPitchVectorEForefootSagittal, EForefootSagittal)
    else:
        # Rotate by defined pitch angle around y-axis
        # Use rodrigues formula
        ForefootPitchAngle = float(FirstMetatarsalPitch) * np.pi/ 180
        ex = eSagittalx* np.cos(ForefootPitchAngle) + \
            np.cross(eSagittaly,eSagittalx)* np.sin(ForefootPitchAngle) + \
            np.dot(eSagittaly,eSagittalx) * eSagittaly *(1-np.cos(ForefootPitchAngle))
    
    
    
    ex = ex/ np.linalg.norm(ex)
    R1 = np.array([0.,0.,1.]) 
    ey = np.cross(R1,ex)
    ey = ey/ np.linalg.norm(ey)
    ez = np.cross(ex,ey)
    
    
    if Side =='Left':
        # For Left Inwards in negative rotation about Z
        ForefootProgressionAngle = -np.arctan2(ForefootProgressionVector[1],ForefootProgressionVector[0])
    if Side =='Right':
        ForefootProgressionAngle = np.arctan2(ForefootProgressionVector[1],ForefootProgressionVector[0])
    
    ForefootPitchAngle = np.arctan2(ex[2],ex[0])
    EForefootAnat = np.column_stack((ex,ey,ez))
    
    #print Side, 'Forefoot'
    #print EForefootAnat
    
    return EForefootAnat
