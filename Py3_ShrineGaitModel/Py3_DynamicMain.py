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
# Dynamic model computes kinematics and kinetics

Created on Mon Mar 19 12:16:37 2018
Last Update: 26 Aug, 2024

@author: psaraswat
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
VersionNumber = 'Py3_v1.3'

import numpy as np
import sys
    
#import Vicon Nexus Subroutines
from viconnexusapi import ViconNexus
vicon = ViconNexus.ViconNexus()

#import Common Vector/Matrix Operations Modules
import Py3_MathModules as math
import Py3_GaitModules as gait


SubjectName = vicon.GetSubjectNames()[0]
FilePath, FileName = vicon.GetTrialName()
StartFrame, EndFrame = vicon.GetTrialRegionOfInterest()
MarkerFrameRate = vicon.GetFrameRate()

                   
# First Argument is the command name, second argument is the testing condition
DefaultTestingCondition = 'BF'
TestingCondition = DefaultTestingCondition
if len(sys.argv) > 1:
    TestingCondition = sys.argv[1]

#StaticDataFileName = FilePath + 'Static_BF_' + SubjectName + '.py'
# Condition- Barefoot (BF) string read as Script Argument
StaticDataFileName = FilePath + 'Static_' + TestingCondition + '_' + SubjectName + '.py'


class Dynamic_Main():
    def __init__(self):

        # =============================================================================
        #       Create ASIS Markers if Pelfix Option was used      
        # =============================================================================
                
        # Function to extract markerdata into an array and check if data exists
        def MarkerArrayCheck(Subject, MarkerName):
            # Check if marker exists at all
            if vicon.HasTrajectory(Subject,MarkerName) is True:
                MarkerDataX, MarkerDataY, MarkerDataZ, MarkerDataExists = vicon.GetTrajectory(Subject, MarkerName)   
            else:
                framecount = vicon.GetFrameCount()
                MarkerDataX= [0 for m in range(framecount)] 
                MarkerDataY= [0 for m in range(framecount)] 
                MarkerDataZ= [0 for m in range(framecount)] 
                MarkerDataExists = [False]*framecount
            return MarkerDataX, MarkerDataY, MarkerDataZ, MarkerDataExists
        
        exec(open(StaticDataFileName).read())
        #execfile(UserPreferencesFileName)
        
        # Compute ASIS Markers if Pelfix Option is Used
        if not self.valuePelvicFixCheck == '0': # Pelfix Option is Used
            
            if self.valuePelvicFixCheck == '1': # Iliac Opton
                LeftIliacMarkerX, LeftIliacMarkerY, LeftIliacMarkerZ, LeftIliacMarkerExists = MarkerArrayCheck(SubjectName, self.LeftIliacMarkerName)
                RightIliacMarkerX, RightIliacMarkerY, RightIliacMarkerZ, RightIliacMarkerExists = MarkerArrayCheck(SubjectName, self.RightIliacMarkerName)
                try:
                    SacralMarkerX, SacralMarkerY, SacralMarkerZ, SacralMarkerExists = MarkerArrayCheck(SubjectName, self.SacralMarkerName)
                except:
                    LeftPSISMarkerX, LeftPSISMarkerY, LeftPSISMarkerZ, LeftPSISMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPSISMarkerName)
                    RightPSISMarkerX, RightPSISMarkerY, RightPSISMarkerZ, RightPSISMarkerExists = MarkerArrayCheck(SubjectName, self.RightPSISMarkerName)
                    SacralMarkerX = (LeftPSISMarkerX + RightPSISMarkerX) / 2
                    SacralMarkerY = (LeftPSISMarkerY + RightPSISMarkerY) / 2
                    SacralMarkerZ = (LeftPSISMarkerZ + RightPSISMarkerZ) / 2
            
            if self.valuePelvicFixCheck == '2': # Triad Opton
                # For Sacral Triad Case, delete Sacral Marker Name
                # Explanation: When Sacral marker is used and exists in the UserPreferences, then 
                # Sacral Marker Name is deleted to push the code towards using PSIS markers.
                try:
                    del self.SacralMarkerName
                except:
                    pass
                LeftPSISMarkerX, LeftPSISMarkerY, LeftPSISMarkerZ, LeftPSISMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPSISMarkerName)
                RightPSISMarkerX, RightPSISMarkerY, RightPSISMarkerZ, RightPSISMarkerExists = MarkerArrayCheck(SubjectName, self.RightPSISMarkerName)
                SacralTriadMarkerX, SacralTriadMarkerY, SacralTriadMarkerZ, SacralTriadMarkerExists = MarkerArrayCheck(SubjectName, self.SacralTriadMarkerName)
            
            #Compute ASIS for each frame            
            framecount = vicon.GetFrameCount()
            arrayLASISMarkerX= [0 for m in range(framecount)] 
            arrayLASISMarkerY= [0 for m in range(framecount)] 
            arrayLASISMarkerZ= [0 for m in range(framecount)] 
            arrayRASISMarkerX= [0 for m in range(framecount)] 
            arrayRASISMarkerY= [0 for m in range(framecount)] 
            arrayRASISMarkerZ= [0 for m in range(framecount)] 
            exists = [True]*framecount
            
            for FrameNumber in range(StartFrame-1,EndFrame):
                # Compute Pelvis Tech Coordinates
                if self.valuePelvicFixCheck == '1':
                    # Pelvis Technical coordinate system based on LILC, RILC, SACR
                    LeftIliacMarker = np.array([LeftIliacMarkerX[FrameNumber], LeftIliacMarkerY[FrameNumber], LeftIliacMarkerZ[FrameNumber]])
                    RightIliacMarker = np.array([RightIliacMarkerX[FrameNumber], RightIliacMarkerY[FrameNumber], RightIliacMarkerZ[FrameNumber]])
                    SacralMarker = np.array([SacralMarkerX[FrameNumber], SacralMarkerY[FrameNumber], SacralMarkerZ[FrameNumber]])
                    [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftIliacMarker, RightIliacMarker, SacralMarker)
                        
                if self.valuePelvicFixCheck == '2':# Pelvic Triad Option
                    # Pelvis Technical coordinate system based on LPSI, RPSI, SACT
                    LeftPSISMarker = np.array([LeftPSISMarkerX[FrameNumber], LeftPSISMarkerY[FrameNumber], LeftPSISMarkerZ[FrameNumber]])
                    RightPSISMarker = np.array([RightPSISMarkerX[FrameNumber], RightPSISMarkerY[FrameNumber], RightPSISMarkerZ[FrameNumber]])
                    SacralTriadMarker = np.array([SacralTriadMarkerX[FrameNumber], SacralTriadMarkerY[FrameNumber], SacralTriadMarkerZ[FrameNumber]])
                    [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftPSISMarker, RightPSISMarker, SacralTriadMarker)
                            
                LeftASISMarkerLab = math.TransformPointIntoLabCoors(self.valueLeftASISMarkerPelvis,EPelvisTech, MidASISLab)
                RightASISMarkerLab = math.TransformPointIntoLabCoors(self.valueRightASISMarkerPelvis,EPelvisTech, MidASISLab)
        
                arrayLASISMarkerX[FrameNumber] = LeftASISMarkerLab[0]
                arrayLASISMarkerY[FrameNumber] = LeftASISMarkerLab[1]
                arrayLASISMarkerZ[FrameNumber] = LeftASISMarkerLab[2]
                arrayRASISMarkerX[FrameNumber] = RightASISMarkerLab[0]
                arrayRASISMarkerY[FrameNumber] = RightASISMarkerLab[1]
                arrayRASISMarkerZ[FrameNumber] = RightASISMarkerLab[2]
            
            
            vicon.SetTrajectory(SubjectName, self.LeftASISMarkerName, arrayLASISMarkerX, arrayLASISMarkerY, arrayLASISMarkerZ, exists )
            vicon.SetTrajectory(SubjectName, self.RightASISMarkerName, arrayRASISMarkerX, arrayRASISMarkerY, arrayRASISMarkerZ, exists )
        ################################################################################################
        # Compute Heel, Toe and MTP1 Markers if Foot Model is Used         
        if self.valueLeftFootModelCheck == '1':
            LeftFirstMetarsalBaseMarkerX, LeftFirstMetarsalBaseMarkerY, LeftFirstMetarsalBaseMarkerZ, LeftFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalBaseMarkerName)
            LeftFirstMetarsalHeadMarkerX, LeftFirstMetarsalHeadMarkerY, LeftFirstMetarsalHeadMarkerZ, LeftFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalHeadMarkerName)
            LeftFifthMetarsalHeadMarkerX, LeftFifthMetarsalHeadMarkerY, LeftFifthMetarsalHeadMarkerZ, LeftFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFifthMetarsalHeadMarkerName)
        
        if self.valueRightFootModelCheck == '1':
            RightFirstMetarsalBaseMarkerX, RightFirstMetarsalBaseMarkerY, RightFirstMetarsalBaseMarkerZ, RightFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalBaseMarkerName)
            RightFirstMetarsalHeadMarkerX, RightFirstMetarsalHeadMarkerY, RightFirstMetarsalHeadMarkerZ, RightFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalHeadMarkerName)
            RightFifthMetarsalHeadMarkerX, RightFifthMetarsalHeadMarkerY, RightFifthMetarsalHeadMarkerZ, RightFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFifthMetarsalHeadMarkerName)
        
        #Compute markers for each frame            
        framecount = vicon.GetFrameCount()
        
        arrayLMT23HMarkerX= [0 for m in range(framecount)] 
        arrayLMT23HMarkerY= [0 for m in range(framecount)] 
        arrayLMT23HMarkerZ= [0 for m in range(framecount)] 
        
        arrayRMT23HMarkerX= [0 for m in range(framecount)] 
        arrayRMT23HMarkerY= [0 for m in range(framecount)] 
        arrayRMT23HMarkerZ= [0 for m in range(framecount)] 
        
        # Initlialize array for Upper Posterior Calcaneus markers for foot model (LPCALU = {0,0,30}*LHindFoot)
        if self.valueLeftFootModelCheck == '1':
            arrayLPCALUX = [0 for m in range(framecount)]
            arrayLPCALUY = [0 for m in range(framecount)]
            arrayLPCALUZ = [30 for m in range(framecount)]

        if self.valueRightFootModelCheck == '1':
            arrayRPCALUX = [0 for m in range(framecount)]
            arrayRPCALUY = [0 for m in range(framecount)]
            arrayRPCALUZ = [30 for m in range(framecount)]
            
        exists = [True]*framecount
        
        for FrameNumber in range(StartFrame-1,EndFrame):    
            # Compute Technical Coordinate System: Left Foot Segments
            if self.valueLeftFootModelCheck == '1':
                #print FrameNumber
                #print LeftFirstMetarsalBaseMarkerX
                LeftFirstMetarsalBaseMarker = np.array([LeftFirstMetarsalBaseMarkerX[FrameNumber], LeftFirstMetarsalBaseMarkerY[FrameNumber], LeftFirstMetarsalBaseMarkerZ[FrameNumber]])
                LeftFirstMetarsalHeadMarker = np.array([LeftFirstMetarsalHeadMarkerX[FrameNumber], LeftFirstMetarsalHeadMarkerY[FrameNumber], LeftFirstMetarsalHeadMarkerZ[FrameNumber]])
                LeftFifthMetarsalHeadMarker = np.array([LeftFifthMetarsalHeadMarkerX[FrameNumber], LeftFifthMetarsalHeadMarkerY[FrameNumber], LeftFifthMetarsalHeadMarkerZ[FrameNumber]])
                LeftEForefootTech = gait.TechCS_Forefoot_mSHCG('Left', LeftFirstMetarsalBaseMarker, LeftFirstMetarsalHeadMarker, LeftFifthMetarsalHeadMarker)
                LeftMT23HMarkerLab = math.TransformPointIntoLabCoors(self.valueLeft23MetatarsalHeadMarkerForefoot,LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                arrayLMT23HMarkerX[FrameNumber] = LeftMT23HMarkerLab[0]
                arrayLMT23HMarkerY[FrameNumber] = LeftMT23HMarkerLab[1]
                arrayLMT23HMarkerZ[FrameNumber] = LeftMT23HMarkerLab[2]
                
                
            # Compute Technical Coordinate System: Right Foot Segments
            if self.valueRightFootModelCheck == '1':
                RightFirstMetarsalBaseMarker = np.array([RightFirstMetarsalBaseMarkerX[FrameNumber], RightFirstMetarsalBaseMarkerY[FrameNumber], RightFirstMetarsalBaseMarkerZ[FrameNumber]])
                RightFirstMetarsalHeadMarker = np.array([RightFirstMetarsalHeadMarkerX[FrameNumber], RightFirstMetarsalHeadMarkerY[FrameNumber], RightFirstMetarsalHeadMarkerZ[FrameNumber]])
                RightFifthMetarsalHeadMarker = np.array([RightFifthMetarsalHeadMarkerX[FrameNumber], RightFifthMetarsalHeadMarkerY[FrameNumber], RightFifthMetarsalHeadMarkerZ[FrameNumber]])
                RightEForefootTech = gait.TechCS_Forefoot_mSHCG('Right', RightFirstMetarsalBaseMarker, RightFirstMetarsalHeadMarker, RightFifthMetarsalHeadMarker)
                RightMT23HMarkerLab = math.TransformPointIntoLabCoors(self.valueRight23MetatarsalHeadMarkerForefoot,RightEForefootTech, RightFirstMetarsalBaseMarker)
                arrayRMT23HMarkerX[FrameNumber] = RightMT23HMarkerLab[0]
                arrayRMT23HMarkerY[FrameNumber] = RightMT23HMarkerLab[1]
                arrayRMT23HMarkerZ[FrameNumber] = RightMT23HMarkerLab[2]
            

        if self.valueLeftFootModelCheck == '1': 
            vicon.SetTrajectory(SubjectName, self.LeftToeMarkerName, arrayLMT23HMarkerX, arrayLMT23HMarkerY, arrayLMT23HMarkerZ, exists )
            if vicon.HasTrajectory(SubjectName,self.LeftHeelMarkerName) is False:
                LPCALx, LPCALy, LPCALz, LPCALexists = vicon.GetTrajectory( SubjectName, self.LeftPosteriorCalcaneusMarkerName )
                vicon.SetTrajectory(SubjectName, self.LeftHeelMarkerName, LPCALx, LPCALy, LPCALz, exists )
        
        if self.valueRightFootModelCheck == '1':   
            vicon.SetTrajectory(SubjectName, self.RightToeMarkerName, arrayRMT23HMarkerX, arrayRMT23HMarkerY, arrayRMT23HMarkerZ, exists )
            if vicon.HasTrajectory(SubjectName,self.RightHeelMarkerName) is False:
                RPCALx, RPCALy, RPCALz, RPCALexists = vicon.GetTrajectory( SubjectName, self.RightPosteriorCalcaneusMarkerName )
                vicon.SetTrajectory(SubjectName, self.RightHeelMarkerName, RPCALx, RPCALy, RPCALz, exists )
            
        ################################################################################################    

               
        # =============================================================================
        #      Read Marker Data      
        # =============================================================================
        C7MarkerX, C7MarkerY, C7MarkerZ, C7MarkerExists = MarkerArrayCheck(SubjectName, self.C7MarkerName)
        LeftClavicleMarkerX, LeftClavicleMarkerY, LeftClavicleMarkerZ, LeftClavicleMarkerExists = MarkerArrayCheck(SubjectName, self.LeftClavicleMarkerName)
        RightClavicleMarkerX, RightClavicleMarkerY, RightClavicleMarkerZ, RightClavicleMarkerExists = MarkerArrayCheck(SubjectName, self.RightClavicleMarkerName)
        try:
            SacralMarkerX, SacralMarkerY, SacralMarkerZ, SacralMarkerExists = MarkerArrayCheck(SubjectName, self.SacralMarkerName)
            #print('Sacral Marker Found')
        except:
            #print('Sacral Marker Not Found')
            LeftPSISMarkerX, LeftPSISMarkerY, LeftPSISMarkerZ, LeftPSISMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPSISMarkerName)
            RightPSISMarkerX, RightPSISMarkerY, RightPSISMarkerZ, RightPSISMarkerExists = MarkerArrayCheck(SubjectName, self.RightPSISMarkerName)
            framecount = vicon.GetFrameCount()
            SacralMarkerX= [0 for m in range(framecount)] 
            SacralMarkerY= [0 for m in range(framecount)] 
            SacralMarkerZ= [0 for m in range(framecount)] 
            for FrameNumber in range(StartFrame-1,EndFrame): 
                SacralMarkerX[FrameNumber] = (LeftPSISMarkerX[FrameNumber] + RightPSISMarkerX[FrameNumber]) / 2
                SacralMarkerY[FrameNumber] = (LeftPSISMarkerY[FrameNumber] + RightPSISMarkerY[FrameNumber]) / 2
                SacralMarkerZ[FrameNumber] = (LeftPSISMarkerZ[FrameNumber] + RightPSISMarkerZ[FrameNumber]) / 2
        LeftASISMarkerX, LeftASISMarkerY, LeftASISMarkerZ, LeftASISMarkerExists = MarkerArrayCheck(SubjectName, self.LeftASISMarkerName)
        LeftThighMarkerX, LeftThighMarkerY, LeftThighMarkerZ, LeftThighMarkerExists = MarkerArrayCheck(SubjectName, self.LeftThighMarkerName)
        LeftLateralKneeMarkerX, LeftLateralKneeMarkerY, LeftLateralKneeMarkerZ, LeftLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralKneeMarkerName)
        LeftTibialMarkerX, LeftTibialMarkerY, LeftTibialMarkerZ, LeftTibialMarkerExists = MarkerArrayCheck(SubjectName, self.LeftTibialMarkerName)
        
        LeftLateralAnkleMarkerX, LeftLateralAnkleMarkerY, LeftLateralAnkleMarkerZ, LeftLateralAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralAnkleMarkerName)
        LeftToeMarkerX, LeftToeMarkerY, LeftToeMarkerZ, LeftToeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftToeMarkerName)
        LeftMedialAnkleMarkerX, LeftMedialAnkleMarkerY, LeftMedialAnkleMarkerZ, LeftMedialAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.LeftMedialAnkleMarkerName)
        LeftHeelMarkerX, LeftHeelMarkerY, LeftHeelMarkerZ, LeftHeelMarkerExists = MarkerArrayCheck(SubjectName, self.LeftHeelMarkerName)
        if self.valueLeftFootModelCheck == '1':
            LeftLateralCalcaneusMarkerX, LeftLateralCalcaneusMarkerY, LeftLateralCalcaneusMarkerZ, LeftLateralCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralCalcaneusMarkerName)
            LeftMedialCalcaneusMarkerX, LeftMedialCalcaneusMarkerY, LeftMedialCalcaneusMarkerZ, LeftMedialCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.LeftMedialCalcaneusMarkerName)
            LeftPosteriorCalcaneusMarkerX, LeftPosteriorCalcaneusMarkerY, LeftPosteriorCalcaneusMarkerZ, LeftPosteriorCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPosteriorCalcaneusMarkerName)
            LeftFirstMetarsalBaseMarkerX, LeftFirstMetarsalBaseMarkerY, LeftFirstMetarsalBaseMarkerZ, LeftFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalBaseMarkerName)
            LeftFirstMetarsalHeadMarkerX, LeftFirstMetarsalHeadMarkerY, LeftFirstMetarsalHeadMarkerZ, LeftFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalHeadMarkerName)
            LeftFifthMetarsalHeadMarkerX, LeftFifthMetarsalHeadMarkerY, LeftFifthMetarsalHeadMarkerZ, LeftFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFifthMetarsalHeadMarkerName)
            #LeftFirstMetatarsoPhalangealJointMarkerX, LeftFirstMetatarsoPhalangealJointMarkerY, LeftFirstMetatarsoPhalangealJointMarkerZ, LeftFirstMetatarsoPhalangealJointMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetatarsoPhalangealJointMarkerName)
            LeftHalluxMarkerX, LeftHalluxMarkerY, LeftHalluxMarkerZ, LeftHalluxMarkerExists = MarkerArrayCheck(SubjectName, self.LeftHalluxMarkerName)
        RightASISMarkerX, RightASISMarkerY, RightASISMarkerZ, RightASISMarkerExists = MarkerArrayCheck(SubjectName, self.RightASISMarkerName)
        RightThighMarkerX, RightThighMarkerY, RightThighMarkerZ, RightThighMarkerExists = MarkerArrayCheck(SubjectName, self.RightThighMarkerName)
        RightLateralKneeMarkerX, RightLateralKneeMarkerY, RightLateralKneeMarkerZ, RightLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralKneeMarkerName)
        RightTibialMarkerX, RightTibialMarkerY, RightTibialMarkerZ, RightTibialMarkerExists = MarkerArrayCheck(SubjectName, self.RightTibialMarkerName)
        RightLateralAnkleMarkerX, RightLateralAnkleMarkerY, RightLateralAnkleMarkerZ, RightLateralAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralAnkleMarkerName)
        RightToeMarkerX, RightToeMarkerY, RightToeMarkerZ, RightToeMarkerExists = MarkerArrayCheck(SubjectName, self.RightToeMarkerName)
        RightMedialAnkleMarkerX, RightMedialAnkleMarkerY, RightMedialAnkleMarkerZ, RightMedialAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.RightMedialAnkleMarkerName)
        RightHeelMarkerX, RightHeelMarkerY, RightHeelMarkerZ, RightHeelMarkerExists = MarkerArrayCheck(SubjectName, self.RightHeelMarkerName)
        if self.valueRightFootModelCheck == '1':
            RightLateralCalcaneusMarkerX, RightLateralCalcaneusMarkerY, RightLateralCalcaneusMarkerZ, RightLateralCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralCalcaneusMarkerName)
            RightMedialCalcaneusMarkerX, RightMedialCalcaneusMarkerY, RightMedialCalcaneusMarkerZ, RightMedialCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.RightMedialCalcaneusMarkerName)
            RightPosteriorCalcaneusMarkerX, RightPosteriorCalcaneusMarkerY, RightPosteriorCalcaneusMarkerZ, RightPosteriorCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.RightPosteriorCalcaneusMarkerName)
            RightFirstMetarsalBaseMarkerX, RightFirstMetarsalBaseMarkerY, RightFirstMetarsalBaseMarkerZ, RightFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalBaseMarkerName)
            RightFirstMetarsalHeadMarkerX, RightFirstMetarsalHeadMarkerY, RightFirstMetarsalHeadMarkerZ, RightFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalHeadMarkerName)
            RightFifthMetarsalHeadMarkerX, RightFifthMetarsalHeadMarkerY, RightFifthMetarsalHeadMarkerZ, RightFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFifthMetarsalHeadMarkerName)
            #RightFirstMetatarsoPhalangealJointMarkerX, RightFirstMetatarsoPhalangealJointMarkerY, RightFirstMetatarsoPhalangealJointMarkerZ, RightFirstMetatarsoPhalangealJointMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetatarsoPhalangealJointMarkerName)
            RightHalluxMarkerX, RightHalluxMarkerY, RightHalluxMarkerZ, RightHalluxMarkerExists = MarkerArrayCheck(SubjectName, self.RightHalluxMarkerName)
        
        
        # Tibial Triad Check 
        if vicon.HasTrajectory(SubjectName,self.LeftTibialMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftTibialUpperMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftTibialLowerMarkerName) is True:
            LeftTibialTriadCheck = True
            LeftTibialUpperMarkerX, LeftTibialUpperMarkerY, LeftTibialUpperMarkerZ, LeftTibialUpperMarkerExists = MarkerArrayCheck(SubjectName, self.LeftTibialUpperMarkerName)
            LeftTibialLowerMarkerX, LeftTibialLowerMarkerY, LeftTibialLowerMarkerZ, LeftTibialLowerMarkerExists = MarkerArrayCheck(SubjectName, self.LeftTibialLowerMarkerName)
        else: 
            LeftTibialTriadCheck = False
        if vicon.HasTrajectory(SubjectName,self.RightTibialMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightTibialUpperMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightTibialLowerMarkerName) is True:
            RightTibialTriadCheck = True
            RightTibialUpperMarkerX, RightTibialUpperMarkerY, RightTibialUpperMarkerZ, RightTibialUpperMarkerExists = MarkerArrayCheck(SubjectName, self.RightTibialUpperMarkerName)
            RightTibialLowerMarkerX, RightTibialLowerMarkerY, RightTibialLowerMarkerZ, RightTibialLowerMarkerExists = MarkerArrayCheck(SubjectName, self.RightTibialLowerMarkerName)
        else: 
            RightTibialTriadCheck = False
        #print LeftTibialTriadCheck, RightTibialTriadCheck
            
        # =============================================================================
        #       Determine if Trunk Data is Available  
        # =============================================================================
        if (C7MarkerZ[StartFrame-1] * LeftClavicleMarkerZ[StartFrame-1] * RightClavicleMarkerZ[StartFrame-1]) > 0:
            TrunkFlag = 1
        else:
            TrunkFlag = 0

        # =============================================================================
        #      Check for Medial Ankle marker drop-off
        # =============================================================================
        framecount = vicon.GetFrameCount()
        LeftMedialAnkleMarkerDropOff = 0
        RightMedialAnkleMarkerDropOff = 0
        for FrameNumber in range(StartFrame-1,EndFrame):
            if LeftMedialAnkleMarkerZ[FrameNumber] == 0:
                LeftMedialAnkleMarkerDropOff = 1
            if RightMedialAnkleMarkerZ[FrameNumber] == 0:
                RightMedialAnkleMarkerDropOff = 1
                
        # =============================================================================
        #      Determine Walking Direction and lab coordinate system
        # =============================================================================
        
        #initialize the global or lab coordinate system
        ELab = np.eye(3)
        
        # Compute pelvis forward direction
        SacralMarker  = np.array([SacralMarkerX[StartFrame-1],SacralMarkerY[StartFrame-1],SacralMarkerZ[StartFrame-1]])
        CenterASIS = np.array([(LeftASISMarkerX[StartFrame-1] + RightASISMarkerX[StartFrame-1])/2,
                               (LeftASISMarkerY[StartFrame-1] + RightASISMarkerY[StartFrame-1])/2,
                               (LeftASISMarkerZ[StartFrame-1] + RightASISMarkerZ[StartFrame-1])/2])
        PelvisForwardDirectionVector = math.ComputeUnitVecFromPts(SacralMarker, CenterASIS)
        #print PelvisForwardDirectionVector
        if abs(PelvisForwardDirectionVector[1]) > abs(PelvisForwardDirectionVector[0]): # Forward facing direction is + Y
            if PelvisForwardDirectionVector[1] > 0:
                ELab[0,0], ELab[1,0], ELab[2,0]  = 0, 1, 0
                ELab[0,1], ELab[1,1], ELab[2,1]  = -1, 0, 0
                # Always Set to 1 to disable data manipulation
                Direction = 1
            else:
                ELab[0,0], ELab[1,0], ELab[2,0]  = 0, -1, 0
                ELab[0,1], ELab[1,1], ELab[2,1]  = 1, 0, 0
                # Always Set to 1 to disable data manipulation
                Direction = 1
        else:
            if PelvisForwardDirectionVector[0] > 0:
                Direction = 1
            else:
                Direction = -1
                
        #print ELab
        #print Direction
        
        # =============================================================================
        #       Anthropometic relationships from Demester (as reported in Winter's text) are used
        # =============================================================================
        HATMass = 0.678 * float(self.valueBodyMass)
        ThighMass = 0.1 * float(self.valueBodyMass)
        ShankMass = 0.0465 * float(self.valueBodyMass)
        FootMass = 0.0145 *float(self.valueBodyMass)
              
        # =============================================================================
        #      Compute Kinematics & Kinetics 
        # =============================================================================
        
        # Initialize arrays to write to C3D File
        framecount = vicon.GetFrameCount()
        exists = [True]*framecount
        
        arrayLeftHipCenter = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightHipCenter = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeCenter = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeCenter = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnkleCenter = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnkleCenter = [[0. for m in range(framecount)] for n in range(3)]
        
        # ASI, KNE, ANK for MAPS
        arrayLeftASIS = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightASIS = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKNE = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKNE = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftANK = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightANK = [[0. for m in range(framecount)] for n in range(3)]
        
        # Initialize array for Pelvic Origin, UpperPCAL for SLC
        arrayPelvisOrigin = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueLeftFootModelCheck == '1':
            arrayLeftUpperPCAL = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueRightFootModelCheck == '1':
            arrayRightUpperPCAL = [[0. for m in range(framecount)] for n in range(3)]
            
        arrayLeftTrunkAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftTrunkAnglesTOR = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftTrunkAnglesROT = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftPelvisAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftPelvisAnglesTOR = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftPelvisAnglesROT = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftThighAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftShankAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftFootAngles = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueLeftFootModelCheck == '1':
            arrayLeftHindfootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftForefootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftHalluxAngles = [[0. for m in range(framecount)] for n in range(3)]
        
        arrayRightTrunkAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightTrunkAnglesTOR = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightTrunkAnglesROT = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightPelvisAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightPelvisAnglesTOR = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightPelvisAnglesROT = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightThighAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightShankAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightFootAngles = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueRightFootModelCheck == '1':
            arrayRightHindfootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightForefootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightHalluxAngles = [[0. for m in range(framecount)] for n in range(3)]
        
        arrayLeftHipAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeAnglesProximal = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeAnglesDistal = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnkleAngles = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueLeftFootModelCheck == '1':
            arrayLeftAnkleComplexAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftMidfootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftToesAngles = [[0. for m in range(framecount)] for n in range(3)]
        
        arrayRightHipAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeAngles = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeAnglesProximal = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeAnglesDistal = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnkleAngles = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueRightFootModelCheck == '1':
            arrayRightAnkleComplexAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightMidfootAngles = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightToesAngles = [[0. for m in range(framecount)] for n in range(3)]
        
        
        arrayLeftTrunkAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftPelvisAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftThighAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftShankAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftFootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueLeftFootModelCheck == '1':
            arrayLeftHindfootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftForefootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftHalluxAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightTrunkAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightPelvisAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightThighAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightShankAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightFootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueRightFootModelCheck == '1':
            arrayRightHindfootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightForefootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightHalluxAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            
        arrayLeftHipAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnkleAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueLeftFootModelCheck == '1':
            arrayLeftAnkleComplexAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftMidfootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftToesAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            
        arrayRightHipAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnkleAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        if self.valueRightFootModelCheck == '1':
            arrayRightAnkleComplexAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightMidfootAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightToesAnglesRad = [[0. for m in range(framecount)] for n in range(3)]
        
        if self.valueLeftFootModelCheck == '1' or self.valueRightFootModelCheck == '1':
            arraySupination = [[0. for m in range(framecount)] for n in range(3)]
            arraySkew = [[0. for m in range(framecount)] for n in range(3)]
            
        arrayHATCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftThighCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftShankCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftFootCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightThighCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightShankCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightFootCenterOfMass = [[0. for m in range(framecount)] for n in range(3)]
        
        
        arrayLeftHipMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftHipPower = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftHipPowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneePower = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneePowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnkleMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnklePower = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftAnklePowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightHipMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightHipPower = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightHipPowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneePower = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneePowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnkleMoment = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnklePower = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnklePowerTotal = [[0. for m in range(framecount)] for n in range(3)]
        
        # Add JRF, GRF, Moment/Power Sums
        # Joint Reaction Forces
        arrayLeftAnkleJRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftKneeJRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftHipJRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightAnkleJRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightKneeJRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightHipJRF = [[0. for m in range(framecount)] for n in range(3)]
        # Ground Reaction Forces and Moments
        arrayLeftGRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayLeftGRM = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightGRF = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightGRM = [[0. for m in range(framecount)] for n in range(3)]
        # Moment and Power (MP) Sums (SagittalMomentSum, SagittalPowerSum, TotalPowerSum)
        arrayLeftMPSum = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightMPSum = [[0. for m in range(framecount)] for n in range(3)]
        # CoP relative to the foot CS
        arrayLeftFootCoP = [[0. for m in range(framecount)] for n in range(3)]
        arrayRightFootCoP = [[0. for m in range(framecount)] for n in range(3)]

        
        # Muscle Length and Velocities
        arrayGluteusMaxLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayIlioPsoasLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayRectFemLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayMedHamstringLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayLatHamstringLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayGastrocLength = [[0. for m in range(framecount)] for n in range(3)]
        arraySoleusLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayTibPostLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayPeronealLength = [[0. for m in range(framecount)] for n in range(3)]
        arrayVastusLatLength = [[0. for m in range(framecount)] for n in range(3)]
        
        arrayGluteusMaxVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayIlioPsoasVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayRectFemVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayMedHamstringVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayLatHamstringVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayGastrocVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arraySoleusVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayTibPostVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayPeronealVelocity = [[0. for m in range(framecount)] for n in range(3)]
        arrayVastusLatVelocity = [[0. for m in range(framecount)] for n in range(3)]
        
#        arrayLeftMusclePoint1 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayLeftMusclePoint2 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayLeftMusclePoint3 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayLeftMusclePoint4 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayRightMusclePoint1 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayRightMusclePoint2 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayRightMusclePoint3 = [[0. for m in range(framecount)] for n in range(3)]
#        arrayRightMusclePoint4 = [[0. for m in range(framecount)] for n in range(3)]
        
        
        # Muscle Length-Velocity Constants
        # Delp Pelvis Definitio is 12 deg less anteriorly tilted than Newington Gait Model
        PelvicTiltOffset = -12.0
        
        # Location of Femoral heads w.r.t. Delp Pelvis
        DelpLeftHJC =  [-70.7, 83.5,-66.1]
        DelpRightHJC = [-70.7,-83.5,-66.1]
        # Location of KHC w.r.t. HJC at zero knee flexion
        DelpKJC0 = [-5.25,0,-396]
        # Location of AJC w.r.t. KJC
        DelpAJC = [0,0,-430]
        # Location of Patella w.r.r. tibia at zero knee flexion
        DelpLPat0 =  [49.7, 2.4,-22.7]
        DelpRPat0 = [49.7,-2.4,-22.7]
        
        # Third Order Polynomial for knee and patella translation and rotation w.r.r. tibia
        # Knee Joint Center w.r.t. Femoral head *}
        #{* Anterior position vs. Knee Flexion *}
        KneeX0= -5.251699577
        KneeX1=  0.224993829
        KneeX2= -0.000591743
        KneeX3= -9.51E-06
        #{* Superior position vs. Knee Flexion *}
        KneeZ0=-396.0286373
        KneeZ1=  -0.025460796
        KneeZ2=  -0.002797058
        KneeZ3=   9.70E-06
        #{* Patella origin w.r.t. Tibia *}
        #{* Anterior position vs. Knee Flexion *}
        PatX0= 49.64730717
        PatX1= -0.116066668
        PatX2= -0.001214601
        PatX3= -5.31E-07
        #{* Superior position vs. Knee Flexion *}
        PatZ0=-22.66784449
        PatZ1=  0.028928273
        PatZ2=  0.000507812
        PatZ3= -5.79E-06
        #{* Flexion vs. Knee Flexion *}
        PatR0=  2.754722372
        PatR1= -1.019833144
        PatR2=  0.014578827
        PatR3= -6.28E-05
        #{* M/L position: Negative (lateral) for Right side *}
        PatY=  -2.4
        
        #{* Calcaneal Tubercle rel. to AJC *}
        LCalC=[ -48.7,  7.9, -42.0]
        RCalC=[ -48.7, -7.9, -42.0]
        
        LToeC=[ 179, -1.1,  -2.0]
        RToeC=[ 179,  1.1,  -2.0]
        
        
        #{* Locally Referenced Muscle Attachments from Delp *}
        #{* x=anterior, y=left lateral, z=superior *}
        #{* Right hand coordinate system for Left leg, flip sign of y-component for Right *}
        
        #{*Gluteus maximus (Superior [GMaS], Middle [GMaM] and Inferior [GMaI] compartments0, 4 points*}
        GMaS= []
        GMaS.append([-119.5,  70.0,  61.2])		#{*Pel*}
        GMaS.append( [-129.1,  88.6,   1.2])		#{*Pel*}
        GMaS.append([ -45.7,  39.2, -24.8])		#{*Fem*}
        GMaS.append([ -27.7,  47.0, -56.6])		#{*Fem*}
        GMaS_Seg = ['Pelvis','Pelvis','Thigh','Thigh']
        
        GMaM = []
        GMaM.append([-134.9,  56.3,  17.6])		#{*Pel*}
        GMaM.append([-137.6,  91.4, -52.0])		#{*Pel*}
        GMaM.append([ -42.6,  29.3, -53.0])		#{*Fem*}
        GMaM.append([ -15.6,-101.6,  41.9])		#{*Fem*}
        GMaM_Seg = ['Pelvis','Pelvis','Thigh','Thigh']
        
        GMaI = []
        GMaI.append([-155.6,   5.8, -31.4])		#{*Pel*}
        GMaI.append([-152.9,  40.3,-105.2])		#{*Pel*}
        GMaI.append([ -29.9,  13.5,-104.1])		#{*Fem*}
        GMaI.append([  -6.0,  41.1,-141.9])		#{*Fem*}
        GMaI_Seg = ['Pelvis','Pelvis','Thigh','Thigh']
        
        #{* Iliacus, 4 points *}
        Ilia = []
        Ilia.append([ -67.4,  85.4,  36.5])		#{*Pel*}
        Ilia.append([ -21.8,  85.1, -55.0])		#{*Pel*}
        Ilia.append([   1.7,   5.7, -54.3])		#{*Fem*}
        Ilia.append([ -19.3,  12.9, -62.1])		#{*Fem*}
        Ilia_Seg = ['Pelvis','Pelvis','Thigh','Thigh']
        
        #{* Psoas, 4 points *}
        Psoa = []
        Psoa.append([ -64.7,  28.9,  88.7])		#{*Pel*}
        Psoa.append([ -23.8,  75.9, -57.0])		#{*Pel*}
        Psoa.append([   1.6,   3.8, -50.7])		#{*Fem*}
        Psoa.append([  18.8,  10.4, -59.7])		#{*Fem*}
        Psoa_Seg = ['Pelvis','Pelvis','Thigh','Thigh']
        
        #{* Vastus Lateralis, 5 points *}
        VaLa = []
        VaLa.append([   4.8,  34.9,-185.4])		#{*Fem*}
        VaLa.append([  26.9,  40.9,-259.1])		#{*Fem*}
        VaLa.append([  36.1,  20.5,-403.0])     #{*Fem: -172<KneeAng<-69deg*}
        VaLa.append([  25.3,  18.4,-424.3])     #{*Fem: -172<KneeAng<-110deg*}
        VaLa.append([  10.3,  14.1,  42.3])		#{*Pat*}
        VaLa_Seg = ['Thigh','Thigh','Thigh','Thigh','Patella']
        
        
        #{* Semimembranosus, 2 points *}
        SeMe = []
        SeMe.append([-119.2,  69.5,-101.5])		#{*Pel*}
        SeMe.append([ -24.3, -19.4, -53.6])		#{*Tib*}
        SeMe_Seg = ['Pelvis','Shank']
        
        #{* Semitendinosus, 4 points *}
        SeTe = []
        SeTe.append([-123.7,  60.3,-104.3])		#{*Pel*}
        SeTe.append([ -31.4, -14.6, -54.5])		#{*Tib*}
        SeTe.append([ -11.3, -24.5, -74.6])		#{*Tib*}
        SeTe.append([   2.7, -19.3, -95.6])		#{*Tib*}
        SeTe_Seg = ['Pelvis','Shank','Shank','Shank']
        
        #{* Biceps Femoris (long and short head), 2 points *}
        BiFL = []
        BiFL.append([-124.4,  66.6,-100.1])		#{*Pel*}
        BiFL.append([  -8.1,  42.3, -72.9])		#{*Tib*}
        BiFL_Seg = ['Pelvis','Shank']
        
        BiFS = []
        BiFS.append([   5.0,  23.4,-211.1])		#{*Fem*}
        BiFS.append([ -10.1,  40.6, -72.5])		#{*Tib*}
        BiFS_Seg = ['Thigh','Shank']
        
        #{* Rectus Femoris, 2/3 Points *}
        ReFe = []
        ReFe.append([ -29.5,  96.8, -31.1])		#{*Pel*}
        #{* Wraps on Femur at large flexion angles *}
        ReFe.append([  33.4,   1.9,-403.0])     #{*Fem: 83<KneeFlex<171 deg *}
        ReFe.append([  12.1,  -1.0,  43.7])		#{*Pat*}
        ReFe_Seg = ['Pelvis','Thigh','Patella']
        
        #{* Gastrocnemius, Medial [GaMe] and Lateral [GaLa] heads, 3/4 points *}
        GaMe = []
        GaMe.append([ -12.7, -23.5,-392.9])		#{*Fem*}
        #{* Wraps on posterior fem condyles when knee is extended *}
        GaMe.append([ -23.9, -25.8,-402.2])     #{*Fem: -5<KneeFlex<44 deg*}
        GaMe.append([ -21.7, -29.5, -48.7])		#{*Tib*}
        GaMe.append([   4.4,  -5.3,  31.0])		#{*Cal*}
        GaMe_Seg = ['Thigh','Thigh','Shank','Calcaneus']
        
        GaLa = []
        GaLa.append([ -15.5,  27.2,-394.6])		#{*Fem*}
        #{* Wraps on posterior fem condyles when knee is extended *}
        GaLa.append([ -25.4,  27.4,-401.8])		#{*Fem: -5<KneeAng<44 deg*}
        GaLa.append([ -24.2,  23.5, -48.1])		#{*Tib*}
        GaLa.append([   4.4,  -5.3,  31.0])		#{*Cal*}
        GaLa_Seg = ['Thigh','Thigh','Shank','Calcaneus']
        
        #{* Soleus [Sole], 2 Points *}
        Sole = []
        Sole.append([  -2.4,   7.1,-153.3])		#{*Tib*}
        Sole.append([   4.4,  -5.3,  31.0])		#{*Cal*}
        Sole_Seg = ['Shank','Calcaneus']
        
        #{* Tibialis Posterior [TiPo], 4 points *}
        TiPo = []
        TiPo.append([  -9.4,   1.9,-134.8])		#{*Tib*}
        TiPo.append([ -14.4, -22.9,-405.1])		#{*Tib*}
        TiPo.append([  41.7, -28.6,  33.4])		#{*Cal*}
        TiPo.append([  77.2, -28.1,  15.9])		#{*Cal*}
        TiPo_Seg = ['Shank','Shank','Calcaneus','Calcaneus']
        
        #{* Peroneus Brevis [PeBr] and Longus [PeLn], 5, 7 points *}
        PeBr = []
        PeBr.append([  -7.0,  32.5,-264.6])		#{*Tib*}
        PeBr.append([ -19.8,  28.3,-418.4])		#{*Tib*}
        PeBr.append([ -14.4,  28.9,-429.5])		#{*Tib*}
        PeBr.append([  47.1,  23.3,  27.0])		#{*Cal*}
        PeBr.append([  67.7,  34.3,  21.9])		#{*Cal*}
        PeBr_Seg = ['Shank','Shank','Shank','Calcaneus','Calcaneus']
        
        PeLn = []
        PeLn.append([   0.5,  36.2,-156.8])		#{*Tib*}
        PeLn.append([ -20.7,  28.6,-420.5])		#{*Tib*}
        PeLn.append([ -16.2,  28.9,-431.9])		#{*Tib*}
        PeLn.append([  43.8,  22.1,  23.0])		#{*Cal*}
        PeLn.append([  68.1,  28.4,  10.6])		#{*Cal*}
        PeLn.append([  85.2,  11.8,   6.9])		#{*Cal*}
        PeLn.append([ 120.3, -18.4,   8.5])		#{*Cal*}
        PeLn_Seg = ['Shank','Shank','Shank','Calcaneus','Calcaneus','Calcaneus','Calcaneus']
        
        
        #for FrameNumber in xrange(framecount):
        for FrameNumber in range(StartFrame-1,EndFrame):
                 
            #Transform marker data if necessary based on direction that the patient is walking
            C7Marker  = np.array([Direction * C7MarkerX[FrameNumber], Direction * C7MarkerY[FrameNumber], C7MarkerZ[FrameNumber]])
            LeftClavicleMarker  = np.array([Direction * LeftClavicleMarkerX[FrameNumber], Direction * LeftClavicleMarkerY[FrameNumber], LeftClavicleMarkerZ[FrameNumber]])
            RightClavicleMarker  = np.array([Direction * RightClavicleMarkerX[FrameNumber], Direction * RightClavicleMarkerY[FrameNumber], RightClavicleMarkerZ[FrameNumber]])
            SacralMarker  = np.array([Direction * SacralMarkerX[FrameNumber], Direction * SacralMarkerY[FrameNumber], SacralMarkerZ[FrameNumber]])
            LeftASISMarker  = np.array([Direction * LeftASISMarkerX[FrameNumber], Direction * LeftASISMarkerY[FrameNumber], LeftASISMarkerZ[FrameNumber]])
            LeftThighMarker  = np.array([Direction * LeftThighMarkerX[FrameNumber], Direction * LeftThighMarkerY[FrameNumber], LeftThighMarkerZ[FrameNumber]])
            LeftLateralKneeMarker  = np.array([Direction * LeftLateralKneeMarkerX[FrameNumber], Direction * LeftLateralKneeMarkerY[FrameNumber], LeftLateralKneeMarkerZ[FrameNumber]])
            LeftTibialMarker  = np.array([Direction * LeftTibialMarkerX[FrameNumber], Direction * LeftTibialMarkerY[FrameNumber], LeftTibialMarkerZ[FrameNumber]])
            if LeftTibialTriadCheck is True:
                LeftTibialUpperMarker  = np.array([Direction * LeftTibialUpperMarkerX[FrameNumber], Direction * LeftTibialUpperMarkerY[FrameNumber], LeftTibialUpperMarkerZ[FrameNumber]])
                LeftTibialLowerMarker  = np.array([Direction * LeftTibialLowerMarkerX[FrameNumber], Direction * LeftTibialLowerMarkerY[FrameNumber], LeftTibialLowerMarkerZ[FrameNumber]])
            LeftLateralAnkleMarker  = np.array([Direction * LeftLateralAnkleMarkerX[FrameNumber], Direction * LeftLateralAnkleMarkerY[FrameNumber], LeftLateralAnkleMarkerZ[FrameNumber]])
            LeftToeMarker  = np.array([Direction * LeftToeMarkerX[FrameNumber], Direction * LeftToeMarkerY[FrameNumber], LeftToeMarkerZ[FrameNumber]])
            LeftMedialAnkleMarker  = np.array([Direction * LeftMedialAnkleMarkerX[FrameNumber], Direction * LeftMedialAnkleMarkerY[FrameNumber], LeftMedialAnkleMarkerZ[FrameNumber]])
            LeftHeelMarker  = np.array([Direction * LeftHeelMarkerX[FrameNumber], Direction * LeftHeelMarkerY[FrameNumber], LeftHeelMarkerZ[FrameNumber]])
            if self.valueLeftFootModelCheck == '1':
                LeftLateralCalcaneusMarker  = np.array([Direction * LeftLateralCalcaneusMarkerX[FrameNumber], Direction * LeftLateralCalcaneusMarkerY[FrameNumber], LeftLateralCalcaneusMarkerZ[FrameNumber]])
                LeftMedialCalcaneusMarker  = np.array([Direction * LeftMedialCalcaneusMarkerX[FrameNumber], Direction * LeftMedialCalcaneusMarkerY[FrameNumber], LeftMedialCalcaneusMarkerZ[FrameNumber]])
                LeftPosteriorCalcaneusMarker  = np.array([Direction * LeftPosteriorCalcaneusMarkerX[FrameNumber], Direction * LeftPosteriorCalcaneusMarkerY[FrameNumber], LeftPosteriorCalcaneusMarkerZ[FrameNumber]])
                
                # Computer MTP1 Marker
                LeftFirstMetarsalBaseMarker  = np.array([LeftFirstMetarsalBaseMarkerX[FrameNumber], LeftFirstMetarsalBaseMarkerY[FrameNumber], LeftFirstMetarsalBaseMarkerZ[FrameNumber]])
                LeftFirstMetarsalHeadMarker  = np.array([LeftFirstMetarsalHeadMarkerX[FrameNumber], LeftFirstMetarsalHeadMarkerY[FrameNumber], LeftFirstMetarsalHeadMarkerZ[FrameNumber]])
                LeftFifthMetarsalHeadMarker  = np.array([LeftFifthMetarsalHeadMarkerX[FrameNumber], LeftFifthMetarsalHeadMarkerY[FrameNumber], LeftFifthMetarsalHeadMarkerZ[FrameNumber]])
                LeftEForefootTech = gait.TechCS_Forefoot_mSHCG('Left', LeftFirstMetarsalBaseMarker, LeftFirstMetarsalHeadMarker, LeftFifthMetarsalHeadMarker)
                LeftMTP1MarkerLab = math.TransformPointIntoLabCoors(self.valueLeftFirstMetatarsoPhalangealJointMarkerForefoot,LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                LeftFirstMetatarsoPhalangealJointMarker  = np.array([Direction * LeftMTP1MarkerLab[0], Direction * LeftMTP1MarkerLab[1], LeftMTP1MarkerLab[2]])
                
                LeftFirstMetarsalBaseMarker  = np.array([Direction * LeftFirstMetarsalBaseMarkerX[FrameNumber], Direction * LeftFirstMetarsalBaseMarkerY[FrameNumber], LeftFirstMetarsalBaseMarkerZ[FrameNumber]])
                LeftFirstMetarsalHeadMarker  = np.array([Direction * LeftFirstMetarsalHeadMarkerX[FrameNumber], Direction * LeftFirstMetarsalHeadMarkerY[FrameNumber], LeftFirstMetarsalHeadMarkerZ[FrameNumber]])
                LeftFifthMetarsalHeadMarker  = np.array([Direction * LeftFifthMetarsalHeadMarkerX[FrameNumber], Direction * LeftFifthMetarsalHeadMarkerY[FrameNumber], LeftFifthMetarsalHeadMarkerZ[FrameNumber]])
                LeftHalluxMarker  = np.array([Direction * LeftHalluxMarkerX[FrameNumber], Direction * LeftHalluxMarkerY[FrameNumber], LeftHalluxMarkerZ[FrameNumber]])
            RightASISMarker  = np.array([Direction * RightASISMarkerX[FrameNumber], Direction * RightASISMarkerY[FrameNumber], RightASISMarkerZ[FrameNumber]])
            RightThighMarker  = np.array([Direction * RightThighMarkerX[FrameNumber], Direction * RightThighMarkerY[FrameNumber], RightThighMarkerZ[FrameNumber]])
            RightLateralKneeMarker  = np.array([Direction * RightLateralKneeMarkerX[FrameNumber], Direction * RightLateralKneeMarkerY[FrameNumber], RightLateralKneeMarkerZ[FrameNumber]])
            RightTibialMarker  = np.array([Direction * RightTibialMarkerX[FrameNumber], Direction * RightTibialMarkerY[FrameNumber], RightTibialMarkerZ[FrameNumber]])
            if RightTibialTriadCheck is True:
                    RightTibialUpperMarker  = np.array([Direction * RightTibialUpperMarkerX[FrameNumber], Direction * RightTibialUpperMarkerY[FrameNumber], RightTibialUpperMarkerZ[FrameNumber]])
                    RightTibialLowerMarker  = np.array([Direction * RightTibialLowerMarkerX[FrameNumber], Direction * RightTibialLowerMarkerY[FrameNumber], RightTibialLowerMarkerZ[FrameNumber]])
            RightLateralAnkleMarker  = np.array([Direction * RightLateralAnkleMarkerX[FrameNumber], Direction * RightLateralAnkleMarkerY[FrameNumber], RightLateralAnkleMarkerZ[FrameNumber]])
            RightToeMarker  = np.array([Direction * RightToeMarkerX[FrameNumber], Direction * RightToeMarkerY[FrameNumber], RightToeMarkerZ[FrameNumber]])
            RightMedialAnkleMarker  = np.array([Direction * RightMedialAnkleMarkerX[FrameNumber], Direction * RightMedialAnkleMarkerY[FrameNumber], RightMedialAnkleMarkerZ[FrameNumber]])
            RightHeelMarker  = np.array([Direction * RightHeelMarkerX[FrameNumber], Direction * RightHeelMarkerY[FrameNumber], RightHeelMarkerZ[FrameNumber]])
            if self.valueRightFootModelCheck == '1':
                RightLateralCalcaneusMarker  = np.array([Direction * RightLateralCalcaneusMarkerX[FrameNumber], Direction * RightLateralCalcaneusMarkerY[FrameNumber], RightLateralCalcaneusMarkerZ[FrameNumber]])
                RightMedialCalcaneusMarker  = np.array([Direction * RightMedialCalcaneusMarkerX[FrameNumber], Direction * RightMedialCalcaneusMarkerY[FrameNumber], RightMedialCalcaneusMarkerZ[FrameNumber]])
                RightPosteriorCalcaneusMarker  = np.array([Direction * RightPosteriorCalcaneusMarkerX[FrameNumber], Direction * RightPosteriorCalcaneusMarkerY[FrameNumber], RightPosteriorCalcaneusMarkerZ[FrameNumber]])
                
                # Computer MTP1 Marker
                RightFirstMetarsalBaseMarker  = np.array([RightFirstMetarsalBaseMarkerX[FrameNumber], RightFirstMetarsalBaseMarkerY[FrameNumber], RightFirstMetarsalBaseMarkerZ[FrameNumber]])
                RightFirstMetarsalHeadMarker  = np.array([RightFirstMetarsalHeadMarkerX[FrameNumber], RightFirstMetarsalHeadMarkerY[FrameNumber], RightFirstMetarsalHeadMarkerZ[FrameNumber]])
                RightFifthMetarsalHeadMarker  = np.array([RightFifthMetarsalHeadMarkerX[FrameNumber], RightFifthMetarsalHeadMarkerY[FrameNumber], RightFifthMetarsalHeadMarkerZ[FrameNumber]])
                RightEForefootTech = gait.TechCS_Forefoot_mSHCG('Right', RightFirstMetarsalBaseMarker, RightFirstMetarsalHeadMarker, RightFifthMetarsalHeadMarker)
                RightMTP1MarkerLab = math.TransformPointIntoLabCoors(self.valueRightFirstMetatarsoPhalangealJointMarkerForefoot,RightEForefootTech, RightFirstMetarsalBaseMarker)
                RightFirstMetatarsoPhalangealJointMarker  = np.array([Direction * RightMTP1MarkerLab[0], Direction * RightMTP1MarkerLab[1], RightMTP1MarkerLab[2]])
                
                RightFirstMetarsalBaseMarker  = np.array([Direction * RightFirstMetarsalBaseMarkerX[FrameNumber], Direction * RightFirstMetarsalBaseMarkerY[FrameNumber], RightFirstMetarsalBaseMarkerZ[FrameNumber]])
                RightFirstMetarsalHeadMarker  = np.array([Direction * RightFirstMetarsalHeadMarkerX[FrameNumber], Direction * RightFirstMetarsalHeadMarkerY[FrameNumber], RightFirstMetarsalHeadMarkerZ[FrameNumber]])
                RightFifthMetarsalHeadMarker  = np.array([Direction * RightFifthMetarsalHeadMarkerX[FrameNumber], Direction * RightFifthMetarsalHeadMarkerY[FrameNumber], RightFifthMetarsalHeadMarkerZ[FrameNumber]])
                RightHalluxMarker  = np.array([Direction * RightHalluxMarkerX[FrameNumber], Direction * RightHalluxMarkerY[FrameNumber], RightHalluxMarkerZ[FrameNumber]])
            
            # Compute Technical Coordinate System: Trunk
            if TrunkFlag == 1:
                [ETrunkTech,PelvisCenterLab,ShouldersCenterLab] = gait.TechCS_Trunk_Newington(C7Marker, LeftClavicleMarker, RightClavicleMarker, LeftASISMarker, RightASISMarker, SacralMarker)
                # Compute Anatomical Coordinate System: Trunk
                ETrunkAnat = math.TransformAnatCoorSysFromTechCoors(self.valueETrunkAnatRelTech, ETrunkTech)
                # Overwrite in case Trunk transformation is zeros in Static File
                ETrunkAnat = ETrunkTech
                    
            # Compute Technical Coordinate System: Pelvis
            [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftASISMarker, RightASISMarker, SacralMarker)
            # Compute Anatomical Coordinate System: Pelvis
            EPelvisAnat = math.TransformAnatCoorSysFromTechCoors(self.valueEPelvisAnatRelTech, EPelvisTech)
            
            # Compute Hip Center Location, relative to midASIS point and expressed relative to pelvic coor system
            if self.HipModelName == 'Newington':
                # Newington
                [LeftHipCenterPelvis, LeftHipCenterLab] = gait.JointCenterModel_Hip_Newington('Left', self.MarkerDiameter, self.valueASISdist, self.valueLeftASIStoGTdist, self.valueLeftLegLength, self.valueRightLegLength,  RightASISMarker, LeftASISMarker, EPelvisTech, MidASISLab)
                [RightHipCenterPelvis, RightHipCenterLab] = gait.JointCenterModel_Hip_Newington('Right', self.MarkerDiameter, self.valueASISdist, self.valueRightASIStoGTdist, self.valueLeftLegLength, self.valueRightLegLength, RightASISMarker, LeftASISMarker, EPelvisTech, MidASISLab)
            if self.HipModelName == 'Harrington':
                # Harrington Hip Model
                [LeftHipCenterPelvis, LeftHipCenterLab] = gait.JointCenterModel_Hip_Harrington('Left', self.valueASISdist, RightASISMarker, LeftASISMarker, SacralMarker, EPelvisTech, MidASISLab)
                [RightHipCenterPelvis, RightHipCenterLab] = gait.JointCenterModel_Hip_Harrington('Right', self.valueASISdist, RightASISMarker, LeftASISMarker, SacralMarker, EPelvisTech, MidASISLab)
            if self.HipModelName == 'Harrington2':
                # Harrington Hip Model- 2 variable
                [LeftHipCenterPelvis, LeftHipCenterLab] = gait.JointCenterModel_Hip_Harrington2('Left', self.valueASISdist, self.valueLeftLegLength, self.valueRightLegLength, RightASISMarker, LeftASISMarker, SacralMarker, EPelvisTech, MidASISLab)
                [RightHipCenterPelvis, RightHipCenterLab] = gait.JointCenterModel_Hip_Harrington2('Right', self.valueASISdist, self.valueLeftLegLength, self.valueRightLegLength, RightASISMarker, LeftASISMarker, SacralMarker, EPelvisTech, MidASISLab)
            
            # Compute Technical Coordinate System: Thigh   
            LeftEThighTech = gait.TechCS_Thigh_Newington('Left', LeftHipCenterLab, LeftThighMarker, LeftLateralKneeMarker)
            RightEThighTech = gait.TechCS_Thigh_Newington('Right', RightHipCenterLab, RightThighMarker, RightLateralKneeMarker)
            # Compute Anatomical Coordinate System: Thigh
            LeftEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEThighAnatRelTech,LeftEThighTech)
            RightEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEThighAnatRelTech,RightEThighTech)
            
            # Compute Location of Knee Center (in lab space, based on thigh anatomical frame)
            LeftKneeCenterLab = math.TransformPointIntoLabCoors(self.valueLeftKneeCenterThigh, LeftEThighTech, LeftLateralKneeMarker)
            RightKneeCenterLab = math.TransformPointIntoLabCoors(self.valueRightKneeCenterThigh, RightEThighTech, RightLateralKneeMarker)
            
            
            #print LeftTibialTriadCheck, RightTibialTriadCheck
            
            # Compute Technical Coordinate System: Shank
            if LeftTibialTriadCheck is True:
                LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftTibialUpperMarker, LeftTibialLowerMarker, LeftTibialMarker)
            else:
                LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftKneeCenterLab, LeftTibialMarker, LeftLateralAnkleMarker)
            if RightTibialTriadCheck is True:
                RightEShankTech = gait.TechCS_Shank_Newington('Right', RightTibialUpperMarker, RightTibialLowerMarker, RightTibialMarker)
            else:
                RightEShankTech = gait.TechCS_Shank_Newington('Right', RightKneeCenterLab, RightTibialMarker, RightLateralAnkleMarker)
            #print FrameNumber, RightEShankTech
            
            # Compute anklejoint centers
            if LeftTibialTriadCheck is True:
                LeftAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueLeftAnkleCenterShank, LeftEShankTech, LeftTibialMarker)
            else:
                LeftAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueLeftAnkleCenterShank, LeftEShankTech, LeftLateralAnkleMarker)
            if RightTibialTriadCheck is True:
                RightAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueRightAnkleCenterShank, RightEShankTech, RightTibialMarker)
            else:
                RightAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueRightAnkleCenterShank, RightEShankTech, RightLateralAnkleMarker)
            #print FrameNumber, RightAnkleCenterLab
            
            # If Medial ankle is available,then recompute ankle joint center
            if LeftMedialAnkleMarkerDropOff == 0:
                LeftAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Left', self.MarkerDiameter, self.valueLeftAnkleWidth, LeftLateralAnkleMarker, LeftMedialAnkleMarker)
            if RightMedialAnkleMarkerDropOff == 0:
                RightAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Right', self.MarkerDiameter, self.valueRightAnkleWidth, RightLateralAnkleMarker, RightMedialAnkleMarker)
                
            # Compute Technical Coordinate System: Foot
            LeftEFootTech = gait.TechCS_Foot_Newington('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftToeMarker)
            RightEFootTech = gait.TechCS_Foot_Newington('Right', RightKneeCenterLab, RightAnkleCenterLab, RightToeMarker)
            
            # Compute Technical Coordinate System: Left Foot Segments
            if self.valueLeftFootModelCheck == '1':
                LeftEHindfootTech = gait.TechCS_Hindfoot_mSHCG('Left', LeftLateralCalcaneusMarker, LeftMedialCalcaneusMarker, LeftPosteriorCalcaneusMarker)
                LeftEForefootTech = gait.TechCS_Forefoot_mSHCG('Left', LeftFirstMetarsalBaseMarker, LeftFirstMetarsalHeadMarker, LeftFifthMetarsalHeadMarker)
                LeftEHalluxTech = gait.TechCS_Hallux_mSHCG('Left', LeftHalluxMarker, LeftFirstMetatarsoPhalangealJointMarker, LeftToeMarker)
            
            # Compute Technical Coordinate System: Right Foot Segments
            if self.valueRightFootModelCheck == '1':
                RightEHindfootTech = gait.TechCS_Hindfoot_mSHCG('Right', RightLateralCalcaneusMarker, RightMedialCalcaneusMarker, RightPosteriorCalcaneusMarker)
                RightEForefootTech = gait.TechCS_Forefoot_mSHCG('Right', RightFirstMetarsalBaseMarker, RightFirstMetarsalHeadMarker, RightFifthMetarsalHeadMarker)
                RightEHalluxTech = gait.TechCS_Hallux_mSHCG('Right', RightHalluxMarker, RightFirstMetatarsoPhalangealJointMarker, RightToeMarker)
            
            # Compute Anatomical Coordinate Systems: Shank 
            LeftEShankProximalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEShankProximalAnatRelTech, LeftEShankTech)
            RightEShankProximalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEShankProximalAnatRelTech, RightEShankTech)
            LeftEShankDistalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEShankDistalAnatRelTech, LeftEShankTech)
            RightEShankDistalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEShankDistalAnatRelTech, RightEShankTech)
            
            # If Medial ankle is available,then recompute Shank Proximal/Distal Anatomical Coordinate System
            if LeftMedialAnkleMarkerDropOff == 0:
                LeftEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Left', LeftKneeCenterLab, LeftLateralKneeMarker, LeftAnkleCenterLab)
                LeftEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftLateralAnkleMarker)
            if RightMedialAnkleMarkerDropOff == 0:
                RightEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Right', RightKneeCenterLab, RightLateralKneeMarker, RightAnkleCenterLab)
                RightEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Right', RightKneeCenterLab, RightAnkleCenterLab, RightLateralAnkleMarker)
                
            # Compute Anatomical Coordinate Systems: Foot
            LeftEFootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEFootAnatRelTech, LeftEFootTech)
            RightEFootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEFootAnatRelTech, RightEFootTech)
            
            try:
                # Compute 2nd Foot Coordinate System for Joint Reaction forces that uses the Tibia for 2md defining line
                LeftEFootTibAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEFootAnat2RelTech , LeftEFootTech)
                RightEFootTibAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEFootAnat2RelTech , RightEFootTech)
            except:
                LeftEFootTibAnat = np.matrix([[0. for m in range(3)] for n in range(3)])
                RightEFootTibAnat = np.matrix([[0. for m in range(3)] for n in range(3)])
               
            # Compute Anatomical Coordinate System: Left Foot Segments
            if self.valueLeftFootModelCheck == '1':
                LeftEHindfootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEHindfootAnatRelTech, LeftEHindfootTech)
                LeftEForefootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEForefootAnatRelTech, LeftEForefootTech)
                LeftEHalluxAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEHalluxAnatRelTech, LeftEHalluxTech)
                # 3D array, local vector in hindfoot to the upper cal point
                LeftUpperPosteriorCalcaneusHindfoot = np.array([arrayLPCALUX[FrameNumber], arrayLPCALUY[FrameNumber], arrayLPCALUZ[FrameNumber]])
                # Transform into Lab CS
                LeftUpperPosteriorCalcaneusMarker = math.TransformPointIntoLabCoors(LeftUpperPosteriorCalcaneusHindfoot, LeftEHindfootAnat, LeftPosteriorCalcaneusMarker)

            # Compute Anatomical Coordinate System: Right Foot Segments
            if self.valueRightFootModelCheck == '1':
                RightEHindfootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEHindfootAnatRelTech, RightEHindfootTech)
                RightEForefootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEForefootAnatRelTech, RightEForefootTech)
                RightEHalluxAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEHalluxAnatRelTech, RightEHalluxTech)
                # 3D array, local vector in hindfoot to the upper cal point
                RightUpperPosteriorCalcaneusHindfoot = np.array([arrayRPCALUX[FrameNumber], arrayRPCALUY[FrameNumber], arrayRPCALUZ[FrameNumber]])
                # Transform into Lab CS
                RightUpperPosteriorCalcaneusMarker = math.TransformPointIntoLabCoors(RightUpperPosteriorCalcaneusHindfoot, RightEHindfootAnat, RightPosteriorCalcaneusMarker)

            # Compute Kinematics
            
            #Compute trunk kinematics
            if TrunkFlag == 1:
                TrunkAnglesTORRad = math.EulerAngles_YXZ(ETrunkAnat, ELab)
                TrunkAnglesROTRad = math.EulerAngles_ZXY(ETrunkAnat, ELab)
                if self.TrunkRotationSequence == 'TOR':
                    TrunkAnglesRad = TrunkAnglesTORRad
                if self.TrunkRotationSequence == 'ROT':
                    TrunkAnglesRad = TrunkAnglesROTRad
            else:
                TrunkAnglesTORRad = np.array([0.,0.,0.])   
                TrunkAnglesROTRad = np.array([0.,0.,0.])   
                TrunkAnglesRad = np.array([0.,0.,0.])    
            #Compute pelvic kinematics
            PelvisAnglesTORRad = math.EulerAngles_YXZ(EPelvisAnat, ELab)
            PelvisAnglesROTRad = math.EulerAngles_ZXY(EPelvisAnat, ELab)
            if self.PelvisRotationSequence == 'TOR':
                PelvisAnglesRad = PelvisAnglesTORRad
            if self.PelvisRotationSequence == 'ROT':
                PelvisAnglesRad = PelvisAnglesROTRad
            #Compute thigh kinematics
            LeftThighAnglesRad = math.EulerAngles_YXZ(LeftEThighAnat, ELab)
            RightThighAnglesRad = math.EulerAngles_YXZ(RightEThighAnat, ELab)
            #Compute shank kinematics
            LeftShankAnglesRad = math.EulerAngles_YXZ(LeftEShankDistalAnat, ELab)     
            RightShankAnglesRad = math.EulerAngles_YXZ(RightEShankDistalAnat, ELab)     
            #Compute foot kinematics
            LeftFootAnglesRad = math.EulerAngles_YXZ(LeftEFootAnat, ELab)
            RightFootAnglesRad = math.EulerAngles_YXZ(RightEFootAnat, ELab)
            #Compute foot segment kinematics
            if self.valueLeftFootModelCheck == '1':
                LeftHindfootAnglesRad = math.EulerAngles_YXZ(LeftEHindfootAnat, ELab)
                LeftForefootAnglesRad = math.EulerAngles_YXZ(LeftEForefootAnat, ELab)
                LeftHalluxAnglesRad = math.EulerAngles_YXZ(LeftEHalluxAnat, ELab)
                # Create a Coordinate System with y axis aligned with HF progression axis
                ey = np.array([LeftEHindfootAnat[0][1],LeftEHindfootAnat[1][1],0])#LeftEHindfootAnat[1][2]])
                ey = ey/ np.linalg.norm(ey)
                R1 = np.array([0.,0.,1.]) 
                ex = np.cross(ey,R1)
                ez = np.cross(ex,ey)
                LeftEHFProgression = np.column_stack((ex,ey,ez))
                ##########################################################################
                # Segment Inclinatiosn are measured w.r.t. Lab axis aligned with HF Progression
                LeftHindfootAnglesRelHFProgressionRad = math.EulerAngles_YXZ(LeftEHindfootAnat, LeftEHFProgression)
                LeftForefootAnglesRelHFProgressionRad = math.EulerAngles_YXZ(LeftEForefootAnat, LeftEHFProgression)
                LeftHalluxAnglesRelHFProgressionRad = math.EulerAngles_YXZ(LeftEHalluxAnat, LeftEHFProgression)               
            if self.valueRightFootModelCheck == '1':
                RightHindfootAnglesRad = math.EulerAngles_YXZ(RightEHindfootAnat, ELab)
                RightForefootAnglesRad = math.EulerAngles_YXZ(RightEForefootAnat, ELab)
                RightHalluxAnglesRad = math.EulerAngles_YXZ(RightEHalluxAnat, ELab)
                # Create a Coordinate System with y axis aligned with HF progression axis
                ey = np.array([RightEHindfootAnat[0][1],RightEHindfootAnat[1][1],0])#RightEHindfootAnat[1][2]])
                ey = ey/ np.linalg.norm(ey)
                R1 = np.array([0.,0.,1.]) 
                ex = np.cross(ey,R1)
                ez = np.cross(ex,ey)
                RightEHFProgression = np.column_stack((ex,ey,ez))
                ##########################################################################
                # Segment Inclinatiosn are measured w.r.t. Lab axis aligned with HF Progression
                RightHindfootAnglesRelHFProgressionRad = math.EulerAngles_YXZ(RightEHindfootAnat, RightEHFProgression)
                RightForefootAnglesRelHFProgressionRad = math.EulerAngles_YXZ(RightEForefootAnat, RightEHFProgression)
                RightHalluxAnglesRelHFProgressionRad = math.EulerAngles_YXZ(RightEHalluxAnat, RightEHFProgression)    
            #Compute hip kinematics
            LeftHipAnglesRad = math.EulerAngles_YXZ(LeftEThighAnat, EPelvisAnat)
            RightHipAnglesRad = math.EulerAngles_YXZ(RightEThighAnat, EPelvisAnat)
            #Compute knee kinematics
            LeftKneeAnglesProximalRad = math.EulerAngles_YXZ(LeftEShankProximalAnat, LeftEThighAnat)    
            RightKneeAnglesProximalRad = math.EulerAngles_YXZ(RightEShankProximalAnat, RightEThighAnat)
            LeftKneeAnglesDistalRad = math.EulerAngles_YXZ(LeftEShankDistalAnat, LeftEThighAnat)    
            RightKneeAnglesDistalRad = math.EulerAngles_YXZ(RightEShankDistalAnat, RightEThighAnat)
            if self.ShankCoordinateSystem == 'Distal':
                LeftKneeAnglesRad = math.EulerAngles_YXZ(LeftEShankDistalAnat, LeftEThighAnat)    
                RightKneeAnglesRad = math.EulerAngles_YXZ(RightEShankDistalAnat, RightEThighAnat)
            if self.ShankCoordinateSystem == 'Proximal':
                LeftKneeAnglesRad = math.EulerAngles_YXZ(LeftEShankProximalAnat, LeftEThighAnat)    
                RightKneeAnglesRad = math.EulerAngles_YXZ(RightEShankProximalAnat, RightEThighAnat)    
            #Compute ankle kinematics
            LeftAnkleAnglesRad = math.EulerAngles_YXZ(LeftEFootAnat, LeftEShankDistalAnat)
            RightAnkleAnglesRad = math.EulerAngles_YXZ(RightEFootAnat, RightEShankDistalAnat)
            #Compute foot joint kinematics
            if self.valueLeftFootModelCheck == '1':
                LeftAnkleComplexAnglesRad = math.EulerAngles_YXZ(LeftEHindfootAnat, LeftEShankDistalAnat)
                LeftMidfootAnglesRad = math.EulerAngles_YXZ(LeftEForefootAnat, LeftEHindfootAnat)
                if not LeftHalluxMarker[2] == 0: # if Hallux marker missing, set ToeAngles to zero
                    LeftToesAnglesRad = math.EulerAngles_YXZ(LeftEHalluxAnat, LeftEForefootAnat)
                else:
                    LeftToesAnglesRad = np.array([0.,0.,0.])
                
            if self.valueRightFootModelCheck == '1':
                RightAnkleComplexAnglesRad = math.EulerAngles_YXZ(RightEHindfootAnat, RightEShankDistalAnat)
                RightMidfootAnglesRad = math.EulerAngles_YXZ(RightEForefootAnat, RightEHindfootAnat)
                RightToesAnglesRad = math.EulerAngles_YXZ(RightEHalluxAnat, RightEForefootAnat)    
                if not RightHalluxMarker[2] == 0: # if Hallux marker missing, set ToeAngles to zero
                    RightToesAnglesRad = math.EulerAngles_YXZ(RightEHalluxAnat, RightEForefootAnat)    
                else:
                    RightToesAnglesRad = np.array([0.,0.,0.])
            
            #Convert units of angles from radians to degrees & set sign based on side and plotting convention
            Sign = -1 # For Left Side
    
            T1, T1[0,0], T1[1,1], T1[2,2] = np.eye(3), -Sign, +1, Sign
            T2, T2[0,0], T2[1,1], T2[2,2] = np.eye(3),  Sign, -1, Sign
            T3, T3[0,0], T3[1,1], T3[2,2] = np.eye(3),  Sign, +1, Sign
            
            LeftTrunkAnglesDeg = T1.dot(TrunkAnglesRad) * 180 / np.pi 
            LeftTrunkAnglesTORDeg = T1.dot(TrunkAnglesTORRad) * 180 / np.pi 
            LeftTrunkAnglesROTDeg = T1.dot(TrunkAnglesROTRad) * 180 / np.pi 
            LeftPelvisAnglesDeg = T1.dot(PelvisAnglesRad) * 180 / np.pi
            LeftPelvisAnglesTORDeg = T1.dot(PelvisAnglesTORRad) * 180 / np.pi
            LeftPelvisAnglesROTDeg = T1.dot(PelvisAnglesROTRad) * 180 / np.pi
            LeftThighAnglesDeg = T1.dot(LeftThighAnglesRad) * 180 / np.pi
            LeftShankAnglesDeg = T1.dot(LeftShankAnglesRad) * 180 / np.pi
            LeftFootAnglesDeg = T1.dot(LeftFootAnglesRad) * 180 / np.pi
            LeftHipAnglesDeg = T2.dot(LeftHipAnglesRad) * 180 / np.pi
            LeftKneeAnglesDeg = T3.dot(LeftKneeAnglesRad) * 180 / np.pi
            LeftKneeAnglesProximalDeg = T3.dot(LeftKneeAnglesProximalRad) * 180 / np.pi
            LeftKneeAnglesDistalDeg = T3.dot(LeftKneeAnglesDistalRad) * 180 / np.pi
            LeftAnkleAnglesDeg = T2.dot(LeftAnkleAnglesRad) * 180 / np.pi
            if self.valueLeftFootModelCheck == '1':
                LeftHindfootAnglesDeg = T1.dot(LeftHindfootAnglesRad) * 180 / np.pi 
                LeftForefootAnglesDeg = T1.dot(LeftForefootAnglesRad) * 180 / np.pi 
                LeftHalluxAnglesDeg   = T1.dot(LeftHalluxAnglesRad) * 180 / np.pi 
                LeftHindfootAnglesRelHFProgressionDeg = T2.dot(LeftHindfootAnglesRelHFProgressionRad) * 180 / np.pi 
                LeftForefootAnglesRelHFProgressionDeg = T2.dot(LeftForefootAnglesRelHFProgressionRad) * 180 / np.pi 
                LeftHalluxAnglesRelHFProgressionDeg   = T2.dot(LeftHalluxAnglesRelHFProgressionRad) * 180 / np.pi 
                LeftAnkleComplexAnglesDeg = T2.dot(LeftAnkleComplexAnglesRad) * 180 / np.pi 
                LeftMidfootAnglesDeg = T2.dot(LeftMidfootAnglesRad) * 180 / np.pi 
                LeftToesAnglesDeg = T2.dot(LeftToesAnglesRad) * 180 / np.pi 
            
            # Store Angles in radians without changing sign based on side and plotting convention
            # These are used in computing Kinetics
            T1, T2, T3 = np.eye(3), np.eye(3), np.eye(3)
            LeftTrunkAnglesRad = T1.dot(TrunkAnglesRad) 
            LeftPelvisAnglesRad = T1.dot(PelvisAnglesRad)
            LeftThighAnglesRad = T1.dot(LeftThighAnglesRad)
            LeftShankAnglesRad = T1.dot(LeftShankAnglesRad)
            LeftFootAnglesRad = T1.dot(LeftFootAnglesRad)
            LeftHipAnglesRad = T2.dot(LeftHipAnglesRad)
            LeftKneeAnglesRad = T3.dot(LeftKneeAnglesRad)
            LeftAnkleAnglesRad = T2.dot(LeftAnkleAnglesRad)
            
            
            Sign = 1 #For Right Side
            
            T1, T1[0,0], T1[1,1], T1[2,2] = np.eye(3), -Sign, +1, Sign
            T2, T2[0,0], T2[1,1], T2[2,2] = np.eye(3),  Sign, -1, Sign
            T3, T3[0,0], T3[1,1], T3[2,2] = np.eye(3),  Sign, +1, Sign
            
            RightTrunkAnglesDeg = T1.dot(TrunkAnglesRad) * 180 / np.pi 
            RightTrunkAnglesTORDeg = T1.dot(TrunkAnglesTORRad) * 180 / np.pi 
            RightTrunkAnglesROTDeg = T1.dot(TrunkAnglesROTRad) * 180 / np.pi 
            RightPelvisAnglesDeg = T1.dot(PelvisAnglesRad) * 180 / np.pi
            RightPelvisAnglesTORDeg = T1.dot(PelvisAnglesTORRad) * 180 / np.pi
            RightPelvisAnglesROTDeg = T1.dot(PelvisAnglesROTRad) * 180 / np.pi
            RightThighAnglesDeg = T1.dot(RightThighAnglesRad) * 180 / np.pi
            RightShankAnglesDeg = T1.dot(RightShankAnglesRad) * 180 / np.pi
            RightFootAnglesDeg = T1.dot(RightFootAnglesRad) * 180 / np.pi
            RightHipAnglesDeg = T2.dot(RightHipAnglesRad) * 180 / np.pi
            RightKneeAnglesDeg = T3.dot(RightKneeAnglesRad) * 180 / np.pi
            RightKneeAnglesProximalDeg = T3.dot(RightKneeAnglesProximalRad) * 180 / np.pi
            RightKneeAnglesDistalDeg = T3.dot(RightKneeAnglesDistalRad) * 180 / np.pi
            RightAnkleAnglesDeg = T2.dot(RightAnkleAnglesRad) * 180 / np.pi
            if self.valueRightFootModelCheck == '1':
                RightHindfootAnglesDeg = T1.dot(RightHindfootAnglesRad) * 180 / np.pi 
                RightForefootAnglesDeg = T1.dot(RightForefootAnglesRad) * 180 / np.pi 
                RightHalluxAnglesDeg   = T1.dot(RightHalluxAnglesRad) * 180 / np.pi 
                RightHindfootAnglesRelHFProgressionDeg = T2.dot(RightHindfootAnglesRelHFProgressionRad) * 180 / np.pi 
                RightForefootAnglesRelHFProgressionDeg = T2.dot(RightForefootAnglesRelHFProgressionRad) * 180 / np.pi 
                RightHalluxAnglesRelHFProgressionDeg   = T2.dot(RightHalluxAnglesRelHFProgressionRad) * 180 / np.pi 
                RightAnkleComplexAnglesDeg = T2.dot(RightAnkleComplexAnglesRad) * 180 / np.pi 
                RightMidfootAnglesDeg = T2.dot(RightMidfootAnglesRad) * 180 / np.pi 
                RightToesAnglesDeg = T2.dot(RightToesAnglesRad) * 180 / np.pi 
            
            
            
            # Store Angles in radians without changing sign based on side and plotting convention
            # These are used in computing Kinetics
            T1, T2, T3 = np.eye(3), np.eye(3), np.eye(3)
            RightTrunkAnglesRad = T1.dot(TrunkAnglesRad) 
            RightPelvisAnglesRad = T1.dot(PelvisAnglesRad)
            RightThighAnglesRad = T1.dot(RightThighAnglesRad)
            RightShankAnglesRad = T1.dot(RightShankAnglesRad)
            RightFootAnglesRad = T1.dot(RightFootAnglesRad)
            RightHipAnglesRad = T2.dot(RightHipAnglesRad)
            RightKneeAnglesRad = T3.dot(RightKneeAnglesRad)
            RightAnkleAnglesRad = T2.dot(RightAnkleAnglesRad)

            # =============================================================================
            #             Compute Muscle Lengths
            # =============================================================================
            
            # Knee Joint Centers based on knee flexion angle
            # Find KJC w.r.t. HJC from 3rd order polynomial and knee flexion
            LKF = LeftKneeAnglesProximalDeg[1]
            RKF = RightKneeAnglesProximalDeg[1]
            
            LeftKneeX  = KneeX0 + KneeX1*LKF + KneeX2*LKF*LKF + KneeX3*LKF*LKF*LKF
            RightKneeX = KneeX0 + KneeX1*RKF + KneeX2*RKF*RKF + KneeX3*RKF*RKF*RKF
            LeftKneeZ  = KneeZ0 + KneeZ1*LKF + KneeZ2*LKF*LKF + KneeZ3*LKF*LKF*LKF
            RightKneeZ = KneeZ0 + KneeZ1*RKF + KneeZ2*RKF*RKF + KneeZ3*RKF*RKF*RKF
            LeftDelpKJC_Polynomial  = [LeftKneeX,  0, LeftKneeZ]
            RightDelpKJC_Polynomial = [RightKneeX, 0, RightKneeZ]
            
            # Patella movement (x and y translation and flexion) with 
            # respect to leg defined by third order polynomials. 	
            LeftPatX  = PatX0 + PatX1*LKF + PatX2*LKF*LKF + PatX3*LKF*LKF*LKF
            RightPatX = PatX0 + PatX1*RKF + PatX2*RKF*RKF + PatX3*RKF*RKF*RKF
            LeftPatZ  = PatZ0 + PatZ1*LKF + PatZ2*LKF*LKF + PatZ3*LKF*LKF*LKF
            RightPatZ = PatZ0 + PatZ1*RKF + PatZ2*RKF*RKF + PatZ3*RKF*RKF*RKF
            LeftPatR  = PatR0 + PatR1*LKF + PatR2*LKF*LKF + PatR3*LKF*LKF*LKF
            RightPatR = PatR0 + PatR1*RKF + PatR2*RKF*RKF + PatR3*RKF*RKF*RKF
            
            # Compute Delp Muscle Model Coordinate Systems
            [EPelvisAnatDelp, MidASISLab] = gait.AnatCS_Pelvis_Delp(LeftASISMarker, RightASISMarker, SacralMarker,PelvicTiltOffset)
            LeftEThighAnatDelp = LeftEThighAnat
            RightEThighAnatDelp = RightEThighAnat
            LeftEShankAnatDelp = LeftEShankProximalAnat#LeftEShankDistalAnat
            RightEShankAnatDelp = RightEShankProximalAnat#RightEShankDistalAnat
            LeftEPatellaAnatDelp = LeftEShankAnatDelp
            RightEPatellaAnatDelp = RightEShankAnatDelp
            # Rotate Patella CS by PatR around Y axis
            LeftEPatellaAnatDelp = math.RotateCSaroundYaxis(LeftEPatellaAnatDelp,LeftPatR)
            RightEPatellaAnatDelp = math.RotateCSaroundYaxis(RightEPatellaAnatDelp,RightPatR)
            LeftECalcaneusAnatDelp = LeftEFootAnat
            RightECalcaneusAnatDelp = RightEFootAnat
            
            PelvisOriginDelp = np.array([MidASISLab[0],MidASISLab[1]+1000.,949.])
            LeftThighOriginDelp = math.TransformPointIntoLabCoors(DelpLeftHJC,EPelvisAnatDelp,PelvisOriginDelp)
            RightThighOriginDelp = math.TransformPointIntoLabCoors(DelpRightHJC,EPelvisAnatDelp,PelvisOriginDelp)
            LeftShankOriginDelp = math.TransformPointIntoLabCoors(LeftDelpKJC_Polynomial,LeftEThighAnatDelp,LeftThighOriginDelp)
            RightShankOriginDelp = math.TransformPointIntoLabCoors(RightDelpKJC_Polynomial,RightEThighAnatDelp,RightThighOriginDelp)
            LeftPatellaOriginDelp  = math.TransformPointIntoLabCoors([LeftPatX, -PatY,LeftPatZ], LeftEShankAnatDelp, LeftShankOriginDelp)
            RightPatellaOriginDelp = math.TransformPointIntoLabCoors([RightPatX, PatY,RightPatZ],RightEShankAnatDelp,RightShankOriginDelp)
            LeftCalcaneusOriginDelp_AJC = math.TransformPointIntoLabCoors(DelpAJC,LeftEShankAnatDelp,LeftShankOriginDelp)
            RightCalcaneusOriginDelp_AJC = math.TransformPointIntoLabCoors(DelpAJC,RightEShankAnatDelp,RightShankOriginDelp)
            LeftCalcaneusOriginDelp = math.TransformPointIntoLabCoors(LCalC,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp_AJC)
            RightCalcaneusOriginDelp = math.TransformPointIntoLabCoors(RCalC,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp_AJC)
            
            # Compute Zero Positions to compute Normalizing Muscle Length
            ELabDelp = np.eye(3)
            EPelvisAnatDelp0 = ELabDelp
            LeftEThighAnatDelp0 = ELabDelp
            RightEThighAnatDelp0 = ELabDelp
            LeftEShankAnatDelp0 = ELabDelp
            RightEShankAnatDelp0 = ELabDelp
            LeftECalcaneusAnatDelp0 = ELabDelp
            RightECalcaneusAnatDelp0 = ELabDelp
            LeftEPatellaAnatDelp0 = ELabDelp
            RightEPatellaAnatDelp0 = ELabDelp
            # Rotate Calcaneus to account for normal tibial torsion
            LeftECalcaneusAnatDelp0 = math.RotateCSaroundZaxis(ELabDelp,15.0)
            RightECalcaneusAnatDelp0 = math.RotateCSaroundZaxis(ELabDelp,-15.0)
            # Flex patellae by constant at zero knee flexion
            LeftEPatellaAnatDelp0 = math.RotateCSaroundYaxis(ELabDelp,PatR0)
            RightEPatellaAnatDelp0 = math.RotateCSaroundYaxis(ELabDelp,PatR0)
            
            PelvisOriginDelp0 = PelvisOriginDelp
            LeftThighOriginDelp0 = PelvisOriginDelp + DelpLeftHJC
            RightThighOriginDelp0 = PelvisOriginDelp + DelpRightHJC
            LeftShankOriginDelp0 = PelvisOriginDelp + DelpLeftHJC + DelpKJC0
            RightShankOriginDelp0 = PelvisOriginDelp + DelpRightHJC + DelpKJC0
            LeftPatellaOriginDelp0 = PelvisOriginDelp + DelpLeftHJC + DelpKJC0 + DelpLPat0
            RightPatellaOriginDelp0 = PelvisOriginDelp + DelpRightHJC + DelpKJC0 + DelpRPat0
            LeftCalcaneusOriginDelp0 = PelvisOriginDelp + DelpLeftHJC + DelpKJC0 + DelpAJC + LCalC
            RightCalcaneusOriginDelp0 = PelvisOriginDelp + DelpRightHJC + DelpKJC0 + DelpAJC + RCalC
            
            
            # Compute Muscle lengths
            [LeftGMaS,LeftGMaSMusclePoints] = math.ComputeMuscleLength('Left',GMaS,GMaS_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightGMaS,RightGMaSMusclePoints] = math.ComputeMuscleLength('Right',GMaS,GMaS_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftGMaS0,LeftGMaSMusclePoints0] = math.ComputeMuscleLength('Left',GMaS,GMaS_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightGMaS0,RightGMaSMusclePoints0]= math.ComputeMuscleLength('Right',GMaS,GMaS_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftGMaM,LeftGMaMMusclePoints] = math.ComputeMuscleLength('Left',GMaM,GMaM_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightGMaM,RightGMaMMusclePoints] = math.ComputeMuscleLength('Right',GMaM,GMaM_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftGMaM0,LeftGMaMMusclePoints0] = math.ComputeMuscleLength('Left',GMaM,GMaM_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightGMaM0,RightGMaMMusclePoints0]= math.ComputeMuscleLength('Right',GMaM,GMaM_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftGMaI,LeftGMaIMusclePoints] = math.ComputeMuscleLength('Left',GMaI,GMaI_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightGMaI,RightGMaIMusclePoints] = math.ComputeMuscleLength('Right',GMaI,GMaI_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftGMaI0,LeftGMaIMusclePoints0] = math.ComputeMuscleLength('Left',GMaI,GMaI_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightGMaI0,RightGMaIMusclePoints0]= math.ComputeMuscleLength('Right',GMaI,GMaI_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftIlia,LeftIliaMusclePoints] = math.ComputeMuscleLength('Left',Ilia,Ilia_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightIlia,RightIliaMusclePoints] = math.ComputeMuscleLength('Right',Ilia,Ilia_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftIlia0,LeftIliaMusclePoints0] = math.ComputeMuscleLength('Left',Ilia,Ilia_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightIlia0,RightIliaMusclePoints0]= math.ComputeMuscleLength('Right',Ilia,Ilia_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftPsoa,LeftPsoaMusclePoints] = math.ComputeMuscleLength('Left',Psoa,Psoa_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightPsoa,RightPsoaMusclePoints] = math.ComputeMuscleLength('Right',Psoa,Psoa_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftPsoa0,LeftPsoaMusclePoints0] = math.ComputeMuscleLength('Left',Psoa,Psoa_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightPsoa0,RightPsoaMusclePoints0]= math.ComputeMuscleLength('Right',Psoa,Psoa_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftSeMe,LeftSeMeMusclePoints] = math.ComputeMuscleLength('Left',SeMe,SeMe_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightSeMe,RightSeMeMusclePoints] = math.ComputeMuscleLength('Right',SeMe,SeMe_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftSeMe0,LeftSeMeMusclePoints0] = math.ComputeMuscleLength('Left',SeMe,SeMe_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightSeMe0,RightSeMeMusclePoints0]= math.ComputeMuscleLength('Right',SeMe,SeMe_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftSeTe,LeftSeTeMusclePoints] = math.ComputeMuscleLength('Left',SeTe,SeTe_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightSeTe,RightSeTeMusclePoints] = math.ComputeMuscleLength('Right',SeTe,SeTe_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftSeTe0,LeftSeTeMusclePoints0] = math.ComputeMuscleLength('Left',SeTe,SeTe_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightSeTe0,RightSeTeMusclePoints0]= math.ComputeMuscleLength('Right',SeTe,SeTe_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftBiFL,LeftBiFLMusclePoints] = math.ComputeMuscleLength('Left',BiFL,BiFL_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightBiFL,RightBiFLMusclePoints] = math.ComputeMuscleLength('Right',BiFL,BiFL_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftBiFL0,LeftBiFLMusclePoints0] = math.ComputeMuscleLength('Left',BiFL,BiFL_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightBiFL0,RightBiFLMusclePoints0]= math.ComputeMuscleLength('Right',BiFL,BiFL_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftBiFS,LeftBiFSMusclePoints] = math.ComputeMuscleLength('Left',BiFS,BiFS_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightBiFS,RightBiFSMusclePoints] = math.ComputeMuscleLength('Right',BiFS,BiFS_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftBiFS0,LeftBiFSMusclePoints0] = math.ComputeMuscleLength('Left',BiFS,BiFS_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightBiFS0,RightBiFSMusclePoints0]= math.ComputeMuscleLength('Right',BiFS,BiFS_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftSole,LeftSoleMusclePoints] = math.ComputeMuscleLength('Left',Sole,Sole_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightSole,RightSoleMusclePoints] = math.ComputeMuscleLength('Right',Sole,Sole_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftSole0,LeftSoleMusclePoints0] = math.ComputeMuscleLength('Left',Sole,Sole_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightSole0,RightSoleMusclePoints0]= math.ComputeMuscleLength('Right',Sole,Sole_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftTiPo,LeftTiPoMusclePoints] = math.ComputeMuscleLength('Left',TiPo,TiPo_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightTiPo,RightTiPoMusclePoints] = math.ComputeMuscleLength('Right',TiPo,TiPo_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftTiPo0,LeftTiPoMusclePoints0] = math.ComputeMuscleLength('Left',TiPo,TiPo_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightTiPo0,RightTiPoMusclePoints0]= math.ComputeMuscleLength('Right',TiPo,TiPo_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftPeBr,LeftPeBrMusclePoints] = math.ComputeMuscleLength('Left',PeBr,PeBr_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightPeBr,RightPeBrMusclePoints] = math.ComputeMuscleLength('Right',PeBr,PeBr_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftPeBr0,LeftPeBrMusclePoints0] = math.ComputeMuscleLength('Left',PeBr,PeBr_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightPeBr0,RightPeBrMusclePoints0]= math.ComputeMuscleLength('Right',PeBr,PeBr_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            [LeftPeLn,LeftPeLnMusclePoints] = math.ComputeMuscleLength('Left',PeLn,PeLn_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightPeLn,RightPeLnMusclePoints] = math.ComputeMuscleLength('Right',PeLn,PeLn_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftPeLn0,LeftPeLnMusclePoints0] = math.ComputeMuscleLength('Left',PeLn,PeLn_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightPeLn0,RightPeLnMusclePoints0]= math.ComputeMuscleLength('Right',PeLn,PeLn_Seg,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            # Remove Second Point if Knee Flexion < 83 deg
            Left_ReFe = []
            if LKF < 83:
                Left_ReFe.append(ReFe[0])
                Left_ReFe.append(ReFe[2])
                Left_ReFe_Seg = ['Pelvis','Patella']
            else:
                Left_ReFe = ReFe
                Left_ReFe_Seg = ReFe_Seg
            Right_ReFe = []
            if RKF < 83:
                Right_ReFe.append(ReFe[0])
                Right_ReFe.append(ReFe[2])
                Right_ReFe_Seg = ['Pelvis','Patella']
            else:
                Right_ReFe = ReFe
                Right_ReFe_Seg = ReFe_Seg
            
            Left_ReFe0 = []
            Left_ReFe0.append(ReFe[0])
            Left_ReFe0.append(ReFe[2])
            Left_ReFe_Seg0 = ['Pelvis','Patella']
            Right_ReFe0 = []
            Right_ReFe0.append(ReFe[0])
            Right_ReFe0.append(ReFe[2])
            Right_ReFe_Seg0 = ['Pelvis','Patella']  
                
            [LeftReFe,LeftReFeMusclePoints] = math.ComputeMuscleLength('Left',Left_ReFe,Left_ReFe_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightReFe,RightReFeMusclePoints] = math.ComputeMuscleLength('Right',Right_ReFe,Right_ReFe_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftReFe0,LeftReFeMusclePoints0] = math.ComputeMuscleLength('Left',Left_ReFe0,Left_ReFe_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightReFe0,RightReFeMusclePoints0]= math.ComputeMuscleLength('Right',Right_ReFe0,Right_ReFe_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            # Remove points depending on knee flexion
            Left_VaLa = []
            if LKF < 110:
                if LKF < 69:
                    Left_VaLa.append(VaLa[0])
                    Left_VaLa.append(VaLa[1])
                    Left_VaLa.append(VaLa[4])
                    Left_VaLa_Seg = ['Thigh','Thigh','Patella']
                else:
                    Left_VaLa.append(VaLa[0])
                    Left_VaLa.append(VaLa[1])
                    Left_VaLa.append(VaLa[2])
                    Left_VaLa.append(VaLa[4])
                    Left_VaLa_Seg = ['Thigh','Thigh','Thigh','Patella']
            else:
                Left_VaLa = VaLa
                Left_VaLa_Seg = VaLa_Seg
            Right_VaLa = []
            if RKF < 110:
                if RKF < 69:
                    Right_VaLa.append(VaLa[0])
                    Right_VaLa.append(VaLa[1])
                    Right_VaLa.append(VaLa[4])
                    Right_VaLa_Seg = ['Thigh','Thigh','Patella']
                else:
                    Right_VaLa.append(VaLa[0])
                    Right_VaLa.append(VaLa[1])
                    Right_VaLa.append(VaLa[2])
                    Right_VaLa.append(VaLa[4])
                    Right_VaLa_Seg = ['Thigh','Thigh','Thigh','Patella']
            else:
                Right_VaLa = VaLa
                Right_VaLa_Seg = VaLa_Seg
            
            Left_VaLa0 = []
            Left_VaLa0.append(VaLa[0])
            Left_VaLa0.append(VaLa[1])
            Left_VaLa0.append(VaLa[4])
            Left_VaLa_Seg0 = ['Thigh','Thigh','Patella']
            Right_VaLa0 = []
            Right_VaLa0.append(VaLa[0])
            Right_VaLa0.append(VaLa[1])
            Right_VaLa0.append(VaLa[4])
            Right_VaLa_Seg0 = ['Thigh','Thigh','Patella']
                    
            [LeftVaLa,LeftVaLaMusclePoints] = math.ComputeMuscleLength('Left',Left_VaLa,Left_VaLa_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightVaLa,RightVaLaMusclePoints] = math.ComputeMuscleLength('Right',Right_VaLa,Right_VaLa_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftVaLa0,LeftVaLaMusclePoints0] = math.ComputeMuscleLength('Left',Left_VaLa0,Left_VaLa_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightVaLa0,RightVaLaMusclePoints0]= math.ComputeMuscleLength('Right',Right_VaLa0,Right_VaLa_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            # Remove points depending on knee flexion
            Left_GaMe = []
            if LKF > 44:
                Left_GaMe.append(GaMe[0])
                Left_GaMe.append(GaMe[2])
                Left_GaMe.append(GaMe[3])
                Left_GaMe_Seg = ['Thigh','Shank','Calcaneus']
            else:
                Left_GaMe = GaMe
                Left_GaMe_Seg = GaMe_Seg
            Right_GaMe = []
            if RKF > 44:
                Right_GaMe.append(GaMe[0])
                Right_GaMe.append(GaMe[2])
                Right_GaMe.append(GaMe[3])
                Right_GaMe_Seg = ['Thigh','Shank','Calcaneus']
            else:
                Right_GaMe = GaMe
                Right_GaMe_Seg = GaMe_Seg
  
            Left_GaMe0 = GaMe
            Left_GaMe_Seg0 = GaMe_Seg
            Right_GaMe0 = GaMe
            Right_GaMe_Seg0 = GaMe_Seg
                
            [LeftGaMe,LeftGaMeMusclePoints] = math.ComputeMuscleLength('Left',Left_GaMe,Left_GaMe_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightGaMe,RightGaMeMusclePoints] = math.ComputeMuscleLength('Right',Right_GaMe,Right_GaMe_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftGaMe0,LeftGaMeMusclePoints0] = math.ComputeMuscleLength('Left',Left_GaMe0,Left_GaMe_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightGaMe0,RightGaMeMusclePoints0]= math.ComputeMuscleLength('Right',Right_GaMe0,Right_GaMe_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            # Remove points depending on knee flexion
            Left_GaLa = []
            if LKF > 44:
                Left_GaLa.append(GaLa[0])
                Left_GaLa.append(GaLa[2])
                Left_GaLa.append(GaLa[3])
                Left_GaLa_Seg = ['Thigh','Shank','Calcaneus']
            else:
                Left_GaLa = GaLa
                Left_GaLa_Seg = GaLa_Seg
            Right_GaLa = []
            if RKF > 44:
                Right_GaLa.append(GaLa[0])
                Right_GaLa.append(GaLa[2])
                Right_GaLa.append(GaLa[3])
                Right_GaLa_Seg = ['Thigh','Shank','Calcaneus']
            else:
                Right_GaLa = GaLa
                Right_GaLa_Seg = GaLa_Seg

            Left_GaLa0 = GaLa
            Left_GaLa_Seg0 = GaLa_Seg
            Right_GaLa0 = GaLa
            Right_GaLa_Seg0 = GaLa_Seg   
            
            [LeftGaLa,LeftGaLaMusclePoints] = math.ComputeMuscleLength('Left',Left_GaLa,Left_GaLa_Seg,EPelvisAnatDelp,PelvisOriginDelp,LeftEThighAnatDelp,LeftThighOriginDelp,LeftEShankAnatDelp,LeftShankOriginDelp,LeftEPatellaAnatDelp,LeftPatellaOriginDelp,LeftECalcaneusAnatDelp,LeftCalcaneusOriginDelp)
            [RightGaLa,RightGaLaMusclePoints] = math.ComputeMuscleLength('Right',Right_GaLa,Right_GaLa_Seg,EPelvisAnatDelp,PelvisOriginDelp,RightEThighAnatDelp,RightThighOriginDelp,RightEShankAnatDelp,RightShankOriginDelp,RightEPatellaAnatDelp,RightPatellaOriginDelp,RightECalcaneusAnatDelp,RightCalcaneusOriginDelp)
            [LeftGaLa0,LeftGaLaMusclePoints0] = math.ComputeMuscleLength('Left',Left_GaLa0,Left_GaLa_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,LeftEThighAnatDelp0,LeftThighOriginDelp0,LeftEShankAnatDelp0,LeftShankOriginDelp0,LeftEPatellaAnatDelp0,LeftPatellaOriginDelp0,LeftECalcaneusAnatDelp0,LeftCalcaneusOriginDelp0)
            [RightGaLa0,RightGaLaMusclePoints0]= math.ComputeMuscleLength('Right',Right_GaLa0,Right_GaLa_Seg0,EPelvisAnatDelp0,PelvisOriginDelp0,RightEThighAnatDelp0,RightThighOriginDelp0,RightEShankAnatDelp0,RightShankOriginDelp0,RightEPatellaAnatDelp0,RightPatellaOriginDelp0,RightECalcaneusAnatDelp0,RightCalcaneusOriginDelp0)
            
            # Fill Arrays to write Joint Centers to C3D File
            arrayLeftHipCenter[0][FrameNumber] = Direction * LeftHipCenterLab[0]
            arrayLeftHipCenter[1][FrameNumber] = Direction * LeftHipCenterLab[1]
            arrayLeftHipCenter[2][FrameNumber] = LeftHipCenterLab[2]
            
            arrayRightHipCenter[0][FrameNumber] = Direction * RightHipCenterLab[0]
            arrayRightHipCenter[1][FrameNumber] = Direction * RightHipCenterLab[1]
            arrayRightHipCenter[2][FrameNumber] = RightHipCenterLab[2]
            
            arrayLeftKneeCenter[0][FrameNumber] = Direction * LeftKneeCenterLab[0]
            arrayLeftKneeCenter[1][FrameNumber] = Direction * LeftKneeCenterLab[1]
            arrayLeftKneeCenter[2][FrameNumber] = LeftKneeCenterLab[2]
            
            arrayRightKneeCenter[0][FrameNumber] = Direction * RightKneeCenterLab[0]
            arrayRightKneeCenter[1][FrameNumber] = Direction * RightKneeCenterLab[1]
            arrayRightKneeCenter[2][FrameNumber] = RightKneeCenterLab[2]
            
            arrayLeftAnkleCenter[0][FrameNumber] = Direction * LeftAnkleCenterLab[0]
            arrayLeftAnkleCenter[1][FrameNumber] = Direction * LeftAnkleCenterLab[1]
            arrayLeftAnkleCenter[2][FrameNumber] = LeftAnkleCenterLab[2]
            
            arrayRightAnkleCenter[0][FrameNumber] = Direction * RightAnkleCenterLab[0]
            arrayRightAnkleCenter[1][FrameNumber] = Direction * RightAnkleCenterLab[1]
            arrayRightAnkleCenter[2][FrameNumber] = RightAnkleCenterLab[2]
            
            # ASI, KNE, ANK markers for MAPS
            arrayLeftASIS[0][FrameNumber] = Direction * LeftASISMarker[0]
            arrayLeftASIS[1][FrameNumber] = Direction * LeftASISMarker[1]
            arrayLeftASIS[2][FrameNumber] = LeftASISMarker[2]
            
            arrayRightASIS[0][FrameNumber] = Direction * RightASISMarker[0]
            arrayRightASIS[1][FrameNumber] = Direction * RightASISMarker[1]
            arrayRightASIS[2][FrameNumber] = RightASISMarker[2]
            
            arrayLeftKNE[0][FrameNumber] = Direction * LeftLateralKneeMarker[0]
            arrayLeftKNE[1][FrameNumber] = Direction * LeftLateralKneeMarker[1]
            arrayLeftKNE[2][FrameNumber] = LeftLateralKneeMarker[2]
            
            arrayRightKNE[0][FrameNumber] = Direction * RightLateralKneeMarker[0]
            arrayRightKNE[1][FrameNumber] = Direction * RightLateralKneeMarker[1]
            arrayRightKNE[2][FrameNumber] = RightLateralKneeMarker[2]
            
            arrayLeftANK[0][FrameNumber] = Direction * LeftLateralAnkleMarker[0]
            arrayLeftANK[1][FrameNumber] = Direction * LeftLateralAnkleMarker[1]
            arrayLeftANK[2][FrameNumber] = LeftLateralAnkleMarker[2]
            
            arrayRightANK[0][FrameNumber] = Direction * RightLateralAnkleMarker[0]
            arrayRightANK[1][FrameNumber] = Direction * RightLateralAnkleMarker[1]
            arrayRightANK[2][FrameNumber] = RightLateralAnkleMarker[2]
            
            # Upper Posterior Calcaneus Marker for SLC
            if self.valueLeftFootModelCheck == '1':
                arrayLeftUpperPCAL[0][FrameNumber] = Direction * LeftUpperPosteriorCalcaneusMarker[0]
                arrayLeftUpperPCAL[1][FrameNumber] = Direction * LeftUpperPosteriorCalcaneusMarker[1]
                arrayLeftUpperPCAL[2][FrameNumber] = LeftUpperPosteriorCalcaneusMarker[2]
            if self.valueRightFootModelCheck == '1':
                arrayRightUpperPCAL[0][FrameNumber] = Direction * RightUpperPosteriorCalcaneusMarker[0]
                arrayRightUpperPCAL[1][FrameNumber] = Direction * RightUpperPosteriorCalcaneusMarker[1]
                arrayRightUpperPCAL[2][FrameNumber] = RightUpperPosteriorCalcaneusMarker[2]
            # Pelvis Origin for SLC
            arrayPelvisOrigin[0][FrameNumber] = (arrayLeftHipCenter[0][FrameNumber] + arrayRightHipCenter[0][FrameNumber])/2
            arrayPelvisOrigin[1][FrameNumber] = (arrayLeftHipCenter[1][FrameNumber] + arrayRightHipCenter[1][FrameNumber])/2
            arrayPelvisOrigin[2][FrameNumber] = (arrayLeftHipCenter[2][FrameNumber] + arrayRightHipCenter[2][FrameNumber])/2

            
            # Fill Arrays to write Segment Angles to C3D File
            #Left
            arrayLeftTrunkAngles[0][FrameNumber] = LeftTrunkAnglesDeg[0]
            arrayLeftTrunkAngles[1][FrameNumber] = LeftTrunkAnglesDeg[1]
            arrayLeftTrunkAngles[2][FrameNumber] = LeftTrunkAnglesDeg[2]
            
            arrayLeftTrunkAnglesTOR[0][FrameNumber] = LeftTrunkAnglesTORDeg[0]
            arrayLeftTrunkAnglesTOR[1][FrameNumber] = LeftTrunkAnglesTORDeg[1]
            arrayLeftTrunkAnglesTOR[2][FrameNumber] = LeftTrunkAnglesTORDeg[2]
            
            arrayLeftTrunkAnglesROT[0][FrameNumber] = LeftTrunkAnglesROTDeg[0]
            arrayLeftTrunkAnglesROT[1][FrameNumber] = LeftTrunkAnglesROTDeg[1]
            arrayLeftTrunkAnglesROT[2][FrameNumber] = LeftTrunkAnglesROTDeg[2]
            
            arrayLeftPelvisAngles[0][FrameNumber] = LeftPelvisAnglesDeg[0]
            arrayLeftPelvisAngles[1][FrameNumber] = LeftPelvisAnglesDeg[1]
            arrayLeftPelvisAngles[2][FrameNumber] = LeftPelvisAnglesDeg[2]
            
            arrayLeftPelvisAnglesTOR[0][FrameNumber] = LeftPelvisAnglesTORDeg[0]
            arrayLeftPelvisAnglesTOR[1][FrameNumber] = LeftPelvisAnglesTORDeg[1]
            arrayLeftPelvisAnglesTOR[2][FrameNumber] = LeftPelvisAnglesTORDeg[2]
            
            arrayLeftPelvisAnglesROT[0][FrameNumber] = LeftPelvisAnglesROTDeg[0]
            arrayLeftPelvisAnglesROT[1][FrameNumber] = LeftPelvisAnglesROTDeg[1]
            arrayLeftPelvisAnglesROT[2][FrameNumber] = LeftPelvisAnglesROTDeg[2]
            
            arrayLeftThighAngles[0][FrameNumber] = LeftThighAnglesDeg[0]
            arrayLeftThighAngles[1][FrameNumber] = LeftThighAnglesDeg[1]
            arrayLeftThighAngles[2][FrameNumber] = LeftThighAnglesDeg[2]
            
            arrayLeftShankAngles[0][FrameNumber] = LeftShankAnglesDeg[0]
            arrayLeftShankAngles[1][FrameNumber] = LeftShankAnglesDeg[1]
            arrayLeftShankAngles[2][FrameNumber] = LeftShankAnglesDeg[2]
            
            arrayLeftFootAngles[0][FrameNumber] = LeftFootAnglesDeg[0]
            arrayLeftFootAngles[1][FrameNumber] = LeftFootAnglesDeg[1]
            arrayLeftFootAngles[2][FrameNumber] = LeftFootAnglesDeg[2]
            
            if self.valueLeftFootModelCheck == '1':
                arrayLeftHindfootAngles[0][FrameNumber] = LeftHindfootAnglesRelHFProgressionDeg[0]
                arrayLeftHindfootAngles[1][FrameNumber] = LeftHindfootAnglesRelHFProgressionDeg[1]
                #arrayLeftHindfootAngles[0][FrameNumber] = LeftHindfootAnglesDeg[0]
                #arrayLeftHindfootAngles[1][FrameNumber] = LeftHindfootAnglesDeg[1]
                arrayLeftHindfootAngles[2][FrameNumber] = LeftHindfootAnglesDeg[2]
                
                arrayLeftForefootAngles[0][FrameNumber] = LeftForefootAnglesRelHFProgressionDeg[0]
                arrayLeftForefootAngles[1][FrameNumber] = LeftForefootAnglesRelHFProgressionDeg[1]
                #arrayLeftForefootAngles[0][FrameNumber] = LeftForefootAnglesDeg[0]
                #arrayLeftForefootAngles[1][FrameNumber] = LeftForefootAnglesDeg[1]
                arrayLeftForefootAngles[2][FrameNumber] = LeftForefootAnglesDeg[2]
                
                arrayLeftHalluxAngles[0][FrameNumber] = LeftHalluxAnglesRelHFProgressionDeg[0]
                arrayLeftHalluxAngles[1][FrameNumber] = LeftHalluxAnglesRelHFProgressionDeg[1]
                #arrayLeftHalluxAngles[0][FrameNumber] = LeftHalluxAnglesDeg[0]
                #arrayLeftHalluxAngles[1][FrameNumber] = LeftHalluxAnglesDeg[1]
                arrayLeftHalluxAngles[2][FrameNumber] = LeftHalluxAnglesDeg[2]
            
            
            # Left Angles in Radians
            arrayLeftTrunkAnglesRad[0][FrameNumber] = LeftTrunkAnglesRad[0]
            arrayLeftTrunkAnglesRad[1][FrameNumber] = LeftTrunkAnglesRad[1]
            arrayLeftTrunkAnglesRad[2][FrameNumber] = LeftTrunkAnglesRad[2]
            
            arrayLeftPelvisAnglesRad[0][FrameNumber] = LeftPelvisAnglesRad[0]
            arrayLeftPelvisAnglesRad[1][FrameNumber] = LeftPelvisAnglesRad[1]
            arrayLeftPelvisAnglesRad[2][FrameNumber] = LeftPelvisAnglesRad[2]
            
            arrayLeftThighAnglesRad[0][FrameNumber] = LeftThighAnglesRad[0]
            arrayLeftThighAnglesRad[1][FrameNumber] = LeftThighAnglesRad[1]
            arrayLeftThighAnglesRad[2][FrameNumber] = LeftThighAnglesRad[2]
            
            arrayLeftShankAnglesRad[0][FrameNumber] = LeftShankAnglesRad[0]
            arrayLeftShankAnglesRad[1][FrameNumber] = LeftShankAnglesRad[1]
            arrayLeftShankAnglesRad[2][FrameNumber] = LeftShankAnglesRad[2]
            
            arrayLeftFootAnglesRad[0][FrameNumber] = LeftFootAnglesRad[0]
            arrayLeftFootAnglesRad[1][FrameNumber] = LeftFootAnglesRad[1]
            arrayLeftFootAnglesRad[2][FrameNumber] = LeftFootAnglesRad[2]
            
            if self.valueLeftFootModelCheck == '1':
                arrayLeftHindfootAnglesRad[0][FrameNumber] = LeftHindfootAnglesRad[0]
                arrayLeftHindfootAnglesRad[1][FrameNumber] = LeftHindfootAnglesRad[1]
                arrayLeftHindfootAnglesRad[2][FrameNumber] = LeftHindfootAnglesRad[2]
                
                arrayLeftForefootAnglesRad[0][FrameNumber] = LeftForefootAnglesRad[0]
                arrayLeftForefootAnglesRad[1][FrameNumber] = LeftForefootAnglesRad[1]
                arrayLeftForefootAnglesRad[2][FrameNumber] = LeftForefootAnglesRad[2]
                
                arrayLeftHalluxAnglesRad[0][FrameNumber] = LeftHalluxAnglesRad[0]
                arrayLeftHalluxAnglesRad[1][FrameNumber] = LeftHalluxAnglesRad[1]
                arrayLeftHalluxAnglesRad[2][FrameNumber] = LeftHalluxAnglesRad[2]
            
            
            #Right
            arrayRightTrunkAngles[0][FrameNumber] = RightTrunkAnglesDeg[0]
            arrayRightTrunkAngles[1][FrameNumber] = RightTrunkAnglesDeg[1]
            arrayRightTrunkAngles[2][FrameNumber] = RightTrunkAnglesDeg[2]
            
            arrayRightTrunkAnglesTOR[0][FrameNumber] = RightTrunkAnglesTORDeg[0]
            arrayRightTrunkAnglesTOR[1][FrameNumber] = RightTrunkAnglesTORDeg[1]
            arrayRightTrunkAnglesTOR[2][FrameNumber] = RightTrunkAnglesTORDeg[2]
            
            arrayRightTrunkAnglesROT[0][FrameNumber] = RightTrunkAnglesROTDeg[0]
            arrayRightTrunkAnglesROT[1][FrameNumber] = RightTrunkAnglesROTDeg[1]
            arrayRightTrunkAnglesROT[2][FrameNumber] = RightTrunkAnglesROTDeg[2]
            
            arrayRightPelvisAngles[0][FrameNumber] = RightPelvisAnglesDeg[0]
            arrayRightPelvisAngles[1][FrameNumber] = RightPelvisAnglesDeg[1]
            arrayRightPelvisAngles[2][FrameNumber] = RightPelvisAnglesDeg[2]
            
            arrayRightPelvisAnglesTOR[0][FrameNumber] = RightPelvisAnglesTORDeg[0]
            arrayRightPelvisAnglesTOR[1][FrameNumber] = RightPelvisAnglesTORDeg[1]
            arrayRightPelvisAnglesTOR[2][FrameNumber] = RightPelvisAnglesTORDeg[2]
            
            arrayRightPelvisAnglesROT[0][FrameNumber] = RightPelvisAnglesROTDeg[0]
            arrayRightPelvisAnglesROT[1][FrameNumber] = RightPelvisAnglesROTDeg[1]
            arrayRightPelvisAnglesROT[2][FrameNumber] = RightPelvisAnglesROTDeg[2]
            
            arrayRightThighAngles[0][FrameNumber] = RightThighAnglesDeg[0]
            arrayRightThighAngles[1][FrameNumber] = RightThighAnglesDeg[1]
            arrayRightThighAngles[2][FrameNumber] = RightThighAnglesDeg[2]
            
            arrayRightShankAngles[0][FrameNumber] = RightShankAnglesDeg[0]
            arrayRightShankAngles[1][FrameNumber] = RightShankAnglesDeg[1]
            arrayRightShankAngles[2][FrameNumber] = RightShankAnglesDeg[2]
            
            arrayRightFootAngles[0][FrameNumber] = RightFootAnglesDeg[0]
            arrayRightFootAngles[1][FrameNumber] = RightFootAnglesDeg[1]
            arrayRightFootAngles[2][FrameNumber] = RightFootAnglesDeg[2]
            
            if self.valueRightFootModelCheck == '1':
                arrayRightHindfootAngles[0][FrameNumber] = RightHindfootAnglesRelHFProgressionDeg[0]
                arrayRightHindfootAngles[1][FrameNumber] = RightHindfootAnglesRelHFProgressionDeg[1]
                #arrayRightHindfootAngles[0][FrameNumber] = RightHindfootAnglesDeg[0]
                #arrayRightHindfootAngles[1][FrameNumber] = RightHindfootAnglesDeg[1]
                arrayRightHindfootAngles[2][FrameNumber] = RightHindfootAnglesDeg[2]
                
                arrayRightForefootAngles[0][FrameNumber] = RightForefootAnglesRelHFProgressionDeg[0]
                arrayRightForefootAngles[1][FrameNumber] = RightForefootAnglesRelHFProgressionDeg[1]
                #arrayRightForefootAngles[0][FrameNumber] = RightForefootAnglesDeg[0]
                #arrayRightForefootAngles[1][FrameNumber] = RightForefootAnglesDeg[1]
                arrayRightForefootAngles[2][FrameNumber] = RightForefootAnglesDeg[2]
                
                arrayRightHalluxAngles[0][FrameNumber] = RightHalluxAnglesRelHFProgressionDeg[0]
                arrayRightHalluxAngles[1][FrameNumber] = RightHalluxAnglesRelHFProgressionDeg[1]
                #arrayRightHalluxAngles[0][FrameNumber] = RightHalluxAnglesDeg[0]
                #arrayRightHalluxAngles[1][FrameNumber] = RightHalluxAnglesDeg[1]
                arrayRightHalluxAngles[2][FrameNumber] = RightHalluxAnglesDeg[2]
            
            # Right Angles in Radians
            arrayRightTrunkAnglesRad[0][FrameNumber] = RightTrunkAnglesRad[0]
            arrayRightTrunkAnglesRad[1][FrameNumber] = RightTrunkAnglesRad[1]
            arrayRightTrunkAnglesRad[2][FrameNumber] = RightTrunkAnglesRad[2]
            
            arrayRightPelvisAnglesRad[0][FrameNumber] = RightPelvisAnglesRad[0]
            arrayRightPelvisAnglesRad[1][FrameNumber] = RightPelvisAnglesRad[1]
            arrayRightPelvisAnglesRad[2][FrameNumber] = RightPelvisAnglesRad[2]
            
            arrayRightThighAnglesRad[0][FrameNumber] = RightThighAnglesRad[0]
            arrayRightThighAnglesRad[1][FrameNumber] = RightThighAnglesRad[1]
            arrayRightThighAnglesRad[2][FrameNumber] = RightThighAnglesRad[2]
            
            arrayRightShankAnglesRad[0][FrameNumber] = RightShankAnglesRad[0]
            arrayRightShankAnglesRad[1][FrameNumber] = RightShankAnglesRad[1]
            arrayRightShankAnglesRad[2][FrameNumber] = RightShankAnglesRad[2]
            
            arrayRightFootAnglesRad[0][FrameNumber] = RightFootAnglesRad[0]
            arrayRightFootAnglesRad[1][FrameNumber] = RightFootAnglesRad[1]
            arrayRightFootAnglesRad[2][FrameNumber] = RightFootAnglesRad[2]
            
            if self.valueRightFootModelCheck == '1':
                arrayRightHindfootAnglesRad[0][FrameNumber] = RightHindfootAnglesRad[0]
                arrayRightHindfootAnglesRad[1][FrameNumber] = RightHindfootAnglesRad[1]
                arrayRightHindfootAnglesRad[2][FrameNumber] = RightHindfootAnglesRad[2]
                
                arrayRightForefootAnglesRad[0][FrameNumber] = RightForefootAnglesRad[0]
                arrayRightForefootAnglesRad[1][FrameNumber] = RightForefootAnglesRad[1]
                arrayRightForefootAnglesRad[2][FrameNumber] = RightForefootAnglesRad[2]
                
                arrayRightHalluxAnglesRad[0][FrameNumber] = RightHalluxAnglesRad[0]
                arrayRightHalluxAnglesRad[1][FrameNumber] = RightHalluxAnglesRad[1]
                arrayRightHalluxAnglesRad[2][FrameNumber] = RightHalluxAnglesRad[2]
            
            # Fill Arrays to write Joint Angles to C3D File
            #Left
            arrayLeftHipAngles[0][FrameNumber] = LeftHipAnglesDeg[0]
            arrayLeftHipAngles[1][FrameNumber] = LeftHipAnglesDeg[1]
            arrayLeftHipAngles[2][FrameNumber] = LeftHipAnglesDeg[2]
            
            arrayLeftKneeAngles[0][FrameNumber] = LeftKneeAnglesDeg[0]
            arrayLeftKneeAngles[1][FrameNumber] = LeftKneeAnglesDeg[1]
            arrayLeftKneeAngles[2][FrameNumber] = LeftKneeAnglesDeg[2]
            
            arrayLeftKneeAnglesProximal[0][FrameNumber] = LeftKneeAnglesProximalDeg[0]
            arrayLeftKneeAnglesProximal[1][FrameNumber] = LeftKneeAnglesProximalDeg[1]
            arrayLeftKneeAnglesProximal[2][FrameNumber] = LeftKneeAnglesProximalDeg[2]
            
            arrayLeftKneeAnglesDistal[0][FrameNumber] = LeftKneeAnglesDistalDeg[0]
            arrayLeftKneeAnglesDistal[1][FrameNumber] = LeftKneeAnglesDistalDeg[1]
            arrayLeftKneeAnglesDistal[2][FrameNumber] = LeftKneeAnglesDistalDeg[2]
            
            arrayLeftAnkleAngles[0][FrameNumber] = LeftAnkleAnglesDeg[0]
            arrayLeftAnkleAngles[1][FrameNumber] = LeftAnkleAnglesDeg[1]
            arrayLeftAnkleAngles[2][FrameNumber] = LeftAnkleAnglesDeg[2]
            
            if self.valueLeftFootModelCheck == '1':
                arrayLeftAnkleComplexAngles[0][FrameNumber] = LeftAnkleComplexAnglesDeg[0]
                arrayLeftAnkleComplexAngles[1][FrameNumber] = LeftAnkleComplexAnglesDeg[1]
                arrayLeftAnkleComplexAngles[2][FrameNumber] = LeftAnkleComplexAnglesDeg[2]
                
                arrayLeftMidfootAngles[0][FrameNumber] = LeftMidfootAnglesDeg[0]
                arrayLeftMidfootAngles[1][FrameNumber] = LeftMidfootAnglesDeg[1]
                arrayLeftMidfootAngles[2][FrameNumber] = LeftMidfootAnglesDeg[2]
                
                arrayLeftToesAngles[0][FrameNumber] = LeftToesAnglesDeg[0]
                arrayLeftToesAngles[1][FrameNumber] = LeftToesAnglesDeg[1]
                arrayLeftToesAngles[2][FrameNumber] = LeftToesAnglesDeg[2]
                
                arraySupination[0][FrameNumber] = np.cos(45*np.pi/180) * (LeftMidfootAnglesDeg[2] + LeftAnkleComplexAnglesDeg[0])
                arraySkew[0][FrameNumber]       = np.cos(45*np.pi/180) * (LeftMidfootAnglesDeg[2] - LeftAnkleComplexAnglesDeg[0])
            
            #Left Joint Angles in Radians
            arrayLeftHipAnglesRad[0][FrameNumber] = LeftHipAnglesRad[0]
            arrayLeftHipAnglesRad[1][FrameNumber] = LeftHipAnglesRad[1]
            arrayLeftHipAnglesRad[2][FrameNumber] = LeftHipAnglesRad[2]
            
            arrayLeftKneeAnglesRad[0][FrameNumber] = LeftKneeAnglesRad[0]
            arrayLeftKneeAnglesRad[1][FrameNumber] = LeftKneeAnglesRad[1]
            arrayLeftKneeAnglesRad[2][FrameNumber] = LeftKneeAnglesRad[2]
            
            arrayLeftAnkleAnglesRad[0][FrameNumber] = LeftAnkleAnglesRad[0]
            arrayLeftAnkleAnglesRad[1][FrameNumber] = LeftAnkleAnglesRad[1]
            arrayLeftAnkleAnglesRad[2][FrameNumber] = LeftAnkleAnglesRad[2]
            
            if self.valueLeftFootModelCheck == '1':
                arrayLeftAnkleComplexAnglesRad[0][FrameNumber] = LeftAnkleComplexAnglesRad[0]
                arrayLeftAnkleComplexAnglesRad[1][FrameNumber] = LeftAnkleComplexAnglesRad[1]
                arrayLeftAnkleComplexAnglesRad[2][FrameNumber] = LeftAnkleComplexAnglesRad[2]
                
                arrayLeftMidfootAnglesRad[0][FrameNumber] = LeftMidfootAnglesRad[0]
                arrayLeftMidfootAnglesRad[1][FrameNumber] = LeftMidfootAnglesRad[1]
                arrayLeftMidfootAnglesRad[2][FrameNumber] = LeftMidfootAnglesRad[2]
                
                arrayLeftToesAnglesRad[0][FrameNumber] = LeftToesAnglesRad[0]
                arrayLeftToesAnglesRad[1][FrameNumber] = LeftToesAnglesRad[1]
                arrayLeftToesAnglesRad[2][FrameNumber] = LeftToesAnglesRad[2]

            
            #Right
            arrayRightHipAngles[0][FrameNumber] = RightHipAnglesDeg[0]
            arrayRightHipAngles[1][FrameNumber] = RightHipAnglesDeg[1]
            arrayRightHipAngles[2][FrameNumber] = RightHipAnglesDeg[2]
            
            arrayRightKneeAngles[0][FrameNumber] = RightKneeAnglesDeg[0]
            arrayRightKneeAngles[1][FrameNumber] = RightKneeAnglesDeg[1]
            arrayRightKneeAngles[2][FrameNumber] = RightKneeAnglesDeg[2]
            
            arrayRightKneeAnglesProximal[0][FrameNumber] = RightKneeAnglesProximalDeg[0]
            arrayRightKneeAnglesProximal[1][FrameNumber] = RightKneeAnglesProximalDeg[1]
            arrayRightKneeAnglesProximal[2][FrameNumber] = RightKneeAnglesProximalDeg[2]
            
            arrayRightKneeAnglesDistal[0][FrameNumber] = RightKneeAnglesDistalDeg[0]
            arrayRightKneeAnglesDistal[1][FrameNumber] = RightKneeAnglesDistalDeg[1]
            arrayRightKneeAnglesDistal[2][FrameNumber] = RightKneeAnglesDistalDeg[2]
            
            arrayRightAnkleAngles[0][FrameNumber] = RightAnkleAnglesDeg[0]
            arrayRightAnkleAngles[1][FrameNumber] = RightAnkleAnglesDeg[1]
            arrayRightAnkleAngles[2][FrameNumber] = RightAnkleAnglesDeg[2]
            
            if self.valueRightFootModelCheck == '1':
                arrayRightAnkleComplexAngles[0][FrameNumber] = RightAnkleComplexAnglesDeg[0]
                arrayRightAnkleComplexAngles[1][FrameNumber] = RightAnkleComplexAnglesDeg[1]
                arrayRightAnkleComplexAngles[2][FrameNumber] = RightAnkleComplexAnglesDeg[2]
                
                arrayRightMidfootAngles[0][FrameNumber] = RightMidfootAnglesDeg[0]
                arrayRightMidfootAngles[1][FrameNumber] = RightMidfootAnglesDeg[1]
                arrayRightMidfootAngles[2][FrameNumber] = RightMidfootAnglesDeg[2]
                
                arrayRightToesAngles[0][FrameNumber] = RightToesAnglesDeg[0]
                arrayRightToesAngles[1][FrameNumber] = RightToesAnglesDeg[1]
                arrayRightToesAngles[2][FrameNumber] = RightToesAnglesDeg[2]
                
                arraySupination[1][FrameNumber] = np.cos(45*np.pi/180) * (RightMidfootAnglesDeg[2] + RightAnkleComplexAnglesDeg[0])
                arraySkew[1][FrameNumber]       = np.cos(45*np.pi/180) * (RightMidfootAnglesDeg[2] - RightAnkleComplexAnglesDeg[0])
            
            #Right Joint Angles in Radians
            arrayRightHipAnglesRad[0][FrameNumber] = RightHipAnglesRad[0]
            arrayRightHipAnglesRad[1][FrameNumber] = RightHipAnglesRad[1]
            arrayRightHipAnglesRad[2][FrameNumber] = RightHipAnglesRad[2]
            
            arrayRightKneeAnglesRad[0][FrameNumber] = RightKneeAnglesRad[0]
            arrayRightKneeAnglesRad[1][FrameNumber] = RightKneeAnglesRad[1]
            arrayRightKneeAnglesRad[2][FrameNumber] = RightKneeAnglesRad[2]
            
            arrayRightAnkleAnglesRad[0][FrameNumber] = RightAnkleAnglesRad[0]
            arrayRightAnkleAnglesRad[1][FrameNumber] = RightAnkleAnglesRad[1]
            arrayRightAnkleAnglesRad[2][FrameNumber] = RightAnkleAnglesRad[2]
            
            if self.valueRightFootModelCheck == '1':
                arrayRightAnkleComplexAnglesRad[0][FrameNumber] = RightAnkleComplexAnglesRad[0]
                arrayRightAnkleComplexAnglesRad[1][FrameNumber] = RightAnkleComplexAnglesRad[1]
                arrayRightAnkleComplexAnglesRad[2][FrameNumber] = RightAnkleComplexAnglesRad[2]
                
                arrayRightMidfootAnglesRad[0][FrameNumber] = RightMidfootAnglesRad[0]
                arrayRightMidfootAnglesRad[1][FrameNumber] = RightMidfootAnglesRad[1]
                arrayRightMidfootAnglesRad[2][FrameNumber] = RightMidfootAnglesRad[2]
                
                arrayRightToesAnglesRad[0][FrameNumber] = RightToesAnglesRad[0]
                arrayRightToesAnglesRad[1][FrameNumber] = RightToesAnglesRad[1]
                arrayRightToesAnglesRad[2][FrameNumber] = RightToesAnglesRad[2]
            
            # Fill Arrays to write Muscle Length in C3D File
            arrayGluteusMaxLength[0][FrameNumber] = (LeftGMaS+LeftGMaM+LeftGMaI)/(LeftGMaS0+LeftGMaM0+LeftGMaI0)
            arrayGluteusMaxLength[1][FrameNumber] = (RightGMaS+RightGMaM+RightGMaI)/(RightGMaS0+RightGMaM0+RightGMaI0)
            
            arrayIlioPsoasLength[0][FrameNumber] = (LeftIlia+LeftPsoa)/(LeftIlia0+LeftPsoa0)
            arrayIlioPsoasLength[1][FrameNumber] = (RightIlia+RightPsoa)/(RightIlia0+RightPsoa0)
            
            arrayRectFemLength[0][FrameNumber] = LeftReFe/LeftReFe0
            arrayRectFemLength[1][FrameNumber] = RightReFe/RightReFe0
            
            arrayMedHamstringLength[0][FrameNumber] = (LeftSeMe+LeftSeTe)/(LeftSeMe0+LeftSeTe0)
            arrayMedHamstringLength[1][FrameNumber] = (RightSeMe+RightSeTe)/(RightSeMe0+RightSeTe0)
            
            arrayLatHamstringLength[0][FrameNumber] = (LeftBiFL+LeftBiFS)/(LeftBiFL0+LeftBiFS0)
            arrayLatHamstringLength[1][FrameNumber] = (RightBiFL+RightBiFS)/(RightBiFL0+RightBiFS0)
            
            arrayGastrocLength[0][FrameNumber] = (LeftGaMe+LeftGaLa)/(LeftGaMe0+LeftGaLa0)
            arrayGastrocLength[1][FrameNumber] = (RightGaMe+RightGaLa)/(RightGaMe0+RightGaLa0)
            
            arraySoleusLength[0][FrameNumber] = LeftSole/LeftSole0
            arraySoleusLength[1][FrameNumber] = RightSole/RightSole0
            
            arrayTibPostLength[0][FrameNumber] = LeftTiPo/LeftTiPo0
            arrayTibPostLength[1][FrameNumber] = RightTiPo/RightTiPo0
            
            arrayPeronealLength[0][FrameNumber] = (LeftPeBr+LeftPeLn)/(LeftPeBr0+LeftPeLn0)
            arrayPeronealLength[1][FrameNumber] = (RightPeBr+RightPeLn)/(RightPeBr0+RightPeLn0)
            
            arrayVastusLatLength[0][FrameNumber] = LeftVaLa/LeftVaLa0
            arrayVastusLatLength[1][FrameNumber] = RightVaLa/RightVaLa0
            

            
            # Compute locations of segmental centers of mass 
            if TrunkFlag == 1:
                HATCenterOfMass   = math.MassCenter(ShouldersCenterLab, PelvisCenterLab, 0.374)
            else:
                HATCenterOfMass   = np.array([0.,0.,0.]) 
            LeftThighCenterOfMass = math.MassCenter(LeftHipCenterLab, LeftKneeCenterLab, 0.567)
            LeftShankCenterOfMass = math.MassCenter(LeftKneeCenterLab, LeftAnkleCenterLab, 0.567, )
            LeftFootCenterOfMass  = math.MassCenter(LeftAnkleCenterLab, LeftToeMarker, 0.5)
            RightThighCenterOfMass= math.MassCenter(RightHipCenterLab, RightKneeCenterLab, 0.567)
            RightShankCenterOfMass= math.MassCenter(RightKneeCenterLab, RightAnkleCenterLab, 0.567, )
            RightFootCenterOfMass = math.MassCenter(RightAnkleCenterLab, RightToeMarker, 0.5)
            
            # Store Center of Mass in 3D Array
            arrayHATCenterOfMass[0][FrameNumber] = Direction * HATCenterOfMass[0]
            arrayHATCenterOfMass[1][FrameNumber] = Direction * HATCenterOfMass[1]
            arrayHATCenterOfMass[2][FrameNumber] = HATCenterOfMass[2]
            
            arrayLeftThighCenterOfMass[0][FrameNumber] = Direction * LeftThighCenterOfMass[0]
            arrayLeftThighCenterOfMass[1][FrameNumber] = Direction * LeftThighCenterOfMass[1]
            arrayLeftThighCenterOfMass[2][FrameNumber] = LeftThighCenterOfMass[2]
            
            arrayLeftShankCenterOfMass[0][FrameNumber] = Direction * LeftShankCenterOfMass[0]
            arrayLeftShankCenterOfMass[1][FrameNumber] = Direction * LeftShankCenterOfMass[1]
            arrayLeftShankCenterOfMass[2][FrameNumber] = LeftShankCenterOfMass[2]
            
            arrayLeftFootCenterOfMass[0][FrameNumber] = Direction * LeftFootCenterOfMass[0]
            arrayLeftFootCenterOfMass[1][FrameNumber] = Direction * LeftFootCenterOfMass[1]
            arrayLeftFootCenterOfMass[2][FrameNumber] = LeftFootCenterOfMass[2]
            
            arrayRightThighCenterOfMass[0][FrameNumber] = Direction * RightThighCenterOfMass[0]
            arrayRightThighCenterOfMass[1][FrameNumber] = Direction * RightThighCenterOfMass[1]
            arrayRightThighCenterOfMass[2][FrameNumber] = RightThighCenterOfMass[2]
            
            arrayRightShankCenterOfMass[0][FrameNumber] = Direction * RightShankCenterOfMass[0]
            arrayRightShankCenterOfMass[1][FrameNumber] = Direction * RightShankCenterOfMass[1]
            arrayRightShankCenterOfMass[2][FrameNumber] = RightShankCenterOfMass[2]
            
            arrayRightFootCenterOfMass[0][FrameNumber] = Direction * RightFootCenterOfMass[0]
            arrayRightFootCenterOfMass[1][FrameNumber] = Direction * RightFootCenterOfMass[1]
            arrayRightFootCenterOfMass[2][FrameNumber] = RightFootCenterOfMass[2]
        
        # =============================================================================
        #         Write Kinematics Outputs to C3D File
        # =============================================================================
        ModelOutputs = vicon.GetModelOutputNames(SubjectName)
        if not 'LHJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LHJC' )
        if not 'RHJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RHJC' )
        if not 'LKJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LKJC' )
        if not 'RKJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RKJC' )
        if not 'LAJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LAJC' )
        if not 'RAJC' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RAJC' )
        
        # ASI, KNE, ANK markers for MAPS
        if not 'LASI' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LASI' )
        if not 'RASI' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RASI' )
        if not 'LKNE' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LKNE' )
        if not 'RKNE' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RKNE' )
        if not 'LANK' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'LANK' )
        if not 'RANK' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'RANK' )
        
        # PELO: Pelvic Origin Defined as Center of Hip Joints
        if not 'PELO' in ModelOutputs:
            vicon.CreateModeledMarker( SubjectName, 'PELO' )

        XYZNames = ['X','Y','Z']
        AnglesTypes = ['Angle','Angle','Angle']
                
        # Left Angles    
        if not 'LTrunkAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LTrunkAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LTrunkAnglesTOR' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LTrunkAnglesTOR', 'Angles', XYZNames, AnglesTypes)
        if not 'LTrunkAnglesROT' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LTrunkAnglesROT', 'Angles', XYZNames, AnglesTypes)
        if not 'LPelvisAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LPelvisAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LPelvisAnglesTOR' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LPelvisAnglesTOR', 'Angles', XYZNames, AnglesTypes)
        if not 'LPelvisAnglesROT' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LPelvisAnglesROT', 'Angles', XYZNames, AnglesTypes)
        if not 'LThighAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LThighAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LShankAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LShankAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LFootProgressAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LFootProgressAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LHipAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LHipAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LKneeAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LKneeAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'LKneeAnglesProximal' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LKneeAnglesProximal', 'Angles', XYZNames, AnglesTypes)
        if not 'LKneeAnglesDistal' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LKneeAnglesDistal', 'Angles', XYZNames, AnglesTypes)
        if not 'LAnkleAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LAnkleAngles', 'Angles', XYZNames, AnglesTypes)
        if self.valueLeftFootModelCheck == '1':
            if not 'LHFGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHFGA', 'Angles', XYZNames, AnglesTypes)
            if not 'LFFGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LFFGA', 'Angles', XYZNames, AnglesTypes)
            if not 'LHXGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHXGA', 'Angles', XYZNames, AnglesTypes)
            if not 'LANKA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LANKA', 'Angles', XYZNames, AnglesTypes)
            if not 'LMDFA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LMDFA', 'Angles', XYZNames, AnglesTypes)
            if not 'LHLXA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHLXA', 'Angles', XYZNames, AnglesTypes)
            # Create Modeled Marker- Upper calcaneus markers [name too long if Left_Upper_Posterior_Calcaneus]
            if self.valueLeftFootModelCheck == '1':
                if not 'Left_Superior_Calcaneus' in ModelOutputs:
                    vicon.CreateModeledMarker( SubjectName, 'Left_Superior_Calcaneus' ) 
        
        # Right Angles
        if not 'RTrunkAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RTrunkAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RTrunkAnglesTOR' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RTrunkAnglesTOR', 'Angles', XYZNames, AnglesTypes)
        if not 'RTrunkAnglesROT' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RTrunkAnglesROT', 'Angles', XYZNames, AnglesTypes)
        if not 'RPelvisAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RPelvisAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RPelvisAnglesTOR' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RPelvisAnglesTOR', 'Angles', XYZNames, AnglesTypes)
        if not 'RPelvisAnglesROT' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RPelvisAnglesROT', 'Angles', XYZNames, AnglesTypes)
        if not 'RThighAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RThighAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RShankAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RShankAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RFootProgressAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RFootProgressAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RHipAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RHipAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RKneeAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RKneeAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RKneeAnglesProximal' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RKneeAnglesProximal', 'Angles', XYZNames, AnglesTypes)
        if not 'RKneeAnglesDistal' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RKneeAnglesDistal', 'Angles', XYZNames, AnglesTypes)
        if not 'RAnkleAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RAnkleAngles', 'Angles', XYZNames, AnglesTypes)
        if self.valueRightFootModelCheck == '1':
            if not 'RHFGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHFGA', 'Angles', XYZNames, AnglesTypes)
            if not 'RFFGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RFFGA', 'Angles', XYZNames, AnglesTypes)
            if not 'RHXGA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHXGA', 'Angles', XYZNames, AnglesTypes)
            if not 'RANKA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RANKA', 'Angles', XYZNames, AnglesTypes)
            if not 'RMDFA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RMDFA', 'Angles', XYZNames, AnglesTypes)
            if not 'RHLXA' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHLXA', 'Angles', XYZNames, AnglesTypes)
            # Create Modeled Marker- Upper calcaneus markers [name too long if Right_Upper_Posterior_Calcaneus]
            if self.valueRightFootModelCheck == '1':
                if not 'Right_Superior_Calcaneus' in ModelOutputs:
                    vicon.CreateModeledMarker( SubjectName, 'Right_Superior_Calcaneus' )
                
        if self.valueLeftFootModelCheck == '1' or self.valueRightFootModelCheck == '1':
            if not 'Supination' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'Supination', 'Angles', XYZNames, AnglesTypes)
            if not 'Skew' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'Skew', 'Angles', XYZNames, AnglesTypes)
        
        # Additional Trunk Angles for MAPS
        if not 'LThoraxAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'LThoraxAngles', 'Angles', XYZNames, AnglesTypes)
        if not 'RThoraxAngles' in ModelOutputs:
            vicon.CreateModelOutput( SubjectName, 'RThoraxAngles', 'Angles', XYZNames, AnglesTypes)
        
        
        # Muscle Lengths & Velocity
        if not 'GluteusMaxLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'GluteusMaxLength', 'Angles', XYZNames, AnglesTypes)
        if not 'GluteusMaxVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'GluteusMaxVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'IlioPsoasLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'IlioPsoasLength', 'Angles', XYZNames, AnglesTypes)
        if not 'IlioPsoasVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'IlioPsoasVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'RectFemLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'RectFemLength', 'Angles', XYZNames, AnglesTypes)
        if not 'RectFemVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'RectFemVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'MedHamstringLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'MedHamstringLength', 'Angles', XYZNames, AnglesTypes)
        if not 'MedHamstringVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'MedHamstringVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'LatHamstringLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'LatHamstringLength', 'Angles', XYZNames, AnglesTypes)
        if not 'LatHamstringVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'LatHamstringVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'GastrocLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'GastrocLength', 'Angles', XYZNames, AnglesTypes)
        if not 'GastrocVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'GastrocVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'SoleusLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'SoleusLength', 'Angles', XYZNames, AnglesTypes)
        if not 'SoleusVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'SoleusVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'TibPostLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'TibPostLength', 'Angles', XYZNames, AnglesTypes)
        if not 'TibPostVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'TibPostVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'PeronealLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'PeronealLength', 'Angles', XYZNames, AnglesTypes)
        if not 'PeronealVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'PeronealVelocity', 'Angles', XYZNames, AnglesTypes)
        if not 'VastusLatLength' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'VastusLatLength', 'Angles', XYZNames, AnglesTypes)
        if not 'VastusLatVelocity' in ModelOutputs:  
            vicon.CreateModelOutput( SubjectName, 'VastusLatVelocity', 'Angles', XYZNames, AnglesTypes)


        
        
        # This function rearranges the array such that 
        # 0- Flexion
        # 1- Ab/Adduction
        # 2- Int/Ext Rotation
        def reArrangeArray(InputArray):
            ReArrangedArray = [[0. for m in range(framecount)] for n in range(3)]
            for i in range(framecount):
                ReArrangedArray[1][i] = InputArray[0][i]
                ReArrangedArray[0][i] = InputArray[1][i]
                ReArrangedArray[2][i] = InputArray[2][i]
            return ReArrangedArray
        
        # Rearrange Angles arrays before writing to C3D        
        ReArranged_arrayLeftTrunkAngles = reArrangeArray(arrayLeftTrunkAngles)
        ReArranged_arrayLeftTrunkAnglesTOR = reArrangeArray(arrayLeftTrunkAnglesTOR)
        ReArranged_arrayLeftTrunkAnglesROT = reArrangeArray(arrayLeftTrunkAnglesROT)
        ReArranged_arrayLeftPelvisAngles = reArrangeArray(arrayLeftPelvisAngles)
        ReArranged_arrayLeftPelvisAnglesTOR = reArrangeArray(arrayLeftPelvisAnglesTOR)
        ReArranged_arrayLeftPelvisAnglesROT = reArrangeArray(arrayLeftPelvisAnglesROT)
        ReArranged_arrayLeftThighAngles = reArrangeArray(arrayLeftThighAngles)
        ReArranged_arrayLeftShankAngles = reArrangeArray(arrayLeftShankAngles)
        ReArranged_arrayLeftFootAngles = reArrangeArray(arrayLeftFootAngles)
        ReArranged_arrayLeftHipAngles = reArrangeArray(arrayLeftHipAngles)
        ReArranged_arrayLeftKneeAngles = reArrangeArray(arrayLeftKneeAngles)
        ReArranged_arrayLeftKneeAnglesProximal = reArrangeArray(arrayLeftKneeAnglesProximal)
        ReArranged_arrayLeftKneeAnglesDistal = reArrangeArray(arrayLeftKneeAnglesDistal)
        ReArranged_arrayLeftAnkleAngles = reArrangeArray(arrayLeftAnkleAngles)
        if self.valueLeftFootModelCheck == '1':
            ReArranged_arrayLeftHindfootAngles = reArrangeArray(arrayLeftHindfootAngles)
            ReArranged_arrayLeftForefootAngles = reArrangeArray(arrayLeftForefootAngles)
            ReArranged_arrayLeftHalluxAngles = reArrangeArray(arrayLeftHalluxAngles)
            ReArranged_arrayLeftAnkleComplexAngles = reArrangeArray(arrayLeftAnkleComplexAngles)
            ReArranged_arrayLeftMidfootAngles = reArrangeArray(arrayLeftMidfootAngles)
            ReArranged_arrayLeftToesAngles = reArrangeArray(arrayLeftToesAngles)
        ReArranged_arrayRightTrunkAngles = reArrangeArray(arrayRightTrunkAngles)
        ReArranged_arrayRightTrunkAnglesTOR = reArrangeArray(arrayRightTrunkAnglesTOR)
        ReArranged_arrayRightTrunkAnglesROT = reArrangeArray(arrayRightTrunkAnglesROT)
        ReArranged_arrayRightPelvisAngles = reArrangeArray(arrayRightPelvisAngles)
        ReArranged_arrayRightPelvisAnglesTOR = reArrangeArray(arrayRightPelvisAnglesTOR)
        ReArranged_arrayRightPelvisAnglesROT = reArrangeArray(arrayRightPelvisAnglesROT)
        ReArranged_arrayRightThighAngles = reArrangeArray(arrayRightThighAngles)
        ReArranged_arrayRightShankAngles = reArrangeArray(arrayRightShankAngles)
        ReArranged_arrayRightFootAngles = reArrangeArray(arrayRightFootAngles)
        ReArranged_arrayRightHipAngles = reArrangeArray(arrayRightHipAngles)
        ReArranged_arrayRightKneeAngles = reArrangeArray(arrayRightKneeAngles)
        ReArranged_arrayRightKneeAnglesProximal = reArrangeArray(arrayRightKneeAnglesProximal)
        ReArranged_arrayRightKneeAnglesDistal = reArrangeArray(arrayRightKneeAnglesDistal)
        ReArranged_arrayRightAnkleAngles = reArrangeArray(arrayRightAnkleAngles)
        if self.valueRightFootModelCheck == '1':
            ReArranged_arrayRightHindfootAngles = reArrangeArray(arrayRightHindfootAngles)
            ReArranged_arrayRightForefootAngles = reArrangeArray(arrayRightForefootAngles)
            ReArranged_arrayRightHalluxAngles = reArrangeArray(arrayRightHalluxAngles)
            ReArranged_arrayRightAnkleComplexAngles = reArrangeArray(arrayRightAnkleComplexAngles)
            ReArranged_arrayRightMidfootAngles = reArrangeArray(arrayRightMidfootAngles)
            ReArranged_arrayRightToesAngles = reArrangeArray(arrayRightToesAngles)
        
        # Write Arrays to C3D Files
        # Joint Centers
        vicon.SetModelOutput(SubjectName, 'LHJC', arrayLeftHipCenter,   exists )
        vicon.SetModelOutput(SubjectName, 'RHJC', arrayRightHipCenter,  exists )
        vicon.SetModelOutput(SubjectName, 'LKJC', arrayLeftKneeCenter,  exists )
        vicon.SetModelOutput(SubjectName, 'RKJC', arrayRightKneeCenter, exists )
        vicon.SetModelOutput(SubjectName, 'LAJC', arrayLeftAnkleCenter, exists )
        vicon.SetModelOutput(SubjectName, 'RAJC', arrayRightAnkleCenter,exists )
        
        # ASI markers for MAPS
        vicon.SetModelOutput(SubjectName, 'LASI', arrayLeftASIS,   exists )
        vicon.SetModelOutput(SubjectName, 'RASI', arrayRightASIS,   exists )
        vicon.SetModelOutput(SubjectName, 'LKNE', arrayLeftKNE,   exists )
        vicon.SetModelOutput(SubjectName, 'RKNE', arrayRightKNE,   exists )
        vicon.SetModelOutput(SubjectName, 'LANK', arrayLeftANK,   exists )
        vicon.SetModelOutput(SubjectName, 'RANK', arrayRightANK,   exists )
        
        # Upper Calcaneus and Pelvis Origin [PELO]
        vicon.SetModelOutput(SubjectName, 'PELO', arrayPelvisOrigin, exists)
        if self.valueLeftFootModelCheck == '1':
            vicon.SetModelOutput(SubjectName, 'Left_Superior_Calcaneus', arrayLeftUpperPCAL, exists)
        if self.valueRightFootModelCheck == '1':
            vicon.SetModelOutput(SubjectName, 'Right_Superior_Calcaneus', arrayRightUpperPCAL, exists)
        
        # Left Angles   
        vicon.SetModelOutput(SubjectName, 'LTrunkAngles',    ReArranged_arrayLeftTrunkAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'LTrunkAnglesTOR',    ReArranged_arrayLeftTrunkAnglesTOR,   exists)
        vicon.SetModelOutput(SubjectName, 'LTrunkAnglesROT',    ReArranged_arrayLeftTrunkAnglesROT,   exists)
        vicon.SetModelOutput(SubjectName, 'LPelvisAngles',   ReArranged_arrayLeftPelvisAngles,  exists)
        vicon.SetModelOutput(SubjectName, 'LPelvisAnglesTOR',   ReArranged_arrayLeftPelvisAnglesTOR,  exists)
        vicon.SetModelOutput(SubjectName, 'LPelvisAnglesROT',   ReArranged_arrayLeftPelvisAnglesROT,  exists)
        vicon.SetModelOutput(SubjectName, 'LThighAngles',    ReArranged_arrayLeftThighAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'LShankAngles',    ReArranged_arrayLeftShankAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'LFootProgressAngles',     ReArranged_arrayLeftFootAngles,    exists)
        vicon.SetModelOutput(SubjectName, 'LHipAngles',      ReArranged_arrayLeftHipAngles,     exists)
        vicon.SetModelOutput(SubjectName, 'LKneeAngles',     ReArranged_arrayLeftKneeAngles,    exists)
        vicon.SetModelOutput(SubjectName, 'LKneeAnglesProximal',     ReArranged_arrayLeftKneeAnglesProximal,    exists)
        vicon.SetModelOutput(SubjectName, 'LKneeAnglesDistal',     ReArranged_arrayLeftKneeAnglesDistal,    exists)
        vicon.SetModelOutput(SubjectName, 'LAnkleAngles',    ReArranged_arrayLeftAnkleAngles,   exists)
        if self.valueLeftFootModelCheck == '1':
            vicon.SetModelOutput(SubjectName, 'LHFGA',     ReArranged_arrayLeftHindfootAngles,    exists)
            vicon.SetModelOutput(SubjectName, 'LFFGA',     ReArranged_arrayLeftForefootAngles,    exists)
            vicon.SetModelOutput(SubjectName, 'LHXGA',     ReArranged_arrayLeftHalluxAngles,      exists)
            vicon.SetModelOutput(SubjectName, 'LANKA',     ReArranged_arrayLeftAnkleComplexAngles,   exists)
            vicon.SetModelOutput(SubjectName, 'LMDFA',     ReArranged_arrayLeftMidfootAngles,   exists)
            vicon.SetModelOutput(SubjectName, 'LHLXA',     ReArranged_arrayLeftToesAngles,   exists)

        # Right Angles
        vicon.SetModelOutput(SubjectName, 'RTrunkAngles',    ReArranged_arrayRightTrunkAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'RTrunkAnglesTOR',    ReArranged_arrayRightTrunkAnglesTOR,   exists)
        vicon.SetModelOutput(SubjectName, 'RTrunkAnglesROT',    ReArranged_arrayRightTrunkAnglesROT,   exists)
        vicon.SetModelOutput(SubjectName, 'RPelvisAngles',   ReArranged_arrayRightPelvisAngles,  exists)
        vicon.SetModelOutput(SubjectName, 'RPelvisAnglesTOR',   ReArranged_arrayRightPelvisAnglesTOR,  exists)
        vicon.SetModelOutput(SubjectName, 'RPelvisAnglesROT',   ReArranged_arrayRightPelvisAnglesROT,  exists)
        vicon.SetModelOutput(SubjectName, 'RThighAngles',    ReArranged_arrayRightThighAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'RShankAngles',    ReArranged_arrayRightShankAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'RFootProgressAngles',     ReArranged_arrayRightFootAngles,    exists)
        vicon.SetModelOutput(SubjectName, 'RHipAngles',      ReArranged_arrayRightHipAngles,     exists)
        vicon.SetModelOutput(SubjectName, 'RKneeAngles',     ReArranged_arrayRightKneeAngles,    exists)
        vicon.SetModelOutput(SubjectName, 'RKneeAnglesProximal',     ReArranged_arrayRightKneeAnglesProximal,    exists)
        vicon.SetModelOutput(SubjectName, 'RKneeAnglesDistal',     ReArranged_arrayRightKneeAnglesDistal,    exists)
        vicon.SetModelOutput(SubjectName, 'RAnkleAngles',    ReArranged_arrayRightAnkleAngles,   exists)
        if self.valueRightFootModelCheck == '1':
            vicon.SetModelOutput(SubjectName, 'RHFGA',     ReArranged_arrayRightHindfootAngles,    exists)
            vicon.SetModelOutput(SubjectName, 'RFFGA',     ReArranged_arrayRightForefootAngles,    exists)
            vicon.SetModelOutput(SubjectName, 'RHXGA',     ReArranged_arrayRightHalluxAngles,      exists)
            vicon.SetModelOutput(SubjectName, 'RANKA',     ReArranged_arrayRightAnkleComplexAngles,   exists)
            vicon.SetModelOutput(SubjectName, 'RMDFA',     ReArranged_arrayRightMidfootAngles,   exists)
            vicon.SetModelOutput(SubjectName, 'RHLXA',     ReArranged_arrayRightToesAngles,   exists)
    
        if self.valueLeftFootModelCheck == '1' or self.valueRightFootModelCheck == '1':
            vicon.SetModelOutput(SubjectName, 'Supination',     arraySupination,    exists)
            vicon.SetModelOutput(SubjectName, 'Skew',     arraySkew,    exists)
        
        # Additional Trunk Angles for MAPS
        vicon.SetModelOutput(SubjectName, 'LThoraxAngles',    ReArranged_arrayLeftTrunkAngles,   exists)
        vicon.SetModelOutput(SubjectName, 'RThoraxAngles',    ReArranged_arrayRightTrunkAngles,   exists)
        
        # Write Muscle Lengths and Velocity
        MarkerFrameRate = vicon.GetFrameRate()
        DeltaTime = 1.0 / MarkerFrameRate
        
        vicon.SetModelOutput(SubjectName, 'GluteusMaxLength',     arrayGluteusMaxLength,    exists) 
        [arrayGluteusMaxVelocity,arrayGluteusMaxAcceleration] = math.Differentiate(arrayGluteusMaxLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'GluteusMaxVelocity',     arrayGluteusMaxVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'IlioPsoasLength',     arrayIlioPsoasLength,    exists) 
        [arrayIlioPsoasVelocity,arrayIlioPsoasAcceleration] = math.Differentiate(arrayIlioPsoasLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'IlioPsoasVelocity',     arrayIlioPsoasVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'RectFemLength',     arrayRectFemLength,    exists) 
        [arrayRectFemVelocity,arrayRectFemAcceleration] = math.Differentiate(arrayRectFemLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'RectFemVelocity',     arrayRectFemVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'MedHamstringLength',     arrayMedHamstringLength,    exists) 
        [arrayMedHamstringVelocity,arrayMedHamstringAcceleration] = math.Differentiate(arrayMedHamstringLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'MedHamstringVelocity',     arrayMedHamstringVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'LatHamstringLength',     arrayLatHamstringLength,    exists) 
        [arrayLatHamstringVelocity,arrayLatHamstringAcceleration] = math.Differentiate(arrayLatHamstringLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'LatHamstringVelocity',     arrayLatHamstringVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'GastrocLength',     arrayGastrocLength,    exists) 
        [arrayGastrocVelocity,arrayGastrocAcceleration] = math.Differentiate(arrayGastrocLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'GastrocVelocity',     arrayGastrocVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'SoleusLength',     arraySoleusLength,    exists) 
        [arraySoleusVelocity,arraySoleusAcceleration] = math.Differentiate(arraySoleusLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'SoleusVelocity',     arraySoleusVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'TibPostLength',     arrayTibPostLength,    exists) 
        [arrayTibPostVelocity,arrayTibPostAcceleration] = math.Differentiate(arrayTibPostLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'TibPostVelocity',     arrayTibPostVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'PeronealLength',     arrayPeronealLength,    exists) 
        [arrayPeronealVelocity,arrayPeronealAcceleration] = math.Differentiate(arrayPeronealLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'PeronealVelocity',     arrayPeronealVelocity,    exists)
        
        vicon.SetModelOutput(SubjectName, 'VastusLatLength',     arrayVastusLatLength,    exists) 
        [arrayVastusLatVelocity,arrayVastusLatAcceleration] = math.Differentiate(arrayVastusLatLength, StartFrame, EndFrame, framecount, DeltaTime)
        vicon.SetModelOutput(SubjectName, 'VastusLatVelocity',     arrayVastusLatVelocity,    exists)

        
        # =============================================================================
        #     Kinetics       
        # =============================================================================
                  
        # Check for Force Plate Hits
        LeftForcePlate_DeviceID = 0 #Default Value if Force Plate Hit is not Found
        RightForcePlate_DeviceID = 0 #Default Value if Force Plate Hit is not Found
                
        DeviceIDs = vicon.GetDeviceIDs()
        for DeviceID in DeviceIDs:
            [name, type, rate, deviceOutputIDs, forceplate, eyetracker] = vicon.GetDeviceDetails(DeviceID)
            #print forceplate.Context
            if forceplate.Context == 'Left':
                LeftForcePlate_DeviceID = DeviceID
                Left_forceplate = forceplate
                #print('Left',string.split(DeviceNames[i])[0])
            if forceplate.Context == 'Right':
                RightForcePlate_DeviceID = DeviceID
                Right_forceplate = forceplate
                #print('Right',string.split(DeviceNames[i])[0])
        
        #print LeftForcePlate_DeviceID, RightForcePlate_DeviceID
        
        
        # =============================================================================
        #         # Compute Kinematic Derivatives
        # =============================================================================
        MarkerFrameRate = vicon.GetFrameRate()
        DeltaTime = 1.0 / MarkerFrameRate
        #Polynomial Order for Smoothing and Differentiating
        Order = 3
        WindowWidth = 21 # Use Odd Number 
        
        if not LeftForcePlate_DeviceID == 0:
            #==================== Smooth Data before Differentiating ======================
            # Center of Mass
            arrayHATCenterOfMass = math.Smooth3DArray(arrayHATCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftThighCenterOfMass = math.Smooth3DArray(arrayLeftThighCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftShankCenterOfMass = math.Smooth3DArray(arrayLeftShankCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftFootCenterOfMass = math.Smooth3DArray(arrayLeftFootCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            # Joint Centers
            arrayLeftHipCenter = math.Smooth3DArray(arrayLeftHipCenter, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftKneeCenter = math.Smooth3DArray(arrayLeftKneeCenter, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftAnkleCenter = math.Smooth3DArray(arrayLeftAnkleCenter, StartFrame, EndFrame, Order, WindowWidth)
            # Left Angles
            arrayLeftTrunkAngles = math.Smooth3DArray(arrayLeftTrunkAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftPelvisAngles = math.Smooth3DArray(arrayLeftPelvisAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftThighAngles = math.Smooth3DArray(arrayLeftThighAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftShankAngles = math.Smooth3DArray(arrayLeftShankAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftFootAngles = math.Smooth3DArray(arrayLeftFootAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftHipAngles = math.Smooth3DArray(arrayLeftHipAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftKneeAngles = math.Smooth3DArray(arrayLeftKneeAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayLeftAnkleAngles = math.Smooth3DArray(arrayLeftAnkleAngles, StartFrame, EndFrame, Order, WindowWidth)
            
            # ======================== Translation Variables Differentiatition ===============================
            # Center of Mass
            [arrayHATLinearVelocityLab , arrayHATLinearAccelerationLab ] = math.Differentiate(arrayHATCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftThighLinearVelocityLab , arrayLeftThighLinearAccelerationLab ] = math.Differentiate(arrayLeftThighCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftShankLinearVelocityLab , arrayLeftShankLinearAccelerationLab ] = math.Differentiate(arrayLeftShankCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftFootLinearVelocityLab , arrayLeftFootLinearAccelerationLab ] = math.Differentiate(arrayLeftFootCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            # Joint Centers
            [arrayLeftHipCenterLinearVelocityLab , arrayLeftHipCenterLinearAccelerationLab ] = math.Differentiate(arrayLeftHipCenter, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftKneeCenterLinearVelocityLab , arrayLeftKneeCenterLinearAccelerationLab ] = math.Differentiate(arrayLeftKneeCenter, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftAnkleCenterLinearVelocityLab , arrayLeftAnkleCenterLinearAccelerationLab ] = math.Differentiate(arrayLeftAnkleCenter, StartFrame, EndFrame, framecount, DeltaTime)
            
            # ======================== Rotational Variables Differentiatition ===============================
            # Left Angles  Derivatives. Derivatives are in Reference Coordinate System. For segment- Lab CS. For Joints- Proximal Segment CS
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftTrunkAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftTrunkAnglesVelocityLab , arrayLeftTrunkAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayLeftTrunkAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftPelvisAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftPelvisAnglesVelocityLab , arrayLeftPelvisAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayLeftPelvisAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftThighAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftThighAnglesVelocityLab , arrayLeftThighAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayLeftThighAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftShankAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftShankAnglesVelocityLab , arrayLeftShankAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayLeftShankAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftFootAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftFootAnglesVelocityLab , arrayLeftFootAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayLeftFootAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftHipAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftHipAnglesVelocityPelvis , arrayLeftHipAnglesAccelerationPelvis] = math.AngVelAcc_Euler_YXZ(arrayLeftHipAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftKneeAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftKneeAnglesVelocityThigh , arrayLeftKneeAnglesAccelerationThigh] = math.AngVelAcc_Euler_YXZ(arrayLeftKneeAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayLeftAnkleAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayLeftAnkleAnglesVelocityShank , arrayLeftAnkleAnglesAccelerationShank] = math.AngVelAcc_Euler_YXZ(arrayLeftAnkleAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            
            # Extract Force Plate Data
            # GetDeviceChannelGlobal(DeviceID, DeviceOutputID, ChannelID)
            # DeviceOutputID: Force = 1, Moment =2, COP =3
            # ChannelID: X =1, Y=2, Z=3
            
            DeviceID = LeftForcePlate_DeviceID
            FP_Origin = Left_forceplate.LocalT # Local Origin- Usually zero
            FP_Center = Left_forceplate.WorldT # Force Plate Center
            
            # Force Plate data in Global coordinate system
            # This is the force from body to force plate going into the ground 
            [arrayFx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 1)
            [arrayFy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 2)
            [arrayFz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 3)
            
            [arrayMx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 1)
            [arrayMy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 2)
            [arrayMz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 3)
            
            [arrayCOPx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 1)
            [arrayCOPy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 2)
            [arrayCOPz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 3)
            
            GRF = np.array([0.,0.,0.]) # Ground Reaction Force
            GRT = np.array([0.,0.,0.]) # Ground Reaction Torque
            COP = np.array([0.,0.,0.]) # Center of Pressure
            COP_Pelvis = np.array([0.,0.,0.]) # Center of Pressure w.r.t. Pelvis
            
            LeftAnkleForceLab = np.array([0.,0.,0.])
            LeftKneeForceLab = np.array([0.,0.,0.])
            LeftHipForceLab = np.array([0.,0.,0.])
            LeftAnkleMoment_Foot = np.array([0.,0.,0.])
            LeftKneeMoment_Shank = np.array([0.,0.,0.])
            LeftHipMoment_Thigh = np.array([0.,0.,0.])
            LeftAnklePower = np.array([0.,0.,0.])
            LeftKneePower = np.array([0.,0.,0.])
            LeftHipPower = np.array([0.,0.,0.])
            for FrameNumber in range(StartFrame -1, EndFrame):
                Sign = -1 # Left Side
                
                #Transform marker data if necessary based on direction that the patient is walking
                
                SacralMarker  = np.array([Direction * SacralMarkerX[FrameNumber], Direction * SacralMarkerY[FrameNumber], SacralMarkerZ[FrameNumber]])
                LeftASISMarker  = np.array([Direction * LeftASISMarkerX[FrameNumber], Direction * LeftASISMarkerY[FrameNumber], LeftASISMarkerZ[FrameNumber]])
                RightASISMarker  = np.array([Direction * RightASISMarkerX[FrameNumber], Direction * RightASISMarkerY[FrameNumber], RightASISMarkerZ[FrameNumber]])
            
                
                LeftThighMarker  = np.array([Direction * LeftThighMarkerX[FrameNumber], Direction * LeftThighMarkerY[FrameNumber], LeftThighMarkerZ[FrameNumber]])
                LeftLateralKneeMarker  = np.array([Direction * LeftLateralKneeMarkerX[FrameNumber], Direction * LeftLateralKneeMarkerY[FrameNumber], LeftLateralKneeMarkerZ[FrameNumber]])
                LeftTibialMarker  = np.array([Direction * LeftTibialMarkerX[FrameNumber], Direction * LeftTibialMarkerY[FrameNumber], LeftTibialMarkerZ[FrameNumber]])
                LeftLateralAnkleMarker  = np.array([Direction * LeftLateralAnkleMarkerX[FrameNumber], Direction * LeftLateralAnkleMarkerY[FrameNumber], LeftLateralAnkleMarkerZ[FrameNumber]])
                LeftToeMarker  = np.array([Direction * LeftToeMarkerX[FrameNumber], Direction * LeftToeMarkerY[FrameNumber], LeftToeMarkerZ[FrameNumber]])
                LeftMedialAnkleMarker  = np.array([Direction * LeftMedialAnkleMarkerX[FrameNumber], Direction * LeftMedialAnkleMarkerY[FrameNumber], LeftMedialAnkleMarkerZ[FrameNumber]])
                LeftHeelMarker  = np.array([Direction * LeftHeelMarkerX[FrameNumber], Direction * LeftHeelMarkerY[FrameNumber], LeftHeelMarkerZ[FrameNumber]])
                if LeftTibialTriadCheck is True:
                    LeftTibialUpperMarker  = np.array([Direction * LeftTibialUpperMarkerX[FrameNumber], Direction * LeftTibialUpperMarkerY[FrameNumber], LeftTibialUpperMarkerZ[FrameNumber]])
                    LeftTibialLowerMarker  = np.array([Direction * LeftTibialLowerMarkerX[FrameNumber], Direction * LeftTibialLowerMarkerY[FrameNumber], LeftTibialLowerMarkerZ[FrameNumber]])
                #Transform joint center data if necessary based on direction that the patient is walking
                LeftHipCenterLab = np.array([Direction * arrayLeftHipCenter[0][FrameNumber], Direction * arrayLeftHipCenter[1][FrameNumber], arrayLeftHipCenter[2][FrameNumber]])
                LeftKneeCenterLab = np.array([Direction * arrayLeftKneeCenter[0][FrameNumber], Direction * arrayLeftKneeCenter[1][FrameNumber], arrayLeftKneeCenter[2][FrameNumber]])
                LeftAnkleCenterLab = np.array([Direction * arrayLeftAnkleCenter[0][FrameNumber], Direction * arrayLeftAnkleCenter[1][FrameNumber], arrayLeftAnkleCenter[2][FrameNumber]])
                #Transform center of mass data if necessary based on direction that the patient is walking
                LeftThighCenterOfMass = np.array([Direction * arrayLeftThighCenterOfMass[0][FrameNumber], Direction * arrayLeftThighCenterOfMass[1][FrameNumber], arrayLeftThighCenterOfMass[2][FrameNumber]])
                LeftShankCenterOfMass = np.array([Direction * arrayLeftShankCenterOfMass[0][FrameNumber], Direction * arrayLeftShankCenterOfMass[1][FrameNumber], arrayLeftShankCenterOfMass[2][FrameNumber]])
                LeftFootCenterOfMass = np.array([Direction * arrayLeftFootCenterOfMass[0][FrameNumber], Direction * arrayLeftFootCenterOfMass[1][FrameNumber], arrayLeftFootCenterOfMass[2][FrameNumber]])
                
                # Compute centroidal radii of gyration (Convert from mm to meters)
                LeftThighRadiusOfGyration = math.RadiusOfGyration(LeftHipCenterLab, LeftKneeCenterLab, 0.323, 0.323, 0.187) /1e3
                LeftShankRadiusOfGyration = math.RadiusOfGyration(LeftKneeCenterLab, LeftAnkleCenterLab, 0.302, 0.302, 0.087) /1e3
                LeftFootRadiusOfGyration = math.RadiusOfGyration(LeftAnkleCenterLab, LeftToeMarker, 0.148, 0.475, 0.475) /1e3
                
                # Compute segmental mass moment of inertia
                LeftThighMassMomentOfInertia = ThighMass * np.square(LeftThighRadiusOfGyration)
                LeftShankMassMomentOfInertia = ShankMass * np.square(LeftShankRadiusOfGyration)
                LeftFootMassMomentOfInertia = FootMass * np.square(LeftFootRadiusOfGyration)
                 
                
                FP_FrameNumber = int(FrameNumber * FP_FrameRate / MarkerFrameRate)
                
                # Compute Vertical Torque (Mz is dependent on COP location)
                Tz = arrayMz[FP_FrameNumber] + arrayFx[FP_FrameNumber] * (arrayCOPy[FP_FrameNumber] - FP_Center[1] + FP_Origin[1]) - arrayFy[FP_FrameNumber] * (arrayCOPx[FP_FrameNumber] -FP_Center[0] + FP_Origin[0])
                
                # Account for Walking Direction
                # Compute Reaction force as opposite of force plate output
                GRF[0] = -Direction * arrayFx[FP_FrameNumber]
                GRF[1] = -Direction * arrayFy[FP_FrameNumber]
                GRF[2] = -arrayFz[FP_FrameNumber]
                GRT[2] = -Tz / 1e3 # Convert from mm to meters

                # Center of Pressure is already in lab/global coordinate system
                COP[0] = Direction * arrayCOPx[FP_FrameNumber]
                COP[1] = Direction * arrayCOPy[FP_FrameNumber]
                COP[2] = 0
                
                ############ Compute Anatomical Coordinate Systems ###################
                [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftASISMarker, RightASISMarker, SacralMarker)
                EPelvisAnat = math.TransformAnatCoorSysFromTechCoors(self.valueEPelvisAnatRelTech, EPelvisTech)
                LeftEThighTech = gait.TechCS_Thigh_Newington('Left', LeftHipCenterLab, LeftThighMarker, LeftLateralKneeMarker)
                LeftEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEThighAnatRelTech,LeftEThighTech)
                if LeftTibialTriadCheck is True:
                    LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftTibialUpperMarker, LeftTibialLowerMarker, LeftTibialMarker)
                else:
                    LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftKneeCenterLab, LeftTibialMarker, LeftLateralAnkleMarker)
                LeftEShankProximalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEShankProximalAnatRelTech, LeftEShankTech)
                LeftEShankDistalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEShankDistalAnatRelTech, LeftEShankTech)
                # If Medial ankle is available,then recompute Shank Proximal/Distal Anatomical Coordinate System
                if LeftMedialAnkleMarkerDropOff == 0:
                    LeftEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Left', LeftKneeCenterLab, LeftLateralKneeMarker, LeftAnkleCenterLab)
                    LeftEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftLateralAnkleMarker)
                LeftEFootTech = gait.TechCS_Foot_Newington('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftToeMarker)
                LeftEFootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEFootAnatRelTech, LeftEFootTech)
                try:
                    LeftEFootTibAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEFootAnat2RelTech, LeftEFootTech)
                except:
                    LeftEFootTibAnat = np.matrix([[0. for m in range(3)] for n in range(3)])
                ####################################################################################################### 
                
                
                # ============================== Ankle ====================================
                # All Distances are in mm. Account for conversion to meters
                LeftAnkleForceLab[0] = FootMass * Direction * arrayLeftFootLinearAccelerationLab[0][FrameNumber] /1e3 - GRF[0]
                LeftAnkleForceLab[1] = FootMass * Direction * arrayLeftFootLinearAccelerationLab[1][FrameNumber] /1e3 - GRF[1]
                LeftAnkleForceLab[2] = FootMass * arrayLeftFootLinearAccelerationLab[2][FrameNumber] /1e3 - GRF[2] + FootMass * 9.81
            
                    
                # vector from center of mass to proximal point of load application
                ProximalVector = LeftAnkleCenterLab - LeftFootCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = COP - LeftFootCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,LeftAnkleForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,GRF) / 1e3 # Convert from mm to meters
                
                # Transform to Foot Coordinate System
                MomentFromProximalForce_Foot = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, LeftEFootAnat)
                MomentfromDistalForce_Foot = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, LeftEFootAnat)
                GRT_Foot = math.TransformVectorIntoMovingCoors(GRT, LeftEFootAnat)
                LeftFootAnglesVelocityLab = np.array([arrayLeftFootAnglesVelocityLab[0][FrameNumber],arrayLeftFootAnglesVelocityLab[1][FrameNumber],arrayLeftFootAnglesVelocityLab[2][FrameNumber]])
                LeftFootAnglesAccelerationLab = np.array([arrayLeftFootAnglesAccelerationLab[0][FrameNumber],arrayLeftFootAnglesAccelerationLab[1][FrameNumber],arrayLeftFootAnglesAccelerationLab[2][FrameNumber]])
                LeftAnkleAnglesVelocityShank = np.array([arrayLeftAnkleAnglesVelocityShank[0][FrameNumber],arrayLeftAnkleAnglesVelocityShank[1][FrameNumber],arrayLeftAnkleAnglesVelocityShank[2][FrameNumber]])
                LeftFootAnglesVelocity_Foot = math.TransformVectorIntoMovingCoors(LeftFootAnglesVelocityLab, LeftEFootAnat) 
                LeftFootAnglesAcceleration_Foot = math.TransformVectorIntoMovingCoors(LeftFootAnglesAccelerationLab, LeftEFootAnat) 
                # Joint velocity is in proximal segment CS. Transform to Distal
                if self.ShankCoordinateSystem == 'Distal':
                    LeftAnkleAnglesVelocityLab = math.TransformVectorIntoLabCoors(LeftAnkleAnglesVelocityShank, LeftEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    LeftAnkleAnglesVelocityLab = math.TransformVectorIntoLabCoors(LeftAnkleAnglesVelocityShank, LeftEShankProximalAnat)
                LeftAnkleAnglesVelocity_Foot = math.TransformVectorIntoMovingCoors(LeftAnkleAnglesVelocityLab, LeftEFootAnat)
                
                LeftAnkleMoment_Foot[0] = LeftFootMassMomentOfInertia[0] * LeftFootAnglesAcceleration_Foot[0] + \
                                        (LeftFootMassMomentOfInertia[2] - LeftFootMassMomentOfInertia[1]) * LeftFootAnglesVelocity_Foot[1] * LeftFootAnglesVelocity_Foot[2] \
                                            - MomentFromProximalForce_Foot[0] - MomentfromDistalForce_Foot[0] - GRT_Foot[0]
                LeftAnkleMoment_Foot[1] = LeftFootMassMomentOfInertia[1] * LeftFootAnglesAcceleration_Foot[1] + \
                                        (LeftFootMassMomentOfInertia[0] - LeftFootMassMomentOfInertia[2]) * LeftFootAnglesVelocity_Foot[2] * LeftFootAnglesVelocity_Foot[0] \
                                            - MomentFromProximalForce_Foot[1] - MomentfromDistalForce_Foot[1] - GRT_Foot[1]
                LeftAnkleMoment_Foot[2] = LeftFootMassMomentOfInertia[2] * LeftFootAnglesAcceleration_Foot[2] + \
                                        (LeftFootMassMomentOfInertia[1] - LeftFootMassMomentOfInertia[0]) * LeftFootAnglesVelocity_Foot[0] * LeftFootAnglesVelocity_Foot[1] \
                                            - MomentFromProximalForce_Foot[2] - MomentfromDistalForce_Foot[2] - GRT_Foot[2]
                
                # Transform Ankle Moment to Lab coordinate system
                LeftAnkleMomentLab = math.TransformVectorIntoLabCoors(LeftAnkleMoment_Foot,LeftEFootAnat)
                
                LeftAnklePower[0] = LeftAnkleMoment_Foot[0] * LeftAnkleAnglesVelocity_Foot[0]
                LeftAnklePower[1] = LeftAnkleMoment_Foot[1] * LeftAnkleAnglesVelocity_Foot[1]
                LeftAnklePower[2] = LeftAnkleMoment_Foot[2] * LeftAnkleAnglesVelocity_Foot[2]
                
                LeftAnklePowerTotal = np.dot(LeftAnkleMoment_Foot, LeftAnkleAnglesVelocity_Foot)
                
                # Normalize and Store in array
                # Apply sign convention based on right versus left side & plotting convention
                # Internal Moments that are Extensor, Abductor, External Rotator are positive
                arrayLeftAnkleMoment[0][FrameNumber] =  -Sign * LeftAnkleMoment_Foot[0] /float(self.valueBodyMass) 
                arrayLeftAnkleMoment[1][FrameNumber] =  LeftAnkleMoment_Foot[1] /float(self.valueBodyMass)
                arrayLeftAnkleMoment[2][FrameNumber] =  -Sign * LeftAnkleMoment_Foot[2] /float(self.valueBodyMass)
                
                arrayLeftAnklePower[0][FrameNumber] =  LeftAnklePower[0] /float(self.valueBodyMass)
                arrayLeftAnklePower[1][FrameNumber] =  LeftAnklePower[1] /float(self.valueBodyMass)
                arrayLeftAnklePower[2][FrameNumber] =  LeftAnklePower[2] /float(self.valueBodyMass)
                
                arrayLeftAnklePowerTotal[0][FrameNumber] =  0
                arrayLeftAnklePowerTotal[1][FrameNumber] =  0
                arrayLeftAnklePowerTotal[2][FrameNumber] =  LeftAnklePowerTotal /float(self.valueBodyMass)
                
                # Transform Ankle Force into Foot CS: X=AP, Y=ML, Z=SI (Do Not Re-arrange these)
                LeftAnkleForceFoot = math.TransformVectorIntoMovingCoors(LeftAnkleForceLab, LeftEFootTibAnat)
                arrayLeftAnkleJRF[0][FrameNumber] = LeftAnkleForceFoot[0] / float(self.valueBodyMass)
                arrayLeftAnkleJRF[1][FrameNumber] = Sign * LeftAnkleForceFoot[1] / float(self.valueBodyMass)
                arrayLeftAnkleJRF[2][FrameNumber] = LeftAnkleForceFoot[2] / float(self.valueBodyMass)
                
                # ============================== Knee ====================================
                # Reverse sign of force and moment from Distal Segment
                LeftAnkleForceLab = - LeftAnkleForceLab
                LeftAnkleMomentLab = - LeftAnkleMomentLab
                
                # All Distances are in mm. Account for conversion to meters
                LeftKneeForceLab[0] = ShankMass * Direction * arrayLeftShankLinearAccelerationLab[0][FrameNumber] /1e3 - LeftAnkleForceLab[0]
                LeftKneeForceLab[1] = ShankMass * Direction * arrayLeftShankLinearAccelerationLab[1][FrameNumber] /1e3 - LeftAnkleForceLab[1]
                LeftKneeForceLab[2] = ShankMass * arrayLeftShankLinearAccelerationLab[2][FrameNumber] /1e3 - LeftAnkleForceLab[2] + FootMass * 9.81
                

                # vector from center of mass to proximal point of load application
                ProximalVector = LeftKneeCenterLab - LeftShankCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = LeftAnkleCenterLab - LeftShankCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,LeftKneeForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,LeftAnkleForceLab) / 1e3 # Convert from mm to meters
                
                # Tranform to Shank Coordinate System
                if self.ShankCoordinateSystem == 'Distal':
                    MomentFromProximalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, LeftEShankDistalAnat)
                    MomentfromDistalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, LeftEShankDistalAnat)
                    LeftAnkleMoment_Shank = math.TransformVectorIntoMovingCoors(LeftAnkleMomentLab, LeftEShankDistalAnat)
                    LeftShankAnglesVelocityLab = np.array([arrayLeftShankAnglesVelocityLab[0][FrameNumber],arrayLeftShankAnglesVelocityLab[1][FrameNumber],arrayLeftShankAnglesVelocityLab[2][FrameNumber]])
                    LeftShankAnglesAccelerationLab = np.array([arrayLeftShankAnglesAccelerationLab[0][FrameNumber],arrayLeftShankAnglesAccelerationLab[1][FrameNumber],arrayLeftShankAnglesAccelerationLab[2][FrameNumber]])
                    LeftKneeAnglesVelocityThigh = np.array([arrayLeftKneeAnglesVelocityThigh[0][FrameNumber],arrayLeftKneeAnglesVelocityThigh[1][FrameNumber],arrayLeftKneeAnglesVelocityThigh[2][FrameNumber]])
                    LeftShankAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(LeftShankAnglesVelocityLab, LeftEShankDistalAnat) 
                    LeftShankAnglesAcceleration_Shank = math.TransformVectorIntoMovingCoors(LeftShankAnglesAccelerationLab, LeftEShankDistalAnat) 
                    # Joint velocity is in proximal segment CS. Transform to Distal
                    LeftKneeAnglesVelocityLab = math.TransformVectorIntoLabCoors(LeftKneeAnglesVelocityThigh, LeftEThighAnat)
                    LeftKneeAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(LeftKneeAnglesVelocityLab, LeftEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    MomentFromProximalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, LeftEShankProximalAnat)
                    MomentfromDistalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, LeftEShankProximalAnat)
                    LeftAnkleMoment_Shank = math.TransformVectorIntoMovingCoors(LeftAnkleMomentLab, LeftEShankProximalAnat)
                    LeftShankAnglesVelocityLab = np.array([arrayLeftShankAnglesVelocityLab[0][FrameNumber],arrayLeftShankAnglesVelocityLab[1][FrameNumber],arrayLeftShankAnglesVelocityLab[2][FrameNumber]])
                    LeftShankAnglesAccelerationLab = np.array([arrayLeftShankAnglesAccelerationLab[0][FrameNumber],arrayLeftShankAnglesAccelerationLab[1][FrameNumber],arrayLeftShankAnglesAccelerationLab[2][FrameNumber]])
                    LeftKneeAnglesVelocityThigh = np.array([arrayLeftKneeAnglesVelocityThigh[0][FrameNumber],arrayLeftKneeAnglesVelocityThigh[1][FrameNumber],arrayLeftKneeAnglesVelocityThigh[2][FrameNumber]])
                    LeftShankAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(LeftShankAnglesVelocityLab, LeftEShankProximalAnat) 
                    LeftShankAnglesAcceleration_Shank = math.TransformVectorIntoMovingCoors(LeftShankAnglesAccelerationLab, LeftEShankProximalAnat) 
                    # Joint velocity is in proximal segment CS. Transform to Distal
                    LeftKneeAnglesVelocityLab = math.TransformVectorIntoLabCoors(LeftKneeAnglesVelocityThigh, LeftEThighAnat)
                    LeftKneeAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(LeftKneeAnglesVelocityLab, LeftEShankProximalAnat)
                
               
                LeftKneeMoment_Shank[0] = LeftShankMassMomentOfInertia[0] * LeftShankAnglesAcceleration_Shank[0] + \
                                        (LeftShankMassMomentOfInertia[2] - LeftShankMassMomentOfInertia[1]) * LeftShankAnglesVelocity_Shank[1] * LeftShankAnglesVelocity_Shank[2] \
                                            - MomentFromProximalForce_Shank[0] - MomentfromDistalForce_Shank[0] - LeftAnkleMoment_Shank[0]
                LeftKneeMoment_Shank[1] = LeftShankMassMomentOfInertia[1] * LeftShankAnglesAcceleration_Shank[1] + \
                                        (LeftShankMassMomentOfInertia[0] - LeftShankMassMomentOfInertia[2]) * LeftShankAnglesVelocity_Shank[2] * LeftShankAnglesVelocity_Shank[0] \
                                            - MomentFromProximalForce_Shank[1] - MomentfromDistalForce_Shank[1] - LeftAnkleMoment_Shank[1]
                LeftKneeMoment_Shank[2] = LeftShankMassMomentOfInertia[2] * LeftShankAnglesAcceleration_Shank[2] + \
                                        (LeftShankMassMomentOfInertia[1] - LeftShankMassMomentOfInertia[0]) * LeftShankAnglesVelocity_Shank[0] * LeftShankAnglesVelocity_Shank[1] \
                                            - MomentFromProximalForce_Shank[2] - MomentfromDistalForce_Shank[2] - LeftAnkleMoment_Shank[2]

                # Transform Knee Moment to Lab coordinate system
                if self.ShankCoordinateSystem == 'Distal':
                    LeftKneeMomentLab = math.TransformVectorIntoLabCoors(LeftKneeMoment_Shank,LeftEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    LeftKneeMomentLab = math.TransformVectorIntoLabCoors(LeftKneeMoment_Shank,LeftEShankProximalAnat)
                    
                LeftKneePower[0] = LeftKneeMoment_Shank[0] * LeftKneeAnglesVelocity_Shank[0]
                LeftKneePower[1] = LeftKneeMoment_Shank[1] * LeftKneeAnglesVelocity_Shank[1]
                LeftKneePower[2] = LeftKneeMoment_Shank[2] * LeftKneeAnglesVelocity_Shank[2]
                
                LeftKneePowerTotal = np.dot(LeftKneeMoment_Shank, LeftKneeAnglesVelocity_Shank)
                
                # Normalize and Store in array
                arrayLeftKneeMoment[0][FrameNumber] =  -Sign * LeftKneeMoment_Shank[0] /float(self.valueBodyMass)
                arrayLeftKneeMoment[1][FrameNumber] =  -LeftKneeMoment_Shank[1] /float(self.valueBodyMass)
                arrayLeftKneeMoment[2][FrameNumber] =  -Sign * LeftKneeMoment_Shank[2] /float(self.valueBodyMass)
                
                arrayLeftKneePower[0][FrameNumber] =  LeftKneePower[0] /float(self.valueBodyMass)
                arrayLeftKneePower[1][FrameNumber] =  LeftKneePower[1] /float(self.valueBodyMass)
                arrayLeftKneePower[2][FrameNumber] =  LeftKneePower[2] /float(self.valueBodyMass)
                
                arrayLeftKneePowerTotal[0][FrameNumber] =  0
                arrayLeftKneePowerTotal[1][FrameNumber] =  0
                arrayLeftKneePowerTotal[2][FrameNumber] =  LeftKneePowerTotal /float(self.valueBodyMass)
                
                # Transform Knee Force into Proximal Tibia CS
                LeftKneeForceTib = math.TransformVectorIntoMovingCoors(LeftKneeForceLab, LeftEShankProximalAnat)
                arrayLeftKneeJRF[0][FrameNumber] = LeftKneeForceTib[0] / float(self.valueBodyMass)
                arrayLeftKneeJRF[1][FrameNumber] = Sign * LeftKneeForceTib[1] / float(self.valueBodyMass)
                arrayLeftKneeJRF[2][FrameNumber] = LeftKneeForceTib[2] / float(self.valueBodyMass)

                
                # ============================== Hip ====================================
                # Reverse sign of force and moment from Distal Segment
                LeftKneeForceLab = - LeftKneeForceLab
                LeftKneeMomentLab = - LeftKneeMomentLab
                
                # All Distances are in mm. Account for conversion to meters
                LeftHipForceLab[0] = ThighMass * Direction * arrayLeftThighLinearAccelerationLab[0][FrameNumber] /1e3 - LeftKneeForceLab[0]
                LeftHipForceLab[1] = ThighMass * Direction * arrayLeftThighLinearAccelerationLab[1][FrameNumber] /1e3 - LeftKneeForceLab[1]
                LeftHipForceLab[2] = ThighMass * arrayLeftThighLinearAccelerationLab[2][FrameNumber] /1e3 - LeftKneeForceLab[2] + FootMass * 9.81
                

                # vector from center of mass to proximal point of load application
                ProximalVector = LeftHipCenterLab - LeftThighCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = LeftKneeCenterLab - LeftThighCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,LeftHipForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,LeftKneeForceLab) / 1e3 # Convert from mm to meters
                
                # Transform to Thigh Coordinate System
                MomentFromProximalForce_Thigh = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, LeftEThighAnat)
                MomentfromDistalForce_Thigh = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, LeftEThighAnat)
                LeftKneeMoment_Thigh = math.TransformVectorIntoMovingCoors(LeftKneeMomentLab, LeftEThighAnat)
                LeftThighAnglesVelocityLab = np.array([arrayLeftThighAnglesVelocityLab[0][FrameNumber],arrayLeftThighAnglesVelocityLab[1][FrameNumber],arrayLeftThighAnglesVelocityLab[2][FrameNumber]])
                LeftThighAnglesAccelerationLab = np.array([arrayLeftThighAnglesAccelerationLab[0][FrameNumber],arrayLeftThighAnglesAccelerationLab[1][FrameNumber],arrayLeftThighAnglesAccelerationLab[2][FrameNumber]])
                LeftHipAnglesVelocityPelvis = np.array([arrayLeftHipAnglesVelocityPelvis[0][FrameNumber],arrayLeftHipAnglesVelocityPelvis[1][FrameNumber],arrayLeftHipAnglesVelocityPelvis[2][FrameNumber]])
                LeftThighAnglesVelocity_Thigh = math.TransformVectorIntoMovingCoors(LeftThighAnglesVelocityLab, LeftEThighAnat) 
                LeftThighAnglesAcceleration_Thigh = math.TransformVectorIntoMovingCoors(LeftThighAnglesAccelerationLab, LeftEThighAnat) 
                # Joint velocity is in proximal segment CS. Transform to Distal
                LeftHipAnglesVelocityLab = math.TransformVectorIntoLabCoors(LeftHipAnglesVelocityPelvis, EPelvisAnat)
                LeftHipAnglesVelocity_Thigh = math.TransformVectorIntoMovingCoors(LeftHipAnglesVelocityLab, LeftEThighAnat)
                
                
                
                LeftHipMoment_Thigh[0] = LeftThighMassMomentOfInertia[0] * LeftThighAnglesAcceleration_Thigh[0] + \
                                        (LeftThighMassMomentOfInertia[2] - LeftThighMassMomentOfInertia[1]) * LeftThighAnglesVelocity_Thigh[1] * LeftThighAnglesVelocity_Thigh[2] \
                                            - MomentFromProximalForce_Thigh[0] - MomentfromDistalForce_Thigh[0] - LeftKneeMoment_Thigh[0]
                LeftHipMoment_Thigh[1] = LeftThighMassMomentOfInertia[1] * LeftThighAnglesAcceleration_Thigh[1] + \
                                        (LeftThighMassMomentOfInertia[0] - LeftThighMassMomentOfInertia[2]) * LeftThighAnglesVelocity_Thigh[2] * LeftThighAnglesVelocity_Thigh[0] \
                                            - MomentFromProximalForce_Thigh[1] - MomentfromDistalForce_Thigh[1] - LeftKneeMoment_Thigh[1]
                LeftHipMoment_Thigh[2] = LeftThighMassMomentOfInertia[2] * LeftThighAnglesAcceleration_Thigh[2] + \
                                        (LeftThighMassMomentOfInertia[1] - LeftThighMassMomentOfInertia[0]) * LeftThighAnglesVelocity_Thigh[0] * LeftThighAnglesVelocity_Thigh[1] \
                                            - MomentFromProximalForce_Thigh[2] - MomentfromDistalForce_Thigh[2] - LeftKneeMoment_Thigh[2]

                # Transform Hip Moment to Lab coordinate system
                LeftHipMomentLab = math.TransformVectorIntoLabCoors(LeftHipMoment_Thigh,LeftEThighAnat)
                
                LeftHipPower[0] = LeftHipMoment_Thigh[0] * LeftHipAnglesVelocity_Thigh[0]
                LeftHipPower[1] = LeftHipMoment_Thigh[1] * LeftHipAnglesVelocity_Thigh[1]
                LeftHipPower[2] = LeftHipMoment_Thigh[2] * LeftHipAnglesVelocity_Thigh[2]
                
                LeftHipPowerTotal = np.dot(LeftHipMoment_Thigh, LeftHipAnglesVelocity_Thigh)
                
                # Normalize and Store in array
                arrayLeftHipMoment[0][FrameNumber] =  -Sign * LeftHipMoment_Thigh[0] /float(self.valueBodyMass)
                arrayLeftHipMoment[1][FrameNumber] =  LeftHipMoment_Thigh[1] /float(self.valueBodyMass)
                arrayLeftHipMoment[2][FrameNumber] =  -Sign * LeftHipMoment_Thigh[2] /float(self.valueBodyMass)
                
                arrayLeftHipPower[0][FrameNumber] =  LeftHipPower[0] /float(self.valueBodyMass)
                arrayLeftHipPower[1][FrameNumber] =  LeftHipPower[1] /float(self.valueBodyMass)
                arrayLeftHipPower[2][FrameNumber] =  LeftHipPower[2] /float(self.valueBodyMass)
                
                arrayLeftHipPowerTotal[0][FrameNumber] =  0
                arrayLeftHipPowerTotal[1][FrameNumber] =  0
                arrayLeftHipPowerTotal[2][FrameNumber] =  LeftHipPowerTotal /float(self.valueBodyMass)
                
                # Transform Hip Force into Thigh CS
                LeftHipForceThigh = math.TransformVectorIntoMovingCoors(LeftHipForceLab, LeftEThighAnat)
                arrayLeftHipJRF[0][FrameNumber] = LeftHipForceThigh[0] / float(self.valueBodyMass)
                arrayLeftHipJRF[1][FrameNumber] = Sign * LeftHipForceThigh[1] / float(self.valueBodyMass)
                arrayLeftHipJRF[2][FrameNumber] = LeftHipForceThigh[2] / float(self.valueBodyMass)
                # Correct for Lab CS
                GRF = math.TransformVectorIntoMovingCoors(GRF, ELab)
                # Write back to GRM, account for side for ML, and scale to BW
                arrayLeftGRF[0][FrameNumber] = GRF[0] / float(self.valueBodyMass)
                arrayLeftGRF[1][FrameNumber] = Sign * GRF[1] / float(self.valueBodyMass)
                arrayLeftGRF[2][FrameNumber] = GRF[2] / float(self.valueBodyMass)
                
                arrayLeftGRM[0][FrameNumber] = arrayCOPx[FP_FrameNumber] - arrayPelvisOrigin[0][FrameNumber]
                arrayLeftGRM[1][FrameNumber] = arrayCOPy[FP_FrameNumber] - arrayPelvisOrigin[1][FrameNumber]
                arrayLeftGRM[2][FrameNumber] = Sign * GRT[2] / float(self.valueBodyMass)
                
                # Store in array of one frame
                COP_Pelvis = np.array([arrayLeftGRM[0][FrameNumber], arrayLeftGRM[1][FrameNumber], arrayLeftGRM[2][FrameNumber]])
                # Correct for Lab CS
                COP_Pelvis = math.TransformVectorIntoMovingCoors(COP_Pelvis, ELab)
                # Write back to GRM, account for walk direction and side for ML, and scale to % leg length
                arrayLeftGRM[0][FrameNumber] = 100 * Direction * COP_Pelvis[0] / self.valueLeftLegLength
                arrayLeftGRM[1][FrameNumber] = 100 * Direction * Sign * COP_Pelvis[1] / self.valueLeftLegLength

                # Add Moment and Power Sums
                # Index 0 is sum of sagittal plane moment, Index 1 is sum of sagittal power, Index3 is sum of total power
                arrayLeftMPSum[0][FrameNumber] = arrayLeftHipMoment[0][FrameNumber] + \
                                                 arrayLeftKneeMoment[0][FrameNumber] + \
                                                 arrayLeftAnkleMoment[0][FrameNumber]
                arrayLeftMPSum[1][FrameNumber] = arrayLeftHipPower[0][FrameNumber] + \
                                                 arrayLeftKneePower[0][FrameNumber] + \
                                                 arrayLeftAnklePower[0][FrameNumber]
                arrayLeftMPSum[2][FrameNumber] = arrayLeftHipPowerTotal[2][FrameNumber] + \
                                                 arrayLeftKneePowerTotal[2][FrameNumber] + \
                                                 arrayLeftAnklePowerTotal[2][FrameNumber]
                
                # Add Foot CoP, compute components first and foot length
                AnkleCOP = COP - LeftAnkleCenterLab
                AnkleCOP[2] = 0
                AnkleCOP_Foot = math.TransformVectorIntoMovingCoors(AnkleCOP, LeftEFootAnat)
                FL = np.linalg.norm(LeftToeMarker - LeftAnkleCenterLab)
                # Normalize
                AnkleCOP_Foot_Normalized = 100 * AnkleCOP_Foot / FL
                # Account for foot progression angle and account for walk direction and M/L
                arrayLeftFootCoP[0][FrameNumber] = AnkleCOP_Foot_Normalized[0]
                arrayLeftFootCoP[1][FrameNumber] = AnkleCOP_Foot_Normalized[1]
                arrayLeftFootCoP[2][FrameNumber] = 0
            
            
            
        if not RightForcePlate_DeviceID == 0:
            #==================== Smooth Data before Differentiating ======================
            # Center of Mass
            arrayHATCenterOfMass = math.Smooth3DArray(arrayHATCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightThighCenterOfMass = math.Smooth3DArray(arrayRightThighCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightShankCenterOfMass = math.Smooth3DArray(arrayRightShankCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightFootCenterOfMass = math.Smooth3DArray(arrayRightFootCenterOfMass, StartFrame, EndFrame, Order, WindowWidth)
            # Joint Centers
            arrayRightHipCenter = math.Smooth3DArray(arrayRightHipCenter, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightKneeCenter = math.Smooth3DArray(arrayRightKneeCenter, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightAnkleCenter = math.Smooth3DArray(arrayRightAnkleCenter, StartFrame, EndFrame, Order, WindowWidth)
            # Right Angles
            arrayRightTrunkAngles = math.Smooth3DArray(arrayRightTrunkAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightPelvisAngles = math.Smooth3DArray(arrayRightPelvisAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightThighAngles = math.Smooth3DArray(arrayRightThighAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightShankAngles = math.Smooth3DArray(arrayRightShankAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightFootAngles = math.Smooth3DArray(arrayRightFootAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightHipAngles = math.Smooth3DArray(arrayRightHipAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightKneeAngles = math.Smooth3DArray(arrayRightKneeAngles, StartFrame, EndFrame, Order, WindowWidth)
            arrayRightAnkleAngles = math.Smooth3DArray(arrayRightAnkleAngles, StartFrame, EndFrame, Order, WindowWidth)
            
            # ======================== Translation Variables Differentiatition ===============================
            # Center of Mass
            [arrayHATLinearVelocityLab , arrayHATLinearAccelerationLab ] = math.Differentiate(arrayHATCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightThighLinearVelocityLab , arrayRightThighLinearAccelerationLab ] = math.Differentiate(arrayRightThighCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightShankLinearVelocityLab , arrayRightShankLinearAccelerationLab ] = math.Differentiate(arrayRightShankCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightFootLinearVelocityLab , arrayRightFootLinearAccelerationLab ] = math.Differentiate(arrayRightFootCenterOfMass, StartFrame, EndFrame, framecount, DeltaTime)
            # Joint Centers
            [arrayRightHipCenterLinearVelocityLab , arrayRightHipCenterLinearAccelerationLab ] = math.Differentiate(arrayRightHipCenter, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightKneeCenterLinearVelocityLab , arrayRightKneeCenterLinearAccelerationLab ] = math.Differentiate(arrayRightKneeCenter, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightAnkleCenterLinearVelocityLab , arrayRightAnkleCenterLinearAccelerationLab ] = math.Differentiate(arrayRightAnkleCenter, StartFrame, EndFrame, framecount, DeltaTime)
            
            # ======================== Rotational Variables Differentiatition ===============================
            # Right Angles  Derivatives. Derivatives are in Reference Coordinate System. For segment- Lab CS. For Joints- Proximal Segment CS
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightTrunkAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightTrunkAnglesVelocityLab , arrayRightTrunkAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayRightTrunkAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightPelvisAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightPelvisAnglesVelocityLab , arrayRightPelvisAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayRightPelvisAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightThighAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightThighAnglesVelocityLab , arrayRightThighAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayRightThighAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightShankAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightShankAnglesVelocityLab , arrayRightShankAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayRightShankAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightFootAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightFootAnglesVelocityLab , arrayRightFootAnglesAccelerationLab] = math.AngVelAcc_Euler_YXZ(arrayRightFootAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightHipAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightHipAnglesVelocityPelvis , arrayRightHipAnglesAccelerationPelvis] = math.AngVelAcc_Euler_YXZ(arrayRightHipAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightKneeAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightKneeAnglesVelocityThigh , arrayRightKneeAnglesAccelerationThigh] = math.AngVelAcc_Euler_YXZ(arrayRightKneeAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            [arrayVelocity , arrayAcceleration] = math.Differentiate(arrayRightAnkleAnglesRad, StartFrame, EndFrame, framecount, DeltaTime)
            [arrayRightAnkleAnglesVelocityShank , arrayRightAnkleAnglesAccelerationShank] = math.AngVelAcc_Euler_YXZ(arrayRightAnkleAnglesRad, arrayVelocity, arrayAcceleration, StartFrame, EndFrame, framecount)
            
            # Extract Force Plate Data
            # GetDeviceChannelGlobal(DeviceID, DeviceOutputID, ChannelID)
            # DeviceOutputID: Force = 1, Moment = 2, COP = 3
            # ChannelID: X =1, Y=2, Z=3
            
            DeviceID = RightForcePlate_DeviceID
            FP_Origin = Right_forceplate.LocalT # Local Origin- Usually zero
            FP_Center = Right_forceplate.WorldT # Force Plate Center
            
            # Force Plate data in Global coordinate system
            # This is the force from body to force plate going into the ground 
            [arrayFx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 1)
            [arrayFy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 2)
            [arrayFz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 1, 3)
            
            [arrayMx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 1)
            [arrayMy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 2)
            [arrayMz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 2, 3)
            
            [arrayCOPx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 1)
            [arrayCOPy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 2)
            [arrayCOPz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(DeviceID, 3, 3)
            
            GRF = np.array([0.,0.,0.]) # Ground Reaction Force
            GRT = np.array([0.,0.,0.]) # Ground Reaction Torque
            COP = np.array([0.,0.,0.]) # Center of Pressure
            RightAnkleForceLab = np.array([0.,0.,0.])
            RightKneeForceLab = np.array([0.,0.,0.])
            RightHipForceLab = np.array([0.,0.,0.])
            RightAnkleMoment_Foot = np.array([0.,0.,0.])
            RightKneeMoment_Shank = np.array([0.,0.,0.])
            RightHipMoment_Thigh = np.array([0.,0.,0.])
            RightAnklePower = np.array([0.,0.,0.])
            RightKneePower = np.array([0.,0.,0.])
            RightHipPower = np.array([0.,0.,0.])
            for FrameNumber in range(StartFrame -1, EndFrame):
                Sign = 1 # Right Side
                
                #Transform marker data if necessary based on direction that the patient is walking
                RightThighMarker  = np.array([Direction * RightThighMarkerX[FrameNumber], Direction * RightThighMarkerY[FrameNumber], RightThighMarkerZ[FrameNumber]])
                RightLateralKneeMarker  = np.array([Direction * RightLateralKneeMarkerX[FrameNumber], Direction * RightLateralKneeMarkerY[FrameNumber], RightLateralKneeMarkerZ[FrameNumber]])
                RightTibialMarker  = np.array([Direction * RightTibialMarkerX[FrameNumber], Direction * RightTibialMarkerY[FrameNumber], RightTibialMarkerZ[FrameNumber]])
                RightLateralAnkleMarker  = np.array([Direction * RightLateralAnkleMarkerX[FrameNumber], Direction * RightLateralAnkleMarkerY[FrameNumber], RightLateralAnkleMarkerZ[FrameNumber]])
                RightToeMarker  = np.array([Direction * RightToeMarkerX[FrameNumber], Direction * RightToeMarkerY[FrameNumber], RightToeMarkerZ[FrameNumber]])
                RightMedialAnkleMarker  = np.array([Direction * RightMedialAnkleMarkerX[FrameNumber], Direction * RightMedialAnkleMarkerY[FrameNumber], RightMedialAnkleMarkerZ[FrameNumber]])
                RightHeelMarker  = np.array([Direction * RightHeelMarkerX[FrameNumber], Direction * RightHeelMarkerY[FrameNumber], RightHeelMarkerZ[FrameNumber]])
                if RightTibialTriadCheck is True:
                    RightTibialUpperMarker  = np.array([Direction * RightTibialUpperMarkerX[FrameNumber], Direction * RightTibialUpperMarkerY[FrameNumber], RightTibialUpperMarkerZ[FrameNumber]])
                    RightTibialLowerMarker  = np.array([Direction * RightTibialLowerMarkerX[FrameNumber], Direction * RightTibialLowerMarkerY[FrameNumber], RightTibialLowerMarkerZ[FrameNumber]])
                #Transform joint center data if necessary based on direction that the patient is walking
                RightHipCenterLab = np.array([Direction * arrayRightHipCenter[0][FrameNumber], Direction * arrayRightHipCenter[1][FrameNumber], arrayRightHipCenter[2][FrameNumber]])
                RightKneeCenterLab = np.array([Direction * arrayRightKneeCenter[0][FrameNumber], Direction * arrayRightKneeCenter[1][FrameNumber], arrayRightKneeCenter[2][FrameNumber]])
                RightAnkleCenterLab = np.array([Direction * arrayRightAnkleCenter[0][FrameNumber], Direction * arrayRightAnkleCenter[1][FrameNumber], arrayRightAnkleCenter[2][FrameNumber]])
                #Transform center of mass data if necessary based on direction that the patient is walking
                RightThighCenterOfMass = np.array([Direction * arrayRightThighCenterOfMass[0][FrameNumber], Direction * arrayRightThighCenterOfMass[1][FrameNumber], arrayRightThighCenterOfMass[2][FrameNumber]])
                RightShankCenterOfMass = np.array([Direction * arrayRightShankCenterOfMass[0][FrameNumber], Direction * arrayRightShankCenterOfMass[1][FrameNumber], arrayRightShankCenterOfMass[2][FrameNumber]])
                RightFootCenterOfMass = np.array([Direction * arrayRightFootCenterOfMass[0][FrameNumber], Direction * arrayRightFootCenterOfMass[1][FrameNumber], arrayRightFootCenterOfMass[2][FrameNumber]])
                
                # Compute centroidal radii of gyration (Convert from mm to meters)
                RightThighRadiusOfGyration = math.RadiusOfGyration(RightHipCenterLab, RightKneeCenterLab, 0.323, 0.323, 0.187) /1e3
                RightShankRadiusOfGyration = math.RadiusOfGyration(RightKneeCenterLab, RightAnkleCenterLab, 0.302, 0.302, 0.087) /1e3
                RightFootRadiusOfGyration = math.RadiusOfGyration(RightAnkleCenterLab, RightToeMarker, 0.148, 0.475, 0.475) /1e3
                
                # Compute segmental mass moment of inertia
                RightThighMassMomentOfInertia = ThighMass * np.square(RightThighRadiusOfGyration)
                RightShankMassMomentOfInertia = ShankMass * np.square(RightShankRadiusOfGyration)
                RightFootMassMomentOfInertia = FootMass * np.square(RightFootRadiusOfGyration)
                 
                
                FP_FrameNumber = int(FrameNumber * FP_FrameRate / MarkerFrameRate)
                
                # Compute Vertical Torque (Mz is dependent on COP location)
                Tz = arrayMz[FP_FrameNumber] + arrayFx[FP_FrameNumber] * (arrayCOPy[FP_FrameNumber] - FP_Center[1] + FP_Origin[1]) - arrayFy[FP_FrameNumber] * (arrayCOPx[FP_FrameNumber] -FP_Center[0] + FP_Origin[0])
                
                # Account for Walking Direction
                # Compute Reaction force as opposite of force plate output
                GRF[0] = -Direction * arrayFx[FP_FrameNumber]
                GRF[1] = -Direction * arrayFy[FP_FrameNumber]
                GRF[2] = -arrayFz[FP_FrameNumber]
                GRT[2] = -Tz / 1e3 # Convert from mm to meters
                
                # Center of Pressure is already in lab/global coordinate system
                COP[0] = Direction * arrayCOPx[FP_FrameNumber]
                COP[1] = Direction * arrayCOPy[FP_FrameNumber]
                COP[2] = 0
                
                
                ############ Compute Anatomilcal Coordinate Systems ###################
                [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftASISMarker, RightASISMarker, SacralMarker)
                EPelvisAnat = math.TransformAnatCoorSysFromTechCoors(self.valueEPelvisAnatRelTech, EPelvisTech)
                RightEThighTech = gait.TechCS_Thigh_Newington('Right', RightHipCenterLab, RightThighMarker, RightLateralKneeMarker)
                RightEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEThighAnatRelTech,RightEThighTech)
                if RightTibialTriadCheck is True:
                    RightEShankTech = gait.TechCS_Shank_Newington('Right', RightTibialUpperMarker, RightTibialLowerMarker, RightTibialMarker)
                else:
                    RightEShankTech = gait.TechCS_Shank_Newington('Right', RightKneeCenterLab, RightTibialMarker, RightLateralAnkleMarker)
                RightEShankProximalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEShankProximalAnatRelTech, RightEShankTech)
                RightEShankDistalAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEShankDistalAnatRelTech, RightEShankTech)
                # If Medial ankle is available,then recompute Shank Proximal/Distal Anatomical Coordinate System
                if RightMedialAnkleMarkerDropOff == 0:
                    RightEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Right', RightKneeCenterLab, RightLateralKneeMarker, RightAnkleCenterLab)
                    RightEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Right', RightKneeCenterLab, RightAnkleCenterLab, RightLateralAnkleMarker)
                RightEFootTech = gait.TechCS_Foot_Newington('Right', RightKneeCenterLab, RightAnkleCenterLab, RightToeMarker)
                RightEFootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEFootAnatRelTech, RightEFootTech)
                try:
                    RightEFootTibAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEFootAnat2RelTech, RightEFootTech)
                except:
                    RightEFootTibAnat = np.matrix([[0. for m in range(3)] for n in range(3)])
                ####################################################################################################### 
                
                
                # ============================== Ankle ====================================
                # All Distances are in mm. Account for conversion to meters
                RightAnkleForceLab[0] = FootMass * Direction * arrayRightFootLinearAccelerationLab[0][FrameNumber] /1e3 - GRF[0]
                RightAnkleForceLab[1] = FootMass * Direction * arrayRightFootLinearAccelerationLab[1][FrameNumber] /1e3 - GRF[1]
                RightAnkleForceLab[2] = FootMass * arrayRightFootLinearAccelerationLab[2][FrameNumber] /1e3 - GRF[2] + FootMass * 9.81
            
                    
                # vector from center of mass to proximal point of load application
                ProximalVector = RightAnkleCenterLab - RightFootCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = COP - RightFootCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,RightAnkleForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,GRF) / 1e3 # Convert from mm to meters
                
                # Tranform to Foot Coordinate System
                MomentFromProximalForce_Foot = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, RightEFootAnat)
                MomentfromDistalForce_Foot = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, RightEFootAnat)
                GRT_Foot = math.TransformVectorIntoMovingCoors(GRT, RightEFootAnat)
                RightFootAnglesVelocityLab = np.array([arrayRightFootAnglesVelocityLab[0][FrameNumber],arrayRightFootAnglesVelocityLab[1][FrameNumber],arrayRightFootAnglesVelocityLab[2][FrameNumber]])
                RightFootAnglesAccelerationLab = np.array([arrayRightFootAnglesAccelerationLab[0][FrameNumber],arrayRightFootAnglesAccelerationLab[1][FrameNumber],arrayRightFootAnglesAccelerationLab[2][FrameNumber]])
                RightAnkleAnglesVelocityShank = np.array([arrayRightAnkleAnglesVelocityShank[0][FrameNumber],arrayRightAnkleAnglesVelocityShank[1][FrameNumber],arrayRightAnkleAnglesVelocityShank[2][FrameNumber]])
                RightFootAnglesVelocity_Foot = math.TransformVectorIntoMovingCoors(RightFootAnglesVelocityLab, RightEFootAnat) 
                RightFootAnglesAcceleration_Foot = math.TransformVectorIntoMovingCoors(RightFootAnglesAccelerationLab, RightEFootAnat) 
                # Joint velocity is in proximal segment CS. Transform to Distal
                if self.ShankCoordinateSystem == 'Distal':
                    RightAnkleAnglesVelocityLab = math.TransformVectorIntoLabCoors(RightAnkleAnglesVelocityShank, RightEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    RightAnkleAnglesVelocityLab = math.TransformVectorIntoLabCoors(RightAnkleAnglesVelocityShank, RightEShankProximalAnat)
                RightAnkleAnglesVelocity_Foot = math.TransformVectorIntoMovingCoors(RightAnkleAnglesVelocityLab, RightEFootAnat)

                
                RightAnkleMoment_Foot[0] = RightFootMassMomentOfInertia[0] * RightFootAnglesAcceleration_Foot[0] + \
                                        (RightFootMassMomentOfInertia[2] - RightFootMassMomentOfInertia[1]) * RightFootAnglesVelocity_Foot[1] * RightFootAnglesVelocity_Foot[2] \
                                            - MomentFromProximalForce_Foot[0] - MomentfromDistalForce_Foot[0] - GRT_Foot[0]
                RightAnkleMoment_Foot[1] = RightFootMassMomentOfInertia[1] * RightFootAnglesAcceleration_Foot[1] + \
                                        (RightFootMassMomentOfInertia[0] - RightFootMassMomentOfInertia[2]) * RightFootAnglesVelocity_Foot[2] * RightFootAnglesVelocity_Foot[0] \
                                            - MomentFromProximalForce_Foot[1] - MomentfromDistalForce_Foot[1] - GRT_Foot[1]
                RightAnkleMoment_Foot[2] = RightFootMassMomentOfInertia[2] * RightFootAnglesAcceleration_Foot[2] + \
                                        (RightFootMassMomentOfInertia[1] - RightFootMassMomentOfInertia[0]) * RightFootAnglesVelocity_Foot[0] * RightFootAnglesVelocity_Foot[1] \
                                            - MomentFromProximalForce_Foot[2] - MomentfromDistalForce_Foot[2] - GRT_Foot[2]
                
                # Transform Ankle Moment to Lab coordinate system
                RightAnkleMomentLab = math.TransformVectorIntoLabCoors(RightAnkleMoment_Foot,RightEFootAnat)
                
                RightAnklePower[0] = RightAnkleMoment_Foot[0] * RightAnkleAnglesVelocity_Foot[0]
                RightAnklePower[1] = RightAnkleMoment_Foot[1] * RightAnkleAnglesVelocity_Foot[1]
                RightAnklePower[2] = RightAnkleMoment_Foot[2] * RightAnkleAnglesVelocity_Foot[2]
                
                RightAnklePowerTotal = np.dot(RightAnkleMoment_Foot, RightAnkleAnglesVelocity_Foot)
                
                # Normalize and Store in array
                # Apply sign convention based on right versus Right side & plotting convention
                # Internal Moments that are Extensor, Abductor, External Rotator are positive
                arrayRightAnkleMoment[0][FrameNumber] =  -Sign * RightAnkleMoment_Foot[0] /float(self.valueBodyMass) 
                arrayRightAnkleMoment[1][FrameNumber] =  RightAnkleMoment_Foot[1] /float(self.valueBodyMass)
                arrayRightAnkleMoment[2][FrameNumber] =  -Sign * RightAnkleMoment_Foot[2] /float(self.valueBodyMass)
                
                arrayRightAnklePower[0][FrameNumber] =  RightAnklePower[0] /float(self.valueBodyMass)
                arrayRightAnklePower[1][FrameNumber] =  RightAnklePower[1] /float(self.valueBodyMass)
                arrayRightAnklePower[2][FrameNumber] =  RightAnklePower[2] /float(self.valueBodyMass)
                
                arrayRightAnklePowerTotal[0][FrameNumber] =  0 
                arrayRightAnklePowerTotal[1][FrameNumber] =  0 
                arrayRightAnklePowerTotal[2][FrameNumber] =  RightAnklePowerTotal /float(self.valueBodyMass)
                
                # Transform Ankle Force into Foot CS
                RightAnkleForceFoot = math.TransformVectorIntoMovingCoors(RightAnkleForceLab, RightEFootTibAnat)
                arrayRightAnkleJRF[0][FrameNumber] = RightAnkleForceFoot[0] / float(self.valueBodyMass)
                arrayRightAnkleJRF[1][FrameNumber] = Sign * RightAnkleForceFoot[1] / float(self.valueBodyMass)
                arrayRightAnkleJRF[2][FrameNumber] = RightAnkleForceFoot[2] / float(self.valueBodyMass)
                
                # ============================== Knee ====================================
                # Reverse sign of force and moment from Distal Segment
                RightAnkleForceLab = - RightAnkleForceLab
                RightAnkleMomentLab = - RightAnkleMomentLab
                
                # All Distances are in mm. Account for conversion to meters
                RightKneeForceLab[0] = ShankMass * Direction * arrayRightShankLinearAccelerationLab[0][FrameNumber] /1e3 - RightAnkleForceLab[0]
                RightKneeForceLab[1] = ShankMass * Direction * arrayRightShankLinearAccelerationLab[1][FrameNumber] /1e3 - RightAnkleForceLab[1]
                RightKneeForceLab[2] = ShankMass * arrayRightShankLinearAccelerationLab[2][FrameNumber] /1e3 - RightAnkleForceLab[2] + FootMass * 9.81
                

                # vector from center of mass to proximal point of load application
                ProximalVector = RightKneeCenterLab - RightShankCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = RightAnkleCenterLab - RightShankCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,RightKneeForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,RightAnkleForceLab) / 1e3 # Convert from mm to meters
                
                # Tranform to Shank Coordinate System
                if self.ShankCoordinateSystem == 'Distal':
                    MomentFromProximalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, RightEShankDistalAnat)
                    MomentfromDistalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, RightEShankDistalAnat)
                    RightAnkleMoment_Shank = math.TransformVectorIntoMovingCoors(RightAnkleMomentLab, RightEShankDistalAnat)
                    RightShankAnglesVelocityLab = np.array([arrayRightShankAnglesVelocityLab[0][FrameNumber],arrayRightShankAnglesVelocityLab[1][FrameNumber],arrayRightShankAnglesVelocityLab[2][FrameNumber]])
                    RightShankAnglesAccelerationLab = np.array([arrayRightShankAnglesAccelerationLab[0][FrameNumber],arrayRightShankAnglesAccelerationLab[1][FrameNumber],arrayRightShankAnglesAccelerationLab[2][FrameNumber]])
                    RightKneeAnglesVelocityThigh = np.array([arrayRightKneeAnglesVelocityThigh[0][FrameNumber],arrayRightKneeAnglesVelocityThigh[1][FrameNumber],arrayRightKneeAnglesVelocityThigh[2][FrameNumber]])
                    RightShankAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(RightShankAnglesVelocityLab, RightEShankDistalAnat) 
                    RightShankAnglesAcceleration_Shank = math.TransformVectorIntoMovingCoors(RightShankAnglesAccelerationLab, RightEShankDistalAnat) 
                    # Joint velocity is in proximal segment CS. Transform to Distal
                    RightKneeAnglesVelocityLab = math.TransformVectorIntoLabCoors(RightKneeAnglesVelocityThigh, RightEThighAnat)
                    RightKneeAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(RightKneeAnglesVelocityLab, RightEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    MomentFromProximalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, RightEShankProximalAnat)
                    MomentfromDistalForce_Shank = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, RightEShankProximalAnat)
                    RightAnkleMoment_Shank = math.TransformVectorIntoMovingCoors(RightAnkleMomentLab, RightEShankProximalAnat)
                    RightShankAnglesVelocityLab = np.array([arrayRightShankAnglesVelocityLab[0][FrameNumber],arrayRightShankAnglesVelocityLab[1][FrameNumber],arrayRightShankAnglesVelocityLab[2][FrameNumber]])
                    RightShankAnglesAccelerationLab = np.array([arrayRightShankAnglesAccelerationLab[0][FrameNumber],arrayRightShankAnglesAccelerationLab[1][FrameNumber],arrayRightShankAnglesAccelerationLab[2][FrameNumber]])
                    RightKneeAnglesVelocityThigh = np.array([arrayRightKneeAnglesVelocityThigh[0][FrameNumber],arrayRightKneeAnglesVelocityThigh[1][FrameNumber],arrayRightKneeAnglesVelocityThigh[2][FrameNumber]])
                    RightShankAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(RightShankAnglesVelocityLab, RightEShankProximalAnat) 
                    RightShankAnglesAcceleration_Shank = math.TransformVectorIntoMovingCoors(RightShankAnglesAccelerationLab, RightEShankProximalAnat) 
                    # Joint velocity is in proximal segment CS. Transform to Distal
                    RightKneeAnglesVelocityLab = math.TransformVectorIntoLabCoors(RightKneeAnglesVelocityThigh, RightEThighAnat)
                    RightKneeAnglesVelocity_Shank = math.TransformVectorIntoMovingCoors(RightKneeAnglesVelocityLab, RightEShankProximalAnat)
                
                RightKneeMoment_Shank[0] = RightShankMassMomentOfInertia[0] * RightShankAnglesAcceleration_Shank[0] + \
                                        (RightShankMassMomentOfInertia[2] - RightShankMassMomentOfInertia[1]) * RightShankAnglesVelocity_Shank[1] * RightShankAnglesVelocity_Shank[2] \
                                            - MomentFromProximalForce_Shank[0] - MomentfromDistalForce_Shank[0] - RightAnkleMoment_Shank[0]
                RightKneeMoment_Shank[1] = RightShankMassMomentOfInertia[1] * RightShankAnglesAcceleration_Shank[1] + \
                                        (RightShankMassMomentOfInertia[0] - RightShankMassMomentOfInertia[2]) * RightShankAnglesVelocity_Shank[2] * RightShankAnglesVelocity_Shank[0] \
                                            - MomentFromProximalForce_Shank[1] - MomentfromDistalForce_Shank[1] - RightAnkleMoment_Shank[1]
                RightKneeMoment_Shank[2] = RightShankMassMomentOfInertia[2] * RightShankAnglesAcceleration_Shank[2] + \
                                        (RightShankMassMomentOfInertia[1] - RightShankMassMomentOfInertia[0]) * RightShankAnglesVelocity_Shank[0] * RightShankAnglesVelocity_Shank[1] \
                                            - MomentFromProximalForce_Shank[2] - MomentfromDistalForce_Shank[2] - RightAnkleMoment_Shank[2]

                # Transform Knee Moment to Lab coordinate system
                if self.ShankCoordinateSystem == 'Distal':
                    RightKneeMomentLab = math.TransformVectorIntoLabCoors(RightKneeMoment_Shank,RightEShankDistalAnat)
                if self.ShankCoordinateSystem == 'Proximal':
                    RightKneeMomentLab = math.TransformVectorIntoLabCoors(RightKneeMoment_Shank,RightEShankProximalAnat)
                    
                RightKneePower[0] = RightKneeMoment_Shank[0] * RightKneeAnglesVelocity_Shank[0]
                RightKneePower[1] = RightKneeMoment_Shank[1] * RightKneeAnglesVelocity_Shank[1]
                RightKneePower[2] = RightKneeMoment_Shank[2] * RightKneeAnglesVelocity_Shank[2]
                
                RightKneePowerTotal = np.dot(RightKneeMoment_Shank, RightKneeAnglesVelocity_Shank)
                
                # Normalize and Store in array
                arrayRightKneeMoment[0][FrameNumber] =  -Sign * RightKneeMoment_Shank[0] /float(self.valueBodyMass)
                arrayRightKneeMoment[1][FrameNumber] =  -RightKneeMoment_Shank[1] /float(self.valueBodyMass)
                arrayRightKneeMoment[2][FrameNumber] =  -Sign * RightKneeMoment_Shank[2] /float(self.valueBodyMass)
                
                arrayRightKneePower[0][FrameNumber] =  RightKneePower[0] /float(self.valueBodyMass)
                arrayRightKneePower[1][FrameNumber] =  RightKneePower[1] /float(self.valueBodyMass)
                arrayRightKneePower[2][FrameNumber] =  RightKneePower[2] /float(self.valueBodyMass)
                
                arrayRightKneePowerTotal[0][FrameNumber] =  0 
                arrayRightKneePowerTotal[1][FrameNumber] =  0 
                arrayRightKneePowerTotal[2][FrameNumber] =  RightKneePowerTotal /float(self.valueBodyMass)
                
                # Transform Knee Force into Proximal Tibia CS
                RightKneeForceTib = math.TransformVectorIntoMovingCoors(RightKneeForceLab, RightEShankProximalAnat)
                arrayRightKneeJRF[0][FrameNumber] = RightKneeForceTib[0] / float(self.valueBodyMass)
                arrayRightKneeJRF[1][FrameNumber] = Sign * RightKneeForceTib[1] / float(self.valueBodyMass)
                arrayRightKneeJRF[2][FrameNumber] = RightKneeForceTib[2] / float(self.valueBodyMass)

                # ============================== Hip ====================================
                # Reverse sign of force and moment from Distal Segment
                RightKneeForceLab = - RightKneeForceLab
                RightKneeMomentLab = - RightKneeMomentLab
                
                # All Distances are in mm. Account for conversion to meters
                RightHipForceLab[0] = ThighMass * Direction * arrayRightThighLinearAccelerationLab[0][FrameNumber] /1e3 - RightKneeForceLab[0]
                RightHipForceLab[1] = ThighMass * Direction * arrayRightThighLinearAccelerationLab[1][FrameNumber] /1e3 - RightKneeForceLab[1]
                RightHipForceLab[2] = ThighMass * arrayRightThighLinearAccelerationLab[2][FrameNumber] /1e3 - RightKneeForceLab[2] + FootMass * 9.81
                

                # vector from center of mass to proximal point of load application
                ProximalVector = RightHipCenterLab - RightThighCenterOfMass
                # vector from center of mass to distal point of load application
                DistalVector = RightKneeCenterLab - RightThighCenterOfMass 
                
                MomentFromProximalForce = np.cross(ProximalVector,RightHipForceLab) / 1e3 # Convert from mm to meters
                MomentFromDistalForce = np.cross(DistalVector,RightKneeForceLab) / 1e3 # Convert from mm to meters
                
                # Transform to Thigh Coordinate System
                MomentFromProximalForce_Thigh = math.TransformVectorIntoMovingCoors(MomentFromProximalForce, RightEThighAnat)
                MomentfromDistalForce_Thigh = math.TransformVectorIntoMovingCoors(MomentFromDistalForce, RightEThighAnat)
                RightKneeMoment_Thigh = math.TransformVectorIntoMovingCoors(RightKneeMomentLab, RightEThighAnat)
                RightThighAnglesVelocityLab = np.array([arrayRightThighAnglesVelocityLab[0][FrameNumber],arrayRightThighAnglesVelocityLab[1][FrameNumber],arrayRightThighAnglesVelocityLab[2][FrameNumber]])
                RightThighAnglesAccelerationLab = np.array([arrayRightThighAnglesAccelerationLab[0][FrameNumber],arrayRightThighAnglesAccelerationLab[1][FrameNumber],arrayRightThighAnglesAccelerationLab[2][FrameNumber]])
                RightHipAnglesVelocityPelvis = np.array([arrayRightHipAnglesVelocityPelvis[0][FrameNumber],arrayRightHipAnglesVelocityPelvis[1][FrameNumber],arrayRightHipAnglesVelocityPelvis[2][FrameNumber]])
                RightThighAnglesVelocity_Thigh = math.TransformVectorIntoMovingCoors(RightThighAnglesVelocityLab, RightEThighAnat) 
                RightThighAnglesAcceleration_Thigh = math.TransformVectorIntoMovingCoors(RightThighAnglesAccelerationLab, RightEThighAnat) 
                # Joint velocity is in proximal segment CS. Transform to Distal
                RightHipAnglesVelocityLab = math.TransformVectorIntoLabCoors(RightHipAnglesVelocityPelvis, EPelvisAnat)
                RightHipAnglesVelocity_Thigh = math.TransformVectorIntoMovingCoors(RightHipAnglesVelocityLab, RightEThighAnat)
                
                RightHipMoment_Thigh[0] = RightThighMassMomentOfInertia[0] * RightThighAnglesAcceleration_Thigh[0] + \
                                        (RightThighMassMomentOfInertia[2] - RightThighMassMomentOfInertia[1]) * RightThighAnglesVelocity_Thigh[1] * RightThighAnglesVelocity_Thigh[2] \
                                            - MomentFromProximalForce_Thigh[0] - MomentfromDistalForce_Thigh[0] - RightKneeMoment_Thigh[0]
                RightHipMoment_Thigh[1] = RightThighMassMomentOfInertia[1] * RightThighAnglesAcceleration_Thigh[1] + \
                                        (RightThighMassMomentOfInertia[0] - RightThighMassMomentOfInertia[2]) * RightThighAnglesVelocity_Thigh[2] * RightThighAnglesVelocity_Thigh[0] \
                                            - MomentFromProximalForce_Thigh[1] - MomentfromDistalForce_Thigh[1] - RightKneeMoment_Thigh[1]
                RightHipMoment_Thigh[2] = RightThighMassMomentOfInertia[2] * RightThighAnglesAcceleration_Thigh[2] + \
                                        (RightThighMassMomentOfInertia[1] - RightThighMassMomentOfInertia[0]) * RightThighAnglesVelocity_Thigh[0] * RightThighAnglesVelocity_Thigh[1] \
                                            - MomentFromProximalForce_Thigh[2] - MomentfromDistalForce_Thigh[2] - RightKneeMoment_Thigh[2]

                # Transform Hip Moment to Lab coordinate system
                RightHipMomentLab = math.TransformVectorIntoLabCoors(RightHipMoment_Thigh,RightEThighAnat)
                
                RightHipPower[0] = RightHipMoment_Thigh[0] * RightHipAnglesVelocity_Thigh[0]
                RightHipPower[1] = RightHipMoment_Thigh[1] * RightHipAnglesVelocity_Thigh[1]
                RightHipPower[2] = RightHipMoment_Thigh[2] * RightHipAnglesVelocity_Thigh[2]
                
                RightHipPowerTotal = np.dot(RightHipMoment_Thigh, RightHipAnglesVelocity_Thigh)
                
                # Normalize and Store in array
                arrayRightHipMoment[0][FrameNumber] =  -Sign * RightHipMoment_Thigh[0] /float(self.valueBodyMass)
                arrayRightHipMoment[1][FrameNumber] =  RightHipMoment_Thigh[1] /float(self.valueBodyMass)
                arrayRightHipMoment[2][FrameNumber] =  -Sign * RightHipMoment_Thigh[2] /float(self.valueBodyMass)
                
                arrayRightHipPower[0][FrameNumber] =  RightHipPower[0] /float(self.valueBodyMass)
                arrayRightHipPower[1][FrameNumber] =  RightHipPower[1] /float(self.valueBodyMass)
                arrayRightHipPower[2][FrameNumber] =  RightHipPower[2] /float(self.valueBodyMass)
                
                arrayRightHipPowerTotal[0][FrameNumber] =  0 
                arrayRightHipPowerTotal[1][FrameNumber] =  0 
                arrayRightHipPowerTotal[2][FrameNumber] =  RightHipPowerTotal /float(self.valueBodyMass)
                
                # Transform Hip Force into Thigh CS
                RightHipForceThigh = math.TransformVectorIntoMovingCoors(RightHipForceLab, RightEThighAnat)
                arrayRightHipJRF[0][FrameNumber] = RightHipForceThigh[0] / float(self.valueBodyMass)
                arrayRightHipJRF[1][FrameNumber] = Sign * RightHipForceThigh[1] / float(self.valueBodyMass)
                arrayRightHipJRF[2][FrameNumber] = RightHipForceThigh[2] / float(self.valueBodyMass)
                
                # Add Ground Reaction Forces and Moments: Flip X and Y if walking in -X
                # Correct for Lab CS
                GRF = math.TransformVectorIntoMovingCoors(GRF, ELab)
                # Account for side for ML and scale to BW
                arrayRightGRF[0][FrameNumber] = GRF[0] / float(self.valueBodyMass)
                arrayRightGRF[1][FrameNumber] = Sign * GRF[1] / float(self.valueBodyMass)
                arrayRightGRF[2][FrameNumber] = GRF[2] / float(self.valueBodyMass)
				
                # Add Center of Pressure w.r.t. PELO
                arrayRightGRM[0][FrameNumber] = arrayCOPx[FP_FrameNumber] - arrayPelvisOrigin[0][FrameNumber]
                arrayRightGRM[1][FrameNumber] = arrayCOPy[FP_FrameNumber] - arrayPelvisOrigin[1][FrameNumber]
                arrayRightGRM[2][FrameNumber] = Sign * GRT[2] / float(self.valueBodyMass)
                
                # Store in array of one frame
                COP_Pelvis = np.array([arrayRightGRM[0][FrameNumber], arrayRightGRM[1][FrameNumber], arrayRightGRM[2][FrameNumber]])
                # Correct for Lab CS
                COP_Pelvis = math.TransformVectorIntoMovingCoors(COP_Pelvis, ELab)
                # Write back to GRM, account for direction and side for ML, and scale to % leg length
                arrayRightGRM[0][FrameNumber] = 100 * Direction * COP_Pelvis[0] / self.valueRightLegLength
                arrayRightGRM[1][FrameNumber] = 100 * Sign * Direction * COP_Pelvis[1] / self.valueRightLegLength


                # Index 0 is sum of sagittal plane moment, Index 1 is sum of sagittal power, Index3 is sum of total power
                arrayRightMPSum[0][FrameNumber] = arrayRightHipMoment[0][FrameNumber] + arrayRightKneeMoment[0][FrameNumber]  + \
                                                 arrayRightAnkleMoment[0][FrameNumber]
                arrayRightMPSum[1][FrameNumber] = arrayRightHipPower[0][FrameNumber] + arrayRightKneePower[0][FrameNumber] + \
                                                 arrayRightAnklePower[0][FrameNumber]
                arrayRightMPSum[2][FrameNumber] = arrayRightHipPowerTotal[2][FrameNumber] + arrayRightKneePowerTotal[2][FrameNumber] + \
                                                 arrayRightAnklePowerTotal[2][FrameNumber]
                
                # Add Foot CoP, compute components first and foot length
                AnkleCOP = COP - RightAnkleCenterLab
                AnkleCOP[2] = 0
                # Account for foot progression angle and account for walk direction and M/L
                AnkleCOP_Foot = math.TransformVectorIntoMovingCoors(AnkleCOP, RightEFootAnat)
                FL = np.linalg.norm(RightToeMarker - RightAnkleCenterLab)
                # Normalize
                AnkleCOP_Foot_Normalized = 100 * AnkleCOP_Foot / FL
                arrayRightFootCoP[0][FrameNumber] = AnkleCOP_Foot_Normalized[0]
                arrayRightFootCoP[1][FrameNumber] = -AnkleCOP_Foot_Normalized[1]
                arrayRightFootCoP[2][FrameNumber] = 0
        
        # =============================================================================
        #         Write Kinetics Outputs to C3D File
        # =============================================================================
        XYZNames = ['X','Y','Z']
        ForcesTypes = ['Force','Force','Force']
        MomentsTypes = ['Torque','Torque','Torque']
        MomentsNormalizedTypes = ['TorqueNormalized','TorqueNormalized','TorqueNormalized']
        PowersNormalizedTypes = ['PowerNormalized','PowerNormalized','PowerNormalized']
        ForceNormalizedTypes = ['ForceNormalized','ForceNormalized','ForceNormalized']

        # Left Moments and Power
        if not LeftForcePlate_DeviceID == 0:
            if not 'LHipMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHipMoment',  'Moments', XYZNames, MomentsNormalizedTypes)
            if not 'LKneeMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LKneeMoment', 'Moments', XYZNames, MomentsNormalizedTypes)
            if not 'LAnkleMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LAnkleMoment','Moments', XYZNames, MomentsNormalizedTypes)
            if not 'LHipPower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHipPower',   'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'LKneePower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LKneePower',  'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'LAnklePower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LAnklePower', 'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'LHipPowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHipPowerComponents',   'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'LKneePowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LKneePowerComponents',  'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'LAnklePowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LAnklePowerComponents', 'Powers',  XYZNames, PowersNormalizedTypes)
            # Add JRFs
            if not 'LAnkleForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LAnkleForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'LKneeForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LKneeForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'LHipForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LHipForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            # Add GRFs and GRMs
            if not 'LGroundReactionForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LGroundReactionForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'LGroundReactionMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LGroundReactionMoment', 'Moments',  XYZNames, MomentsNormalizedTypes)
            if not 'LMomentPowerSum' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LMomentPowerSum', 'Moments',  XYZNames, MomentsNormalizedTypes)
            # Add COP
            if not 'LFootCoP' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'LFootCoP', 'Angles', XYZNames, AnglesTypes)
        
        # Right Moments and Power
        if not RightForcePlate_DeviceID == 0:
            if not 'RHipMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHipMoment',  'Moments', XYZNames, MomentsNormalizedTypes)
            if not 'RKneeMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RKneeMoment', 'Moments', XYZNames, MomentsNormalizedTypes)
            if not 'RAnkleMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RAnkleMoment','Moments', XYZNames, MomentsNormalizedTypes)
            if not 'RHipPower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHipPower',   'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'RKneePower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RKneePower',  'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'RAnklePower' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RAnklePower', 'Powers',  XYZNames, PowersNormalizedTypes)  
            if not 'RHipPowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHipPowerComponents',   'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'RKneePowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RKneePowerComponents',  'Powers',  XYZNames, PowersNormalizedTypes)
            if not 'RAnklePowerComponents' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RAnklePowerComponents', 'Powers',  XYZNames, PowersNormalizedTypes)
            
            # Add JRFs
            if not 'RAnkleForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RAnkleForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'RKneeForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RKneeForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'RHipForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RHipForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            # Add GRFs and GRMs
            if not 'RGroundReactionForce' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RGroundReactionForce', 'Forces',  XYZNames, ForceNormalizedTypes)
            if not 'RGroundReactionMoment' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RGroundReactionMoment', 'Moments',  XYZNames, MomentsNormalizedTypes)
            if not 'RMomentPowerSum' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RMomentPowerSum', 'Moments',  XYZNames, MomentsNormalizedTypes)
            # Add COP
            if not 'RFootCoP' in ModelOutputs:
                vicon.CreateModelOutput( SubjectName, 'RFootCoP', 'Angles', XYZNames, AnglesTypes)

            
        # Rearrange all arrays before writing to C3D
        ReArranged_arrayLeftHipMoment = reArrangeArray(arrayLeftHipMoment)
        ReArranged_arrayLeftKneeMoment = reArrangeArray(arrayLeftKneeMoment)
        ReArranged_arrayLeftAnkleMoment = reArrangeArray(arrayLeftAnkleMoment)
        ReArranged_arrayLeftHipPower = reArrangeArray(arrayLeftHipPower)
        ReArranged_arrayLeftKneePower = reArrangeArray(arrayLeftKneePower)
        ReArranged_arrayLeftAnklePower = reArrangeArray(arrayLeftAnklePower)
        ReArranged_arrayLeftHipPowerTotal = reArrangeArray(arrayLeftHipPowerTotal)
        ReArranged_arrayLeftKneePowerTotal = reArrangeArray(arrayLeftKneePowerTotal)
        ReArranged_arrayLeftAnklePowerTotal = reArrangeArray(arrayLeftAnklePowerTotal)
        
        ReArranged_arrayRightHipMoment = reArrangeArray(arrayRightHipMoment)
        ReArranged_arrayRightKneeMoment = reArrangeArray(arrayRightKneeMoment)
        ReArranged_arrayRightAnkleMoment = reArrangeArray(arrayRightAnkleMoment)
        ReArranged_arrayRightHipPower = reArrangeArray(arrayRightHipPower)
        ReArranged_arrayRightKneePower = reArrangeArray(arrayRightKneePower)
        ReArranged_arrayRightAnklePower = reArrangeArray(arrayRightAnklePower)
        ReArranged_arrayRightHipPowerTotal = reArrangeArray(arrayRightHipPowerTotal)
        ReArranged_arrayRightKneePowerTotal = reArrangeArray(arrayRightKneePowerTotal)
        ReArranged_arrayRightAnklePowerTotal = reArrangeArray(arrayRightAnklePowerTotal)
        
        # Write Arrays to C3D Files
        # Left
        if not LeftForcePlate_DeviceID == 0:
            vicon.SetModelOutput(SubjectName, 'LHipMoment', ReArranged_arrayLeftHipMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'LKneeMoment', ReArranged_arrayLeftKneeMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'LAnkleMoment', ReArranged_arrayLeftAnkleMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'LHipPower', ReArranged_arrayLeftHipPowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'LKneePower', ReArranged_arrayLeftKneePowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'LAnklePower', ReArranged_arrayLeftAnklePowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'LHipPowerComponents', ReArranged_arrayLeftHipPower,   exists)
            vicon.SetModelOutput(SubjectName, 'LKneePowerComponents', ReArranged_arrayLeftKneePower,   exists)
            vicon.SetModelOutput(SubjectName, 'LAnklePowerComponents', ReArranged_arrayLeftAnklePower,   exists)
            # Add JRFs to output (not re-arranged)
            vicon.SetModelOutput(SubjectName, 'LAnkleForce', arrayLeftAnkleJRF,   exists)
            vicon.SetModelOutput(SubjectName, 'LKneeForce', arrayLeftKneeJRF,   exists)
            vicon.SetModelOutput(SubjectName, 'LHipForce', arrayLeftHipJRF, exists)
            # Add GRFs and GRMs to output (not re-arranged)
            vicon.SetModelOutput(SubjectName, 'LGroundReactionForce', arrayLeftGRF, exists)
            vicon.SetModelOutput(SubjectName, 'LGroundReactionMoment', arrayLeftGRM, exists)
            # Add Moment and Power Sums and Foot COP
            vicon.SetModelOutput(SubjectName, 'LMomentPowerSum', arrayLeftMPSum, exists)
            vicon.SetModelOutput(SubjectName, 'LFootCoP', arrayLeftFootCoP, exists)

        if not RightForcePlate_DeviceID == 0:
            vicon.SetModelOutput(SubjectName, 'RHipMoment', ReArranged_arrayRightHipMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'RKneeMoment', ReArranged_arrayRightKneeMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'RAnkleMoment', ReArranged_arrayRightAnkleMoment,   exists)
            vicon.SetModelOutput(SubjectName, 'RHipPower', ReArranged_arrayRightHipPowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'RKneePower', ReArranged_arrayRightKneePowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'RAnklePower', ReArranged_arrayRightAnklePowerTotal,   exists)
            vicon.SetModelOutput(SubjectName, 'RHipPowerComponents', ReArranged_arrayRightHipPower,   exists)
            vicon.SetModelOutput(SubjectName, 'RKneePowerComponents', ReArranged_arrayRightKneePower,   exists)
            vicon.SetModelOutput(SubjectName, 'RAnklePowerComponents', ReArranged_arrayRightAnklePower,   exists)
            # Add JRFs to output (not re-arranged)
            vicon.SetModelOutput(SubjectName, 'RAnkleForce', arrayRightAnkleJRF, exists)
            vicon.SetModelOutput(SubjectName, 'RKneeForce', arrayRightKneeJRF, exists)
            vicon.SetModelOutput(SubjectName, 'RHipForce', arrayRightHipJRF, exists)
            # Add GRFs and GRMs to output (not re-arranged)
            vicon.SetModelOutput(SubjectName, 'RGroundReactionForce', arrayRightGRF, exists)
            vicon.SetModelOutput(SubjectName, 'RGroundReactionMoment', arrayRightGRM, exists)
            # Add Moment and Power Sums and Foot CoP
            vicon.SetModelOutput(SubjectName, 'RMomentPowerSum', arrayRightMPSum, exists)
            vicon.SetModelOutput(SubjectName, 'RFootCoP', arrayRightFootCoP, exists)

#Calls the main Function
Dynamic_Main()
