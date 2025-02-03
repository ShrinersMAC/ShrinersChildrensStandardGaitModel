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
# Vector/Matrix operations modules

Created on Mon Feb 12 15:49:17 2018
Last Update: 26 Aug, 2024

@author: psaraswat
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

VersionNumber = 'Py3_v1.3'

import numpy as np
import math

def ComputeUnitVecFromPts(Tail, Tip):
    if np.linalg.norm(Tip-Tail) == 0.0 or math.isnan(np.linalg.norm(Tip-Tail)) is True:
        #print('Error: Attempt to divide by zero in determination of unit vector.')
        UnitVector = np.array([0.,0.,0.])
    else:
        UnitVector = (Tip-Tail)/np.linalg.norm(Tip-Tail)
    return UnitVector

def Compute3DAngle(Point1, Point2, Point3):
    UnitVector1 = ComputeUnitVecFromPts(Point2, Point1)
    UnitVector2 = ComputeUnitVecFromPts(Point2, Point3)
    
    Angle = np.arccos(np.dot(UnitVector1, UnitVector2))
    return Angle

def TransformVectorIntoLabCoors(Vector, TransformationMatrix):
    TransformedVector = np.array([0.,0.,0.])
    for i in range(3):
        TransformedVector[i] = Vector[0]*TransformationMatrix[i,0] + Vector[1]*TransformationMatrix[i,1] + Vector[2]*TransformationMatrix[i,2]
    
    return TransformedVector

def TransformPointIntoLabCoors(Point, TransformationMatrix, CoordinateSystemOrigin):
    TransformedVector = TransformVectorIntoLabCoors(Point, TransformationMatrix)
    TransformedPoint = TransformedVector + CoordinateSystemOrigin    

    return TransformedPoint

def TransformVectorIntoMovingCoors(Vector, TransformationMatrix):
    TransformedVector = np.array([0.,0.,0.])
    for i in range(3):
        TransformedVector[i] = Vector[0]*TransformationMatrix[0,i] + Vector[1]*TransformationMatrix[1,i] + Vector[2]*TransformationMatrix[2,i]
        
    return TransformedVector


def TransformPointIntoMovingCoors(Point, TransformationMatrix, Origin):
    
    TranslatedPoint = Point - Origin
    TransformedPoint = TransformVectorIntoMovingCoors(TranslatedPoint, TransformationMatrix)
    
    return TransformedPoint

def TransformAnatCoorSysIntoTechCoors(EAnt, ETech):
    # ea- Vectors to be Transformed
    eax = EAnt[:,0]
    eay = EAnt[:,1]
    eaz = EAnt[:,2]
    
    # et- Transformed Vectors
    etx = TransformVectorIntoMovingCoors(eax,ETech)
    ety = TransformVectorIntoMovingCoors(eay,ETech)
    etz = TransformVectorIntoMovingCoors(eaz,ETech)
    
    EAnatRelTech = np.column_stack((etx,ety,etz))
        
    return EAnatRelTech

def TransformAnatCoorSysFromTechCoors(EAnatRelTech, ETech):
    # ea- Vectors to be Transformed
    eax = EAnatRelTech[:,0]
    eay = EAnatRelTech[:,1]
    eaz = EAnatRelTech[:,2]
    
    # et- Transformed Vectors
    etx = TransformVectorIntoLabCoors(eax,ETech)
    ety = TransformVectorIntoLabCoors(eay,ETech)
    etz = TransformVectorIntoLabCoors(eaz,ETech)
    
    EAnat = np.column_stack((etx,ety,etz))
        
    return EAnat

def EulerAngles_YXZ(EMoving, ERef):
    
    # em- Vectors of Moving Coordinate System
    emx = EMoving[:,0]
    emy = EMoving[:,1]
    emz = EMoving[:,2]
    
    # er- Vectors of Reference Coordinate System
    erx = ERef[:,0]
    ery = ERef[:,1]
    erz = ERef[:,2]
    
    # Initialize Compute Angles in radians 
    AnglesRad = np.array([0.,0.,0.])
    
    # Obiliquity or Ab/Adduction
    AnglesRad[0] = np.arcsin(-np.dot(emz,ery))    
    # Tilt or Flexion/Extension
    #AnglesRad[1] = np.arcsin(np.dot(emz,erx)) / np.cos(AnglesRad[0])
    AnglesRad[1] = np.arctan2(np.dot(emz,erx),np.dot(emz,erz))
    # Int/Ext Rotation
    #AnglesRad[2] = np.arcsin(np.dot(emx,ery)) / np.cos(AnglesRad[0])
    AnglesRad[2] = np.arctan2(np.dot(emx,ery),np.dot(emy,ery))
    
    return AnglesRad

def EulerAngles_ZXY(EMoving, ERef):
    
    # ROWS: em- Vectors of Moving Coordinate System
    emx = EMoving[:,0]
    emy = EMoving[:,1]
    emz = EMoving[:,2]
    
    # COLS: er- Vectors of Reference Coordinate System
    erx = ERef[:,0]
    ery = ERef[:,1]
    erz = ERef[:,2]
    
    # Initialize Compute Angles in radians 
    AnglesRad = np.array([0.,0.,0.])
    
    #alpha = ArcSin(t(2, 3))
    #beta = Atan2(-t(1, 3), t(3, 3))
    #gamma = Atan2(-t(2, 1), t(2, 2))

    # Obiliquity or Ab/Adduction
    AnglesRad[0] = np.arcsin(np.dot(emy,erz))
    # Tilt or Flexion/Extension
    AnglesRad[1] = np.arctan2(-np.dot(emx,erz),np.dot(emz,erz))
    # Int/Ext Rotation
    AnglesRad[2] = np.arctan2(-np.dot(emy,erx),np.dot(emy,ery))
    
    return AnglesRad
	
def EulerAngles_ZYX(EMoving, ERef):
    
    # ROWS: em- Vectors of Moving Coordinate System
    emx = EMoving[:,0]
    emy = EMoving[:,1]
    emz = EMoving[:,2]
    
    # COLS: er- Vectors of Reference Coordinate System
    erx = ERef[:,0]
    ery = ERef[:,1]
    erz = ERef[:,2]
    
    # Initialize Compute Angles in radians 
    AnglesRad = np.array([0.,0.,0.])
    
    #alpha = Atan2(t(2, 3), t(3, 3))
    #beta = ArcSin(-t(1, 3))
    #gamma = Atan2(t(1, 2), t(1, 1))

    # Obiliquity or Ab/Adduction
    AnglesRad[0] = np.arctan2(np.dot(emy,erz),np.dot(emz,erz))
    # Tilt or Flexion/Extension
    AnglesRad[1] = np.arcsin(-np.dot(emx,erz))
    # Int/Ext Rotation
    AnglesRad[2] = np.arctan2(np.dot(emx,ery),np.dot(emx,erx))
    
    return AnglesRad

def AngVelAcc_Euler_YXZ(Angles, Velocity, Acceleration, FirstFrame, LastFrame, framecount):
    AngVel = [[0. for m in range(framecount)] for n in range(3)]
    AngAcc = [[0. for m in range(framecount)] for n in range(3)]    
    
    for FrameNumber in range(FirstFrame-1, LastFrame):
        AngVel[0][FrameNumber] =  Velocity[0][FrameNumber] * np.cos(Angles[1][FrameNumber]) + \
                                  Velocity[2][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.sin(Angles[1][FrameNumber])
        
        AngVel[1][FrameNumber] =  Velocity[1][FrameNumber] + \
                                 -Velocity[2][FrameNumber] * np.sin(Angles[0][FrameNumber])
        
        AngVel[2][FrameNumber] = -Velocity[0][FrameNumber] * np.sin(Angles[1][FrameNumber]) + \
                                  Velocity[2][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.cos(Angles[1][FrameNumber])
                                  
        AngAcc[0][FrameNumber] =  Acceleration[0][FrameNumber] * np.cos(Angles[1][FrameNumber]) +\
                                 -Velocity[0][FrameNumber] * Velocity[1][FrameNumber] * np.sin(Angles[1][FrameNumber]) +\
                                  Acceleration[2][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.sin(Angles[1][FrameNumber]) +\
                                 -Velocity[2][FrameNumber] * Velocity[0][FrameNumber] * np.sin(Angles[0][FrameNumber]) * np.sin(Angles[1][FrameNumber]) +\
                                  Velocity[2][FrameNumber] * Velocity[1][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.cos(Angles[1][FrameNumber])
                                  
        AngAcc[1][FrameNumber] =  Acceleration[1][FrameNumber] + \
                                 -Acceleration[2][FrameNumber] * np.sin(Angles[0][FrameNumber])  + \
                                 -Velocity[2][FrameNumber] * Velocity[0][FrameNumber] * np.cos(Angles[0][FrameNumber])
        
        AngAcc[2][FrameNumber] = -Acceleration[0][FrameNumber] * np.sin(Angles[1][FrameNumber]) + \
                                 -Velocity[0][FrameNumber] * Velocity[1][FrameNumber] * np.cos(Angles[1][FrameNumber]) + \
                                  Acceleration[2][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.cos(Angles[1][FrameNumber]) + \
                                 -Velocity[2][FrameNumber] * Velocity[0][FrameNumber] * np.sin(Angles[0][FrameNumber]) * np.cos(Angles[1][FrameNumber]) + \
                                 -Velocity[2][FrameNumber] * Velocity[1][FrameNumber] * np.cos(Angles[0][FrameNumber]) * np.sin(Angles[1][FrameNumber])
        
    return ([AngVel, AngAcc])

def MassCenter(ProximalPoint, DistalPoint, DistalPercentage):
    
    LongAxisVector = ProximalPoint - DistalPoint
    SegmentLength = np.linalg.norm(LongAxisVector)
    LongAxisUnitVector = LongAxisVector / np.linalg.norm(LongAxisVector)
    
    COM = DistalPoint + DistalPercentage * SegmentLength * LongAxisUnitVector
    
    return COM

def RadiusOfGyration(ProximalPoint, DistalPoint, Percentage1, Percentage2, Percentage3):

    LongAxisVector = ProximalPoint - DistalPoint
    SegmentLength = np.linalg.norm(LongAxisVector)
    
    RadGyr = np.array([0.,0.,0.])
    RadGyr[0] = Percentage1 * SegmentLength
    RadGyr[1] = Percentage2 * SegmentLength
    RadGyr[2] = Percentage3 * SegmentLength
    
    return RadGyr

def Differentiate(YData, FirstFrame, LastFrame, framecount, DeltaTime):
    # Inputs is vector-based data set. 
    # Converts into three single dimensional arrays for differentiation
    # Returns the first and second derivative arrays into vector-based variables
    FirstDerivativeData = [[0. for m in range(framecount)] for n in range(3)]
    SecondDerivativeData = [[0. for m in range(framecount)] for n in range(3)]
    
    for i in range(3):
        for FrameNumber in range(FirstFrame -1 + 3 , LastFrame - 3):
            # Fit Quadratic polynomial in 7 point window
            x = [0, 1*DeltaTime, 2*DeltaTime, 3*DeltaTime, 4*DeltaTime, 5*DeltaTime, 6*DeltaTime]
            y = [ YData[i][FrameNumber-3],YData[i][FrameNumber-2], YData[i][FrameNumber-1], YData[i][FrameNumber], YData[i][FrameNumber+1], YData[i][FrameNumber+2], YData[i][FrameNumber+3] ] 
            
            # Fit fourth order polynomial to the 7 point data window
            coeffs = np.polyfit(x, y, 3)
            ffit_Polynomial = np.poly1d(coeffs)
            FirstDeriv_Polynomial = ffit_Polynomial.deriv()
            SecondDeriv_Polynomial = FirstDeriv_Polynomial.deriv()
            
            # Compute values at midpoint of 7-point window
            FirstDerivativeData[i][FrameNumber] = FirstDeriv_Polynomial(3*DeltaTime)
            SecondDerivativeData[i][FrameNumber] = SecondDeriv_Polynomial(3*DeltaTime)
            
            # Account for Beginning and End Points
            if FrameNumber == FirstFrame -1 + 3:
                FirstDerivativeData[i][FrameNumber-3] = FirstDeriv_Polynomial(0*DeltaTime)
                SecondDerivativeData[i][FrameNumber-3] = SecondDeriv_Polynomial(0*DeltaTime)
                FirstDerivativeData[i][FrameNumber-2] = FirstDeriv_Polynomial(1*DeltaTime)
                SecondDerivativeData[i][FrameNumber-2] = SecondDeriv_Polynomial(1*DeltaTime)
                FirstDerivativeData[i][FrameNumber-1] = FirstDeriv_Polynomial(2*DeltaTime)
                SecondDerivativeData[i][FrameNumber-1] = SecondDeriv_Polynomial(2*DeltaTime)
                #print(x)
                #print(y)
                #print(FirstDeriv_Polynomial(3*DeltaTime))
                #print(SecondDerivativeData[i][FrameNumber])
                
                
            if FrameNumber == LastFrame - 3 - 1:
                FirstDerivativeData[i][FrameNumber+1] = FirstDeriv_Polynomial(4*DeltaTime)
                SecondDerivativeData[i][FrameNumber+1] = SecondDeriv_Polynomial(4*DeltaTime)
                FirstDerivativeData[i][FrameNumber+2] = FirstDeriv_Polynomial(5*DeltaTime)
                SecondDerivativeData[i][FrameNumber+2] = SecondDeriv_Polynomial(5*DeltaTime)
                FirstDerivativeData[i][FrameNumber+3] = FirstDeriv_Polynomial(6*DeltaTime)
                SecondDerivativeData[i][FrameNumber+3] = SecondDeriv_Polynomial(6*DeltaTime)
            
    
    return ([FirstDerivativeData, SecondDerivativeData])

def Smooth1DArray(DataArray,StartFrame,EndFrame,Order,WindowWidth):
    #print DataArray
    DataArraySmoothed = [0. for m in range(len(DataArray))]
    # If WindowWidth is larger than data array size
    if EndFrame - StartFrame + 1 < WindowWidth:
        WindowWidth = EndFrame - StartFrame + 1
    
    # Fit fourth order polynomial to WindowWidth Data
    XWindow = [0. for m in range(WindowWidth)]
    YWindow = [0. for m in range(WindowWidth)]
    for FrameNumber in range(StartFrame - 1 + int(WindowWidth/2), EndFrame - int(WindowWidth/2)):
        for i in range(WindowWidth):
            XWindow[i] = i
            YWindow[i] = DataArray[FrameNumber - int(WindowWidth/2) + i]
        coeffs = np.polyfit(XWindow, YWindow, 3)
        ffit_polynomial = np.poly1d(coeffs)
        DataArraySmoothed[FrameNumber] = ffit_polynomial(int(WindowWidth/2))
        
        # For Beginning of Data Array
        if FrameNumber == StartFrame - 1 + int(WindowWidth/2):
            #print FrameNumber
            #print XWindow
            #print YWindow
            for j in range(int(WindowWidth/2)):
                #print(int(WindowWidth/2) - j - 1, FrameNumber - j - 1)
                DataArraySmoothed[FrameNumber - j - 1] = ffit_polynomial(int(WindowWidth/2) - j - 1)
    
        # For End of Data Array
        if FrameNumber == EndFrame - int(WindowWidth/2) - 1:
            #print FrameNumber
            for j in range(int(WindowWidth/2)):
                #print(int(WindowWidth/2) + j + 1, FrameNumber + j + 1)
                DataArraySmoothed[FrameNumber + j + 1] = ffit_polynomial(int(WindowWidth/2) + j + 1)

    return DataArraySmoothed

def Smooth3DArray(Data3DArray,StartFrame,EndFrame,Order,WindowWidth):
    
    Data3DArraySmoothed = [[0. for m in range(len(Data3DArray[0]))] for n in range(3)]
    Data1DArrayX = [0. for m in range(len(Data3DArray[0]))]
    Data1DArrayY = [0. for m in range(len(Data3DArray[0]))]
    Data1DArrayZ = [0. for m in range(len(Data3DArray[0]))]
    
    # Create 3 1D Arrays
    for i in range(len(Data3DArray[0])):
        Data1DArrayX[i] = Data3DArray[0][i]
        Data1DArrayY[i] = Data3DArray[1][i]
        Data1DArrayZ[i] = Data3DArray[2][i]
    Data1DArrayXSmoothed = Smooth1DArray(Data1DArrayX, StartFrame, EndFrame, Order, WindowWidth)
    Data1DArrayYSmoothed = Smooth1DArray(Data1DArrayY, StartFrame, EndFrame, Order, WindowWidth)
    Data1DArrayZSmoothed = Smooth1DArray(Data1DArrayZ, StartFrame, EndFrame, Order, WindowWidth)
    
    for i in range(len(Data3DArray[0])):
        Data3DArraySmoothed[0][i] = Data1DArrayXSmoothed[i]
        Data3DArraySmoothed[1][i] = Data1DArrayYSmoothed[i]
        Data3DArraySmoothed[2][i] = Data1DArrayZSmoothed[i]
    
    return Data3DArraySmoothed

def Trim3DList(List,StartFrame,EndFrame):
    trimmedList = [[0. for m in range(EndFrame-StartFrame+1)] for n in range(len(List))]
    for i in range(len(List)):
        for j in range(StartFrame-1,EndFrame):
            trimmedList[i][j-StartFrame+1] = List[i][j]        
    return trimmedList

def ComputeMuscleLength(Side,MusclePoints,MuscleSegments,EPelvisAnatDelp,PelvisOrigin,EThighAnat,ThighOrigin,EShankAnat,ShankOrigin,EPatellaAnat,PatellaOrigin,ECalcaneusAnat,CalcaneusOrigin):
    MuscleLength = 0
    MusclePointsLab = []
    for i in range(len(MusclePoints)-1):
        if Side == 'Left':
            MusclePoint1 = MusclePoints[i]
            MusclePoint2 = MusclePoints[i+1]
        if Side == 'Right':
            MusclePoint1 = [MusclePoints[i][0],-MusclePoints[i][1],MusclePoints[i][2]]
            MusclePoint2 = [MusclePoints[i+1][0],-MusclePoints[i+1][1],MusclePoints[i+1][2]]

        # First Point
        if MuscleSegments[i] == 'Pelvis':
            Point1 = TransformPointIntoLabCoors(MusclePoint1,EPelvisAnatDelp,PelvisOrigin)
        if MuscleSegments[i] == 'Thigh':
            Point1 = TransformPointIntoLabCoors(MusclePoint1,EThighAnat,ThighOrigin)
        if MuscleSegments[i] == 'Shank':
            Point1 = TransformPointIntoLabCoors(MusclePoint1,EShankAnat,ShankOrigin)
        if MuscleSegments[i] == 'Patella':
            Point1 = TransformPointIntoLabCoors(MusclePoint1,EPatellaAnat,PatellaOrigin)
        if MuscleSegments[i] == 'Calcaneus':
            Point1 = TransformPointIntoLabCoors(MusclePoint1,ECalcaneusAnat,CalcaneusOrigin)
        # Second Point
        if MuscleSegments[i+1] == 'Pelvis':
            Point2 = TransformPointIntoLabCoors(MusclePoint2,EPelvisAnatDelp,PelvisOrigin)
        if MuscleSegments[i+1] == 'Thigh':
            Point2 = TransformPointIntoLabCoors(MusclePoint2,EThighAnat,ThighOrigin)
        if MuscleSegments[i+1] == 'Shank':
            Point2 = TransformPointIntoLabCoors(MusclePoint2,EShankAnat,ShankOrigin)
        if MuscleSegments[i+1] == 'Patella':
            Point2 = TransformPointIntoLabCoors(MusclePoint2,EPatellaAnat,PatellaOrigin)
        if MuscleSegments[i+1] == 'Calcaneus':
            Point2 = TransformPointIntoLabCoors(MusclePoint2,ECalcaneusAnat,CalcaneusOrigin)
        
        # Add Points to the List
        if i == 0:
            MusclePointsLab.append(Point1)
            MusclePointsLab.append(Point2)
        else:
            MusclePointsLab.append(Point2)
            
        # Compute Distance
        MuscleLength = MuscleLength + np.linalg.norm(Point2-Point1)
  
    return [MuscleLength,MusclePointsLab]

def RotateCSaroundXaxis(InputCS,Angle):
    OutputCS = np.eye(3)
    epx = np.array([InputCS[0][0],InputCS[1][0],InputCS[2][0]])
    epy = np.array([InputCS[0][1],InputCS[1][1],InputCS[2][1]])
    epz = np.array([InputCS[0][2],InputCS[1][2],InputCS[2][2]])
    
    # Rotate CS around Y axis by Angle
    ex = epx
    ey = epy * np.cos(-Angle*np.pi/180) + epz *-np.sin(-Angle*np.pi/180)
    ez = epy * np.sin(-Angle*np.pi/180) + epz * np.cos(-Angle*np.pi/180)
    
    OutputCS = np.column_stack((ex,ey,ez))

    return OutputCS

def RotateCSaroundYaxis(InputCS,Angle):
    OutputCS = np.eye(3)
    epx = np.array([InputCS[0][0],InputCS[1][0],InputCS[2][0]])
    epy = np.array([InputCS[0][1],InputCS[1][1],InputCS[2][1]])
    epz = np.array([InputCS[0][2],InputCS[1][2],InputCS[2][2]])
    
    # Rotate CS around Y axis by Angle
    ex = epx * np.cos(-Angle*np.pi/180) + epz * np.sin(-Angle*np.pi/180)
    ey = epy
    ez = epx *-np.sin(-Angle*np.pi/180) + epz * np.cos(-Angle*np.pi/180)
    
    OutputCS = np.column_stack((ex,ey,ez))

    return OutputCS

def RotateCSaroundZaxis(InputCS,Angle):
    OutputCS = np.eye(3)
    epx = np.array([InputCS[0][0],InputCS[1][0],InputCS[2][0]])
    epy = np.array([InputCS[0][1],InputCS[1][1],InputCS[2][1]])
    epz = np.array([InputCS[0][2],InputCS[1][2],InputCS[2][2]])
    
    # Rotate CS around Y axis by Angle
    ex = epx * np.cos(-Angle*np.pi/180) + epy *-np.sin(-Angle*np.pi/180)
    ey = epx * np.sin(-Angle*np.pi/180) + epy * np.cos(-Angle*np.pi/180)
    ez = epz
    
    OutputCS = np.column_stack((ex,ey,ez))

    return OutputCS