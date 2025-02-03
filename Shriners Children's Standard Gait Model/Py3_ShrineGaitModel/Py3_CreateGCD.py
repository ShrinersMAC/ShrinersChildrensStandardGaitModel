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
# Program to Generate GCD files from C3D Files

Created on Thu May 10 11:50:40 2018
Last Update: Aug 26, 2024

@author: psaraswat
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
VersionNumber = 'Py3_v1.3'

import sys
import numpy as np
import scipy.signal as signal
from datetime import datetime

import tkinter as tk     ## Python 3.x
    
#import Vicon Nexus Subroutines
import ViconNexus
vicon = ViconNexus.ViconNexus()

Small_Font= ("Calibri", 12)
Smaller_Font= ("Calibri", 10)
global SelectedCycleIndex 

NumPointsPerGraph = 101

SubjectName = vicon.GetSubjectNames()[0]
FilePath, FileName = vicon.GetTrialName()
StartFrame, EndFrame = vicon.GetTrialRegionOfInterest()
MarkerFrameRate = vicon.GetFrameRate()
ModelOutputs = vicon.GetModelOutputNames(SubjectName)

# First Argument is the command name, second argument is the testing condition
DefaultTestingCondition = 'BF'
TestingCondition = DefaultTestingCondition
if len(sys.argv) > 1:
    TestingCondition = sys.argv[1]
StaticDataFileName = FilePath + 'Static_' + TestingCondition + '_' + SubjectName + '.py'

  
class CreateGCD_Main():
    def __init__(self):
        exec(open(StaticDataFileName).read()) 
        GCDFileName = FilePath + FileName + '.GCD'
        GCDFile = open(GCDFileName,'w+')
        # Report Generator Requires this line to read GCD file
        GCDFile.write('#!DST-Python3_ShrineGaitModel' + '\n')
        # Write File Creattion Date Time
        GCDFile.write('$FileCreationDateTime' + '\n')
        GCDFile.write(str(datetime.now().date()) + '-' + str(datetime.now().time().hour) + 'h-' + str(datetime.now().time().minute) + 'm-' + str(datetime.now().time().second) + 's' + '\n')
        # Write Program Version
        GCDFile.write('$ProgramVersion' + '\n')
        GCDFile.write(VersionNumber + '\n')
        # Write C3D File Name
        GCDFile.write('$C3DFileName' + '\n')
        GCDFile.write(str(FilePath) + str(FileName) + '.c3d' + '\n')
        # Write Static File Name
        GCDFile.write('$StaticFileName' + '\n')
        GCDFile.write(StaticDataFileName + '\n')
        # Write Body Mass
        GCDFile.write('!Mass' + '\n')
        GCDFile.write(str(self.valueBodyMass) + '\n')
        # Write Height
        GCDFile.write('!Height' + '\n')
        GCDFile.write(str(self.valueHeight) + '\n')
        # Write Left Leg Length
        GCDFile.write('!LeftLegLength' + '\n')
        GCDFile.write(str(self.valueLeftLegLength) + '\n')
        # Write Right Leg Length
        GCDFile.write('!RightLegLength' + '\n')
        GCDFile.write(str(self.valueRightLegLength) + '\n')
        # Write Frame Rate
        GCDFile.write('!VideoRate' + '\n')
        GCDFile.write(str(MarkerFrameRate) + '\n')
        
        # Extract Gait Events
        [LeftFootStrikeEventFrames, LeftFootStrikeEventOffsets] = vicon.GetEvents(SubjectName,'Left','Foot Strike')
        [LeftFootOffEventFrames, LeftFootOffEventOffsets] = vicon.GetEvents(SubjectName,'Left','Foot Off')
        [RightFootStrikeEventFrames, RightFootStrikeEventOffsets] = vicon.GetEvents(SubjectName,'Right','Foot Strike')
        [RightFootOffEventFrames, RightFootOffEventOffsets] = vicon.GetEvents(SubjectName,'Right','Foot Off')
        
        # Event frame rounding, round up if offset is more than 1/2 video frame
        Off_Thresh = 1/(2*vicon.GetFrameRate())
        
        for i in range(len(LeftFootStrikeEventFrames)):
            if LeftFootStrikeEventOffsets[i] >= Off_Thresh:
                LeftFootStrikeEventFrames[i] = LeftFootStrikeEventFrames[i] + 1
        for i in range(len(LeftFootOffEventFrames)):
            if LeftFootOffEventOffsets[i] >= Off_Thresh:
                LeftFootOffEventFrames[i] = LeftFootOffEventFrames[i] + 1
        for i in range(len(RightFootStrikeEventFrames)):
            if RightFootStrikeEventOffsets[i] >= Off_Thresh:
                RightFootStrikeEventFrames[i] = RightFootStrikeEventFrames[i] + 1
        for i in range(len(RightFootOffEventFrames)):
            if RightFootOffEventOffsets[i] >= Off_Thresh:
                RightFootOffEventFrames[i] = RightFootOffEventFrames[i] + 1
        
        # Function to interpolate data to gait cycles
        def ComputeGCDVariable(C3DVariableName,NumPointsPerGraph,Strike1,Strike2):
            C3DVariableX = [0 for m in range(Strike2-Strike1+1)]
            C3DVariableY = [0 for m in range(Strike2-Strike1+1)]
            C3DVariableZ = [0 for m in range(Strike2-Strike1+1)]
            try:
                C3DVariable = np.array([vicon.GetModelOutput(SubjectName, C3DVariableName)][0][0])
                C3DVariableX = C3DVariable[0][Strike1-1:Strike2]
                C3DVariableY = C3DVariable[1][Strike1-1:Strike2]
                C3DVariableZ = C3DVariable[2][Strike1-1:Strike2]
            except:
                pass
            GCD_Time = np.linspace(0, NumPointsPerGraph-1 , NumPointsPerGraph)
            C3D_Time = np.linspace(0, NumPointsPerGraph-1, (Strike2-Strike1+1))
            GCDVariableX = np.interp(GCD_Time, C3D_Time, C3DVariableX)
            GCDVariableY = np.interp(GCD_Time, C3D_Time, C3DVariableY)
            GCDVariableZ = np.interp(GCD_Time, C3D_Time, C3DVariableZ)
            return [GCDVariableX,GCDVariableY,GCDVariableZ]
        
        def ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,C3DVariableName,NumPointsPerGraph,Strike1,Strike2):
            try:
                if EMG_Analog is True:# Analog (MLS)
                    outputID = 0
                    ChannelID = vicon.GetDeviceChannelIDFromName(EMG_AnalogDeviceID,EMG_AnalogDeviceOutputIDs[0],C3DVariableName)
                    outputID = EMG_AnalogDeviceOutputIDs[0]
                    if not outputID == 0:
                        [arrayEMG, Ready, EMG_FrameRate] = vicon.GetDeviceChannel(EMG_AnalogDeviceID, outputID, ChannelID)
                
                if EMG_Digital is True: # Delsys or Noraxon
                    outputID = 0
                    for ID in EMG_DigitalDeviceOutputIDs:
                        name, devtype, unit, ready, channelNames, ChannelIDs = vicon.GetDeviceOutputDetails(EMG_DigitalDeviceID, ID)
                        if name == C3DVariableName:
                            ChannelID = ChannelIDs[0]
                            outputID = ID
                            break
                    if not outputID == 0:
                        [arrayEMG, Ready, EMG_FrameRate] = vicon.GetDeviceChannel(EMG_DigitalDeviceID, outputID, ChannelID)
                
                EMGFrame_Strike1 = int(Strike1 * EMG_FrameRate / MarkerFrameRate)
                EMGFrame_Strike2 = int(Strike2 * EMG_FrameRate / MarkerFrameRate)
                GCDVariable = [0 for m in range(EMGFrame_Strike2 - EMGFrame_Strike1 + 1)]
                for i in range(EMGFrame_Strike1 - 1, EMGFrame_Strike2):
                    GCDVariable[i - EMGFrame_Strike1 + 1] = arrayEMG[i]  
            except:
                GCDVariable = [0 for m in range(Strike2-Strike1+1)]
                
            return GCDVariable
        
        def ComputeGCDVariableFP_Component(FP,FP_DeviceID,NumPointsPerGraph,Strike1,Strike2):
            try:
                [arrayFx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 1, 1)
                [arrayFy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 1, 2)
                [arrayFz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 1, 3)
                
                [arrayMx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 2, 1)
                [arrayMy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 2, 2)
                [arrayMz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 2, 3)
                
                [arrayCOPx, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 3, 1)
                [arrayCOPy, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 3, 2)
                [arrayCOPz, Ready, FP_FrameRate] = vicon.GetDeviceChannelGlobal(FP_DeviceID, 3, 3)
                
                
                FP_Origin = FP.LocalT # Local Origin- Usually zero
                FP_Center = FP.WorldT # Force Plate Center
                
                FPFrame_Strike1 = int(Strike1 * FP_FrameRate/ MarkerFrameRate)
                FPFrame_Strike2 = int(Strike2 * FP_FrameRate/ MarkerFrameRate)
                C3DVariable_GRFx = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRFy = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRFz = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRTz = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_COPx = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_COPy = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                
                
                for i in range(FPFrame_Strike1-1,FPFrame_Strike2): # Return reaction -ve value of force observed by Force Plate
                    C3DVariable_GRFx[i-FPFrame_Strike1 + 1]= -(arrayFx[i]) / (self.valueBodyMass*9.81)
                    C3DVariable_GRFy[i-FPFrame_Strike1 + 1]= -(arrayFy[i]) / (self.valueBodyMass*9.81)
                    C3DVariable_GRFz[i-FPFrame_Strike1 + 1]= -(arrayFz[i]) / (self.valueBodyMass*9.81)
                    
                    Tz= (arrayMz[i] + arrayFx[i] * (arrayCOPy[i] - FP_Center[1] + FP_Origin[1]) - arrayFy[i] * (arrayCOPx[i] -FP_Center[0] + FP_Origin[0]))
                    C3DVariable_GRTz[i-FPFrame_Strike1 + 1]= -Tz / (self.valueBodyMass*9.81)
                    
                    C3DVariable_COPx[i-FPFrame_Strike1 + 1]= arrayCOPx[i]
                    C3DVariable_COPy[i-FPFrame_Strike1 + 1]= arrayCOPy[i]
                    
                GCD_Time = np.linspace(0, NumPointsPerGraph-1 , NumPointsPerGraph)
                C3D_Time = np.linspace(0, NumPointsPerGraph-1, (FPFrame_Strike2-FPFrame_Strike1+1))
                
                GCDVariable_GRFx = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFx)
                GCDVariable_GRFy = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFy)
                GCDVariable_GRFz = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFz)
                GCDVariable_GRTz = np.interp(GCD_Time, C3D_Time, C3DVariable_GRTz)
                GCDVariable_COPx = np.interp(GCD_Time, C3D_Time, C3DVariable_COPx)
                GCDVariable_COPy = np.interp(GCD_Time, C3D_Time, C3DVariable_COPy)
            except:
                FPFrame_Strike1 = int(Strike1 * FP_FrameRate/ MarkerFrameRate)
                FPFrame_Strike2 = int(Strike2 * FP_FrameRate/ MarkerFrameRate)
                C3DVariable_GRFx = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRFy = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRFz = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_GRTz = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_COPx = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                C3DVariable_COPy = [0 for m in range(FPFrame_Strike2-FPFrame_Strike1+1)]
                
                GCD_Time = np.linspace(0, NumPointsPerGraph-1 , NumPointsPerGraph)
                C3D_Time = np.linspace(0, NumPointsPerGraph-1, (FPFrame_Strike2-FPFrame_Strike1+1))
                
                GCDVariable_GRFx = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFx)
                GCDVariable_GRFy = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFy)
                GCDVariable_GRFz = np.interp(GCD_Time, C3D_Time, C3DVariable_GRFz)
                GCDVariable_GRTz = np.interp(GCD_Time, C3D_Time, C3DVariable_GRTz)
                GCDVariable_COPx = np.interp(GCD_Time, C3D_Time, C3DVariable_COPx)
                GCDVariable_COPy = np.interp(GCD_Time, C3D_Time, C3DVariable_COPy)
                
            return [GCDVariable_GRFx,GCDVariable_GRFy,GCDVariable_GRFz,GCDVariable_GRTz,GCDVariable_COPx,GCDVariable_COPy]
            
        def WriteArrayToGCD(GCDFile, GCDVariableName, GCDVariable):
            GCDFile.write('!' + GCDVariableName + '\n')
            for i in range(len(GCDVariable)):
                GCDFile.write(str(np.format_float_positional(float(GCDVariable[i]),precision=6))  + '\n')
                
        def WriteSingleValueToGCD(GCDFile, GCDVariableName, GCDVariable):
            GCDFile.write('!' + GCDVariableName + '\n')
            GCDFile.write(str(np.format_float_positional(float(GCDVariable),precision=6))  + '\n')   
        
        def WriteArrayToGCD_ComputeEMGenvelope(GCDFile, GCDVariableName, GCDVariable,
                                               AveragingWindowSizeInMiliseconds):
            GCDFile.write('!' + GCDVariableName + '\n')
            for i in range(len(GCDVariable)):
                GCDFile.write(str(round(float(GCDVariable[i]), 6)) + '\n')

            # Envelope
            GCD_Time = np.linspace(0, NumPointsPerGraph - 1, NumPointsPerGraph)
            EMG_Time = np.linspace(0, NumPointsPerGraph - 1, len(GCDVariable))

            # Find Signal Frequency
            EMG_DeviceID = 0
            DeviceIDs = vicon.GetDeviceIDs()
            for DeviceID in DeviceIDs:
                [Device_name, Device_type, Device_rate, Device_deviceOutputIDs, Device_forceplate,
                 Device_eyetracker] = vicon.GetDeviceDetails(DeviceID)
                if Device_type == 'Other':
                    name, output_type, unit, ready, channelNames, channelIDs = vicon.GetDeviceOutputDetails(DeviceID, Device_deviceOutputIDs[0])
                    if 'Potential' not in output_type: # Skip instrumented device such as Walker, Transducer
                        if 'Digital' in output_type: # Noraxon
                            EMG_DeviceID = DeviceID
                            EMG_DeviceOutputIDs = Device_deviceOutputIDs
                        else:
                            if 'volt' in unit: # MLS or Delsys
                                if len(channelNames) > 1: # MLS
                                    EMG_DeviceID = DeviceID
                                    EMG_DeviceOutputIDs = Device_deviceOutputIDs
                                else:
                                   if 'IM' in channelNames[0]:
                                       EMG_DeviceID = DeviceID
                                       EMG_DeviceOutputIDs = Device_deviceOutputIDs
            if not EMG_DeviceID == 0:
                if not EMG_Digital:
                    ChannelID = vicon.GetDeviceChannelIDFromName(EMG_DeviceID, EMG_DeviceOutputIDs[0],
                                                             self.LeftRectusFemorisEMGName)
                    outputID = EMG_DeviceOutputIDs[0]
                else:
                    for ID in EMG_DeviceOutputIDs:
                        name, devtype, unit, ready, channelNames, ChannelIDs = vicon.GetDeviceOutputDetails(EMG_DeviceID, ID)
                        if name == self.LeftRectusFemorisEMGName:
                            ChannelID = ChannelIDs[0]
                            outputID = ID
                try:
                    [arrayEMG, Ready, EMG_FrameRate] = vicon.GetDeviceChannel(EMG_DeviceID, outputID, ChannelID)
                    SignalFrequency = EMG_FrameRate
                except:
                    SignalFrequency = 10 * MarkerFrameRate
            else:
                SignalFrequency = 10 * MarkerFrameRate
            
            # Set Signal Frequency to non-zero
            if SignalFrequency == 0:
                SignalFrequency = 10 * MarkerFrameRate
            ###########################################

            # Design the Buterworth filter
            FilterOrder  = 5    
            CutOffFrequency = 10 
            B, A = signal.butter(FilterOrder,CutOffFrequency/(SignalFrequency/2.0),btype='high',output='ba')
            
            # Apply the filter
            GCDVariable_Filtered = signal.filtfilt(B,A, GCDVariable)
            
            # Rectify the signal
            GCDVariable_Rectified = abs(GCDVariable_Filtered)
            
            # Compute window average
            WindowSizeTime = AveragingWindowSizeInMiliseconds # ms
            WindowSize = int(WindowSizeTime*(1000/SignalFrequency))
            GCDVariable_WindowAveraged = GCDVariable_Rectified
            for i in range(len(GCDVariable_Rectified)):
                if i < WindowSize/2:       
                    GCDVariable_WindowAveraged[i] =  sum(GCDVariable_WindowAveraged[i:WindowSize-i])/len(GCDVariable[i:WindowSize-i])
                else:
                    GCDVariable_WindowAveraged[i] =  sum(GCDVariable_WindowAveraged[i-int(WindowSize/2):i+int(WindowSize/2)])/len(GCDVariable[i-int(WindowSize/2):i+int(WindowSize/2)])
                    if i > len(GCDVariable_Rectified) - (WindowSize/2):
                        GCDVariable_WindowAveraged[i] =  sum(GCDVariable_WindowAveraged[i-(WindowSize-(len(GCDVariable_Rectified)-i)):len(GCDVariable_Rectified)])/len(GCDVariable[i-(WindowSize-(len(GCDVariable_Rectified)-i)):len(GCDVariable_Rectified)])

            # Compute Envelope
            GCDVariable_Envelope = np.interp(GCD_Time, EMG_Time, GCDVariable_WindowAveraged)

            GCDFile.write('!' + GCDVariableName + 'Envelope' + '\n')
            for i in range(len(GCDVariable_Envelope)):
                GCDFile.write(str(round(float(GCDVariable_Envelope[i]), 6)) + '\n')
                    

        
        # Left
        LeftStrike1 = 0.
        LeftStrike2 = 0.
        LeftToeOff = 0.
        LeftOppositeToeOff = 0.
        LeftOppositeFootStrike = 0.
        if len(LeftFootStrikeEventFrames) >= 2:
            
            if len(LeftFootStrikeEventFrames) > 2:
                # More than one Left Gait Cycle Found
                
                # Open a window to display page selection
                popup = self.popup = tk.Tk()
                #popup.resizable(0,0)
                #popup.geometry('%dx%d+%d+%d' % (600, 200, 0, 0))
                #Centers the App on Monitor
                AppWidth = 600
                AppHeight= 200
                ScreenWidth = 1600#self.winfo_screenwidth()
                ScreenHeight = 1000#self.winfo_screenheight()
                x=(ScreenWidth/2) - (AppWidth/2)
                y=(ScreenHeight/2)- (AppHeight/2) #Put the App at center of Monitor
                #y=100
                popup.geometry('%dx%d+%d+%d' % (AppWidth, AppHeight, x, y))
                popup.title('Gait Cycle Selection')
                
                
                # Add Save PDF Button
                ProceedButton = tk.Button(popup, text="Proceed", command= lambda: [ReadCycleSelectionLeft(), self.popup.destroy()], font=Small_Font, justify = 'center')#anchor = 'se')
                ProceedButton.place(x=10,y=200-60,width=600-100,height=50) 
                # Exit Button
                CancelButton = tk.Button(popup, text="Cancel", command=lambda: cancelLeft(), font=Small_Font, justify = 'center')
                CancelButton.place(x=600-80,y=200-60,width = 70, height = 50)
                
                #print 'IC   OTO     OIC     TO  IC'
                TitleLabelText = 'Side' + ' \t' + 'IC' + ' \t' + 'OTO' + ' \t' + 'OIC' + ' \t' + 'TO' + ' \t' + 'IC'
                TitleLabel = tk.Label(popup, text=TitleLabelText,font=Small_Font, justify = 'left')
                TitleLabel.place(x=45,y=10)
                
                numCycleIndex = tk.IntVar()
                for numCycle in range(len(LeftFootStrikeEventFrames)-1):
                    LeftStrike1 = 0.
                    LeftStrike2 = 0.
                    LeftToeOff = 0.
                    LeftOppositeToeOff = 0.
                    LeftOppositeFootStrike = 0.
                    LeftStrike1 = sorted(LeftFootStrikeEventFrames)[numCycle]
                    LeftStrike2 = sorted(LeftFootStrikeEventFrames)[numCycle + 1]
                    for i in range(len(LeftFootOffEventFrames)):
                        if LeftFootOffEventFrames[i] > LeftStrike1 and LeftFootOffEventFrames[i] < LeftStrike2:
                            LeftToeOff = LeftFootOffEventFrames[i]
                    for i in range(len(RightFootOffEventFrames)):
                         if RightFootOffEventFrames[i] > LeftStrike1 and RightFootOffEventFrames[i] < LeftToeOff:
                            LeftOppositeToeOff = RightFootOffEventFrames[i]
                    for i in range(len(RightFootStrikeEventFrames)):
                         if RightFootStrikeEventFrames[i] > LeftStrike1 and RightFootStrikeEventFrames[i] < LeftToeOff:
                            LeftOppositeFootStrike = RightFootStrikeEventFrames[i] 
                    # Change to blank if value not found
                    if LeftToeOff == 0:
                        StringLeftToeOff = '   '
                    else:
                        StringLeftToeOff = str(LeftToeOff)
                    if LeftOppositeToeOff == 0:
                        StringLeftOppositeToeOff = '   '
                    else:
                        StringLeftOppositeToeOff = str(LeftOppositeToeOff)
                    if LeftOppositeFootStrike == 0:
                        StringLeftOppositeFootStrike = '   '
                    else:
                        StringLeftOppositeFootStrike = str(LeftOppositeFootStrike)
                        
                    numCycleButtonText = 'Left' + ' \t' + str(LeftStrike1) + ' \t' + StringLeftOppositeToeOff + ' \t' + StringLeftOppositeFootStrike + ' \t' + StringLeftToeOff + ' \t' + str(LeftStrike2) + '\n'
                    
                    numCycleButton = tk.Radiobutton(popup, text=numCycleButtonText, variable = numCycleIndex, value=numCycle, font=Small_Font, command= lambda: ReadCycleSelectionLeft(), anchor = 'center',background='white') 
                    numCycleButton.place(x=10, y = 10 + (numCycle + 1)*35, height = 30, width = 400)                    
                    
                    if LeftStrike1 == 0 or LeftStrike2 == 0 or LeftToeOff == 0 or LeftOppositeToeOff == 0 or LeftOppositeFootStrike == 0:
                        WarningLabel = tk.Label(popup,text="Missing Gait Events!!!", font=Small_Font,justify= 'center',foreground='red')
                        WarningLabel.place(x=420,y=10 + (numCycle + 1)*35, height = 30,)
                        

                
                def cancelLeft():
                    popup.destroy
                    sys.exit()
                    
                def ReadCycleSelectionLeft():
                    global SelectedCycleIndex 
                    SelectedCycleIndex = numCycleIndex.get()
                    LeftStrike1 = 0.
                    LeftStrike2 = 0.
                    LeftToeOff = 0.
                    LeftOppositeToeOff = 0.
                    LeftOppositeFootStrike = 0.
                    LeftStrike1 = sorted(LeftFootStrikeEventFrames)[SelectedCycleIndex ]
                    LeftStrike2 = sorted(LeftFootStrikeEventFrames)[SelectedCycleIndex  + 1]
                    for i in range(len(LeftFootOffEventFrames)):
                        if LeftFootOffEventFrames[i] > LeftStrike1 and LeftFootOffEventFrames[i] < LeftStrike2:
                            LeftToeOff = LeftFootOffEventFrames[i]
                    for i in range(len(RightFootOffEventFrames)):
                         if RightFootOffEventFrames[i] > LeftStrike1 and RightFootOffEventFrames[i] < LeftToeOff:
                            LeftOppositeToeOff = RightFootOffEventFrames[i]
                    for i in range(len(RightFootStrikeEventFrames)):
                         if RightFootStrikeEventFrames[i] > LeftStrike1 and RightFootStrikeEventFrames[i] < LeftToeOff:
                            LeftOppositeFootStrike = RightFootStrikeEventFrames[i] 
                    if LeftStrike1 == 0 or LeftStrike2 == 0 or LeftToeOff == 0 or LeftOppositeToeOff == 0 or LeftOppositeFootStrike == 0:
                        ProceedButton.place_forget()
                    else:
                        ProceedButton.place(x=10,y=200-60,width=600-100,height=50)
                        
                ReadCycleSelectionLeft()
                popup.mainloop()
                
                
                LeftStrike1 = sorted(LeftFootStrikeEventFrames)[SelectedCycleIndex ]
                LeftStrike2 = sorted(LeftFootStrikeEventFrames)[SelectedCycleIndex  + 1]
                for i in range(len(LeftFootOffEventFrames)):
                    if LeftFootOffEventFrames[i] > LeftStrike1 and LeftFootOffEventFrames[i] < LeftStrike2:
                        LeftToeOff = LeftFootOffEventFrames[i]
                for i in range(len(RightFootOffEventFrames)):
                     if RightFootOffEventFrames[i] > LeftStrike1 and RightFootOffEventFrames[i] < LeftToeOff:
                        LeftOppositeToeOff = RightFootOffEventFrames[i]
                for i in range(len(RightFootStrikeEventFrames)):
                     if RightFootStrikeEventFrames[i] > LeftStrike1 and RightFootStrikeEventFrames[i] < LeftToeOff:
                        LeftOppositeFootStrike = RightFootStrikeEventFrames[i] 
                    
            
                    
            if len(LeftFootStrikeEventFrames) == 2:
                # Left Gait Cycle Found
                LeftStrike1 = min(LeftFootStrikeEventFrames[0],LeftFootStrikeEventFrames[1])
                LeftStrike2 = max(LeftFootStrikeEventFrames[0],LeftFootStrikeEventFrames[1])
                for i in range(len(LeftFootOffEventFrames)):
                    if LeftFootOffEventFrames[i] > LeftStrike1 and LeftFootOffEventFrames[i] < LeftStrike2:
                        LeftToeOff = LeftFootOffEventFrames[i]
                for i in range(len(RightFootOffEventFrames)):
                     if RightFootOffEventFrames[i] > LeftStrike1 and RightFootOffEventFrames[i] < LeftToeOff:
                        LeftOppositeToeOff = RightFootOffEventFrames[i]
                for i in range(len(RightFootStrikeEventFrames)):
                     if RightFootStrikeEventFrames[i] > LeftStrike1 and RightFootStrikeEventFrames[i] < LeftToeOff:
                        LeftOppositeFootStrike = RightFootStrikeEventFrames[i]
                
                if LeftOppositeFootStrike == 0 or LeftOppositeToeOff == 0:
                    popup = tk.Tk()
                    popup.resizable(0,0)
                    AppWidth = 400
                    AppHeight= 50
                    ScreenWidth = 1600#self.winfo_screenwidth()
                    ScreenHeight = 1000#self.winfo_screenheight()
                    x=(ScreenWidth/2) - (AppWidth/2)
                    y=(ScreenHeight/2)- (AppHeight/2) #Put the App at center of Monitor
                    popup.geometry('%dx%d+%d+%d' % (AppWidth, AppHeight, x, y))
                    popup.title('Warning')
                    WarningMessage = tk.Label(popup,text="Left Side: Missing Gait Events!!!", font=Small_Font,justify= 'center',foreground='red')
                    WarningMessage.pack()
                    popup.mainloop()
                    
            #print str(LeftStrike1) + ' \t' + str(LeftOppositeToeOff) + ' \t' + str(LeftOppositeFootStrike) + ' \t' + str(LeftToeOff) + ' \t' + str(LeftStrike2) + '\n'
            # Compute Stride Temporal Parameters
            LeftAnkleMarker_Strike1 = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.LeftLateralAnkleMarkerName, LeftStrike1)[0:3])
            LeftAnkleMarker_Strike2 = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.LeftLateralAnkleMarkerName, LeftStrike2)[0:3])
            RightAnkleMarker_OppositeFootContact = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.RightLateralAnkleMarkerName, LeftOppositeFootStrike)[0:3])
            RightAnkleMarker_OppositeToeOff = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.RightLateralAnkleMarkerName, LeftOppositeToeOff)[0:3])
            LeftStrideLength = np.linalg.norm(LeftAnkleMarker_Strike2 - LeftAnkleMarker_Strike1) # mm
            LeftStrideLength_CM = LeftStrideLength/10 # cm
            LeftStepLength = np.linalg.norm(LeftAnkleMarker_Strike2 - RightAnkleMarker_OppositeFootContact) # mm
            LeftStepLength_CM = LeftStepLength/10 # m
            LeftStrideTime = (LeftStrike2 - LeftStrike1) / MarkerFrameRate # Seconds
            LeftStepTime = (LeftStrike2 - LeftToeOff) / MarkerFrameRate # Seconds
            LeftCadence = (1/LeftStrideTime) # /sec
            LeftCadence_StepsPerMin = (1/LeftStrideTime) * 2 * 60 # Steps/min
            
            LeftSpeed = LeftStrideLength / LeftStrideTime # mm/sec
            LeftSpeed_CMPerSec = LeftStrideLength / (LeftStrideTime * 10) # cm/sec
            
            LeftFootOff=100*(float(LeftToeOff)-float(LeftStrike1))/(float(LeftStrike2)-float(LeftStrike1))
            LeftOppositeFootOff=100*(float(LeftOppositeToeOff)-float(LeftStrike1))/(float(LeftStrike2)-float(LeftStrike1))
            LeftOppositeFootContact=100*(float(LeftOppositeFootStrike)-float(LeftStrike1))/(float(LeftStrike2)-float(LeftStrike1))
            LeftStance = LeftFootOff
            LeftDoubleSupport1 = 100*(float(LeftOppositeToeOff)-float(LeftStrike1))/(float(LeftStrike2)-float(LeftStrike1))
            LeftSingleSupport  = 100*(float(LeftOppositeFootStrike)-float(LeftOppositeToeOff))/(float(LeftStrike2)-float(LeftStrike1))
            LeftDoubleSupport2 = 100*(float(LeftToeOff)-float(LeftOppositeFootStrike))/(float(LeftStrike2)-float(LeftStrike1))
            LeftSwing = 100*(float(LeftStrike2)-float(LeftToeOff))/(float(LeftStrike2)-float(LeftStrike1))
            LeftDoubleSupport  = LeftDoubleSupport1 + LeftDoubleSupport2
                        
            # Compute GCD Variables
            [LeftTrunkTilt,LeftTrunkObliquity,LeftTrunkRotation]    = ComputeGCDVariable('LTrunkAngles' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftPelvicTilt,LeftPelvicObliquity,LeftPelvicRotation] = ComputeGCDVariable('LPelvisAngles', NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftHipFlexExt,LeftHipAbAdduct,LeftHipRotation]        = ComputeGCDVariable('LHipAngles'   , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftKneeFlexExt,LeftKneeValgVar,LeftKneeRotation]      = ComputeGCDVariable('LKneeAngles'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [DummyX,DummyY,LeftKneeRotation_Proximal]      = ComputeGCDVariable('LKneeAnglesProximal'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftDorsiPlanFlex,DummyY,LeftFootRotation]             = ComputeGCDVariable('LAnkleAngles' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftFootSagittalInclination,DummyY,LeftFootProgression]        = ComputeGCDVariable('LFootProgressAngles'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            # Compute Pelvis, Knee and Ankle Progression GCD Variables
            [LeftFemurSagittalInclination,DummyY,LeftFemurProgression]      = ComputeGCDVariable('LThighAngles'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftTibiaSagittalInclination,DummyY,LeftTibiaProgression]      = ComputeGCDVariable('LShankAngles'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            
            # Muscle Length 
            [LeftGluteusMaxLength,DummyY,DummyZ]    = ComputeGCDVariable('GluteusMaxLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftIlioPsoasLength,DummyY,DummyZ]    = ComputeGCDVariable('IlioPsoasLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftRectFemLength,DummyY,DummyZ]    = ComputeGCDVariable('RectFemLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftMedHamstringLength,DummyY,DummyZ]    = ComputeGCDVariable('MedHamstringLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftLatHamstringLength,DummyY,DummyZ]    = ComputeGCDVariable('LatHamstringLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftGastrocLength,DummyY,DummyZ]    = ComputeGCDVariable('GastrocLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftSoleusLength,DummyY,DummyZ]    = ComputeGCDVariable('SoleusLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftTibPostLength,DummyY,DummyZ]    = ComputeGCDVariable('TibPostLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftPeronealLength,DummyY,DummyZ]    = ComputeGCDVariable('PeronealLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftVastusLatLength,DummyY,DummyZ]    = ComputeGCDVariable('VastusLatLength' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            # Muscle Velocity 
            [LeftGluteusMaxVelocity,DummyY,DummyZ]    = ComputeGCDVariable('GluteusMaxVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftIlioPsoasVelocity,DummyY,DummyZ]    = ComputeGCDVariable('IlioPsoasVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftRectFemVelocity,DummyY,DummyZ]    = ComputeGCDVariable('RectFemVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftMedHamstringVelocity,DummyY,DummyZ]    = ComputeGCDVariable('MedHamstringVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftLatHamstringVelocity,DummyY,DummyZ]    = ComputeGCDVariable('LatHamstringVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftGastrocVelocity,DummyY,DummyZ]    = ComputeGCDVariable('GastrocVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftSoleusVelocity,DummyY,DummyZ]    = ComputeGCDVariable('SoleusVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftTibPostVelocity,DummyY,DummyZ]    = ComputeGCDVariable('TibPostVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftPeronealVelocity,DummyY,DummyZ]    = ComputeGCDVariable('PeronealVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            [LeftVastusLatVelocity,DummyY,DummyZ]    = ComputeGCDVariable('VastusLatVelocity' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
            
            
            
            # Check if Kinetics Data exist
            if 'LAnklePowerComponents' in ModelOutputs:
                [LeftHipFlexExtMoment,LeftHipAbAdductMoment,LeftHipRotationMoment]      = ComputeGCDVariable('LHipMoment'   , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftKneeFlexExtMoment,LeftKneeValgVarMoment,LeftKneeRotationMoment]    = ComputeGCDVariable('LKneeMoment'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftDorsiPlanFlexMoment,LeftFootAbAdductMoment,LeftFootRotationMoment] = ComputeGCDVariable('LAnkleMoment' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                
                [LeftHipFlexExtPower,LeftHipAbAdductPower,LeftHipRotationPower]         = ComputeGCDVariable('LHipPowerComponents'    , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftKneeFlexExtPower,LeftKneeValgVarPower,LeftKneeRotationPower]       = ComputeGCDVariable('LKneePowerComponents'   , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftDorsiPlanFlexPower,LeftFootAbAdductPower,LeftFootRotationPower]    = ComputeGCDVariable('LAnklePowerComponents'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                
                [DummyX,DummyY,LeftHipPowerTotal]         = ComputeGCDVariable('LHipPower'    , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [DummyX,DummyY,LeftKneePowerTotal]       = ComputeGCDVariable('LKneePower'   , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [DummyX,DummyY,LeftAnklePowerTotal]    = ComputeGCDVariable('LAnklePower'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                
                # Check for Force Plate Hits
                LeftForcePlate_DeviceID = 0 #Default Value if Force Plate Hit is not Found
                DeviceIDs = vicon.GetDeviceIDs()
                for DeviceID in DeviceIDs:
                    [name, type, rate, deviceOutputIDs, forceplate, eyetracker] = vicon.GetDeviceDetails(DeviceID)
                    if forceplate.Context == 'Left':
                        LeftForcePlate_DeviceID = DeviceID
                        Left_ForcePlate = forceplate
                [LeftGRFx, LeftGRFy, LeftGRFz, LeftGRTz, LeftCOPx, LeftCOPy] = ComputeGCDVariableFP_Component(Left_ForcePlate,LeftForcePlate_DeviceID,NumPointsPerGraph,LeftStrike1,LeftStrike2)
                
                LeftAnkleVector_Strike1_To_Strike2 = LeftAnkleMarker_Strike2 - LeftAnkleMarker_Strike1
                if abs(LeftAnkleVector_Strike1_To_Strike2[0]) > abs(LeftAnkleVector_Strike1_To_Strike2[1]):
                    if LeftAnkleVector_Strike1_To_Strike2[0] > 0: 
                        # Walking Direction +X
                        LeftGRF_Anterior    = LeftGRFx
                        LeftGRF_Medial      = -LeftGRFy
                        LeftGRF_Vertical    = LeftGRFz
                        LeftGRT_Vertical    = -LeftGRTz
                    else: 
                        # Walking Direction -X
                        LeftGRF_Anterior = -LeftGRFx
                        LeftGRF_Medial = LeftGRFy
                        LeftGRF_Vertical = LeftGRFz
                        LeftGRT_Vertical = -LeftGRTz
                else:
                    if LeftAnkleVector_Strike1_To_Strike2[1] > 0: 
                        # Walking Direction +y
                        LeftGRF_Anterior    = LeftGRFy
                        LeftGRF_Medial      = LeftGRFx
                        LeftGRF_Vertical    = LeftGRFz
                        LeftGRT_Vertical    = -LeftGRTz
                    else:
                        # Walking Direction -Y
                        LeftGRF_Anterior = -LeftGRFy
                        LeftGRF_Medial = -LeftGRFx
                        LeftGRF_Vertical = LeftGRFz
                        LeftGRT_Vertical = -LeftGRTz
                    
                
            # Check if EMG Data exist
            EMG_DigitalDeviceID = 0
            EMG_AnalogDeviceID = 0
            EMG_DigitalDeviceOutputIDs = 0
            EMG_AnalogDeviceOutputIDs = 0
            EMG_Digital = False
            EMG_Analog = False
            DeviceIDs = vicon.GetDeviceIDs()
            try:
                for DeviceID in DeviceIDs:
                    [Device_name, Device_type, Device_rate, Device_deviceOutputIDs, Device_forceplate, Device_eyetracker] = vicon.GetDeviceDetails(DeviceID)
                    if Device_type == 'Other':
                        name, output_type, unit, ready, channelNames, channelIDs = vicon.GetDeviceOutputDetails(DeviceID, Device_deviceOutputIDs[0])
                        if 'Potential' not in output_type: # Skip instrumented device such as Walker, Transducer
                            if 'Digital' in output_type: # Noraxon
                                EMG_Digital = True
                                EMG_DigitalDeviceID = DeviceID
                                EMG_DigitalDeviceOutputIDs = Device_deviceOutputIDs
                            else:
                                if 'volt' in unit: # MLS or Delsys
                                    if len(channelNames) > 1: # MLS / Analog
                                        EMG_Analog = True
                                        EMG_AnalogDeviceID = DeviceID
                                        EMG_AnalogDeviceOutputIDs = Device_deviceOutputIDs
                                    else:
                                       if 'IM' in channelNames[0]: # Delsys
                                           EMG_Digital = True
                                           EMG_DigitalDeviceID = DeviceID
                                           EMG_DigitalDeviceOutputIDs = Device_deviceOutputIDs
            except:
                pass
                           
            if EMG_DigitalDeviceID != 0 or EMG_AnalogDeviceID != 0:
                LeftRectusFemorisEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftRectusFemorisEMGName,     NumPointsPerGraph,LeftStrike1,LeftStrike2)
                LeftVasltusLateralisEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftVasltusLateralisEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                LeftMedialHamstringsEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftMedialHamstringsEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                LeftGastrocnemiusEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftGastrocnemiusEMGName,     NumPointsPerGraph,LeftStrike1,LeftStrike2)
                LeftTibialisAnteriorEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftTibialisAnteriorEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                # Lexington 
                try:
                    LeftGluteusMaximusEMG   = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftGluteusMaximusEMGName,    NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                try:
                    LeftGluteusMediusEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftGluteusMediusEMGName,     NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                try:
                    LeftAdductorsEMG        = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftAdductorsEMGName,         NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                # Montreal
                try:
                    LeftVasltusMedialisEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftVasltusMedialisEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                try:
                    LeftLateralHamstringsEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftLateralHamstringsEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                try:
                    LeftPeroneusLongusEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.LeftPeroneusLongusEMGName,  NumPointsPerGraph,LeftStrike1,LeftStrike2)
                except:
                    pass
                
            # Check if Foot Model data exists
            if self.valueLeftFootModelCheck == '1':
                [LeftHindFootTilt,LeftHindFootObliquity,LeftHindFootRotation]                    = ComputeGCDVariable('LHFGA' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftForeFootTilt,LeftForeFootObliquity,LeftForeFootRotation]                    = ComputeGCDVariable('LFFGA' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftAnkleComplexDorsiPlanFlex,LeftAnkleComplexValgVar,LeftAnkleComplexRotation] = ComputeGCDVariable('LANKA' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftMidFootDorsiPlanFlex,LeftMidFootSupPron,LeftMidFootAbAdduct]                = ComputeGCDVariable('LMDFA' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftToeFlexExt,DummyY,LeftToeValgVar]                                           = ComputeGCDVariable('LHLXA' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftSupination,DummyY,DummyZ]                                                   = ComputeGCDVariable('Supination' , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                [LeftSkew,DummyY,DummyZ]                                                         = ComputeGCDVariable('Skew'  , NumPointsPerGraph, LeftStrike1, LeftStrike2)
                
            
            
        # Right    
        RightStrike1 = 0.
        RightStrike2 = 0.
        RightToeOff = 0.
        RightOppositeToeOff = 0.
        RightOppositeFootStrike = 0.
        if len(RightFootStrikeEventFrames) >= 2:
            
            if len(RightFootStrikeEventFrames) > 2:
                # More than one Right Gait Cycle Found
                
                # Open a window to display page selection
                popup = self.popup = tk.Tk()
                #popup.resizable(0,0)
                #popup.geometry('%dx%d+%d+%d' % (600, 200, 0, 0))
                #Centers the App on Monitor
                AppWidth = 600
                AppHeight= 200
                ScreenWidth = 1600#self.winfo_screenwidth()
                ScreenHeight = 1000#self.winfo_screenheight()
                x=(ScreenWidth/2) - (AppWidth/2)
                y=(ScreenHeight/2)- (AppHeight/2) #Put the App at center of Monitor
                #y=100
                popup.geometry('%dx%d+%d+%d' % (AppWidth, AppHeight, x, y))
                popup.title('Gait Cycle Selection')
                
                #print 'IC   OTO     OIC     TO  IC'
                TitleLabelText = 'Side' + ' \t' + 'IC' + ' \t' + 'OTO' + ' \t' + 'OIC' + ' \t' + 'TO' + ' \t' + 'IC'
                TitleLabel = tk.Label(popup, text=TitleLabelText,font=Small_Font, justify = 'left')
                TitleLabel.place(x=45,y=10)

                numCycleIndex = tk.IntVar()
                for numCycle in range(len(RightFootStrikeEventFrames)-1):
                    RightStrike1 = 0.
                    RightStrike2 = 0.
                    RightToeOff = 0.
                    RightOppositeToeOff = 0.
                    RightOppositeFootStrike = 0.
                    RightStrike1 = sorted(RightFootStrikeEventFrames)[numCycle]
                    RightStrike2 = sorted(RightFootStrikeEventFrames)[numCycle + 1]
                    for i in range(len(RightFootOffEventFrames)):
                        if RightFootOffEventFrames[i] > RightStrike1 and RightFootOffEventFrames[i] < RightStrike2:
                            RightToeOff = RightFootOffEventFrames[i]
                    for i in range(len(LeftFootOffEventFrames)):
                         if LeftFootOffEventFrames[i] > RightStrike1 and LeftFootOffEventFrames[i] < RightToeOff:
                            RightOppositeToeOff = LeftFootOffEventFrames[i]
                    for i in range(len(LeftFootStrikeEventFrames)):
                         if LeftFootStrikeEventFrames[i] > RightStrike1 and LeftFootStrikeEventFrames[i] < RightToeOff:
                            RightOppositeFootStrike = LeftFootStrikeEventFrames[i] 
                    # Change to blank if value not found
                    if RightToeOff == 0:
                        StringRightToeOff = '   '
                    else:
                        StringRightToeOff = str(RightToeOff)
                    if RightOppositeToeOff == 0:
                        StringRightOppositeToeOff = '   '
                    else:
                        StringRightOppositeToeOff = str(RightOppositeToeOff)
                    if RightOppositeFootStrike == 0:
                        StringRightOppositeFootStrike = '   '
                    else:
                        StringRightOppositeFootStrike = str(RightOppositeFootStrike)
                        
                    numCycleButtonText = 'Right' + ' \t' + str(RightStrike1) + ' \t' + StringRightOppositeToeOff + ' \t' + StringRightOppositeFootStrike + ' \t' + StringRightToeOff + ' \t' + str(RightStrike2) + '\n'
                    
                    numCycleButton = tk.Radiobutton(popup, text=numCycleButtonText, variable = numCycleIndex, value=numCycle, font=Small_Font, command= lambda: ReadCycleSelectionRight(), anchor = 'center',background='white') 
                    numCycleButton.place(x=10, y = 10 + (numCycle + 1)*35, height = 30, width = 400)                    
                    
                    if RightStrike1 == 0 or RightStrike2 == 0 or RightToeOff == 0 or RightOppositeToeOff == 0 or RightOppositeFootStrike == 0:
                        WarningLabel = tk.Label(popup,text="Missing Gait Events!!!", font=Small_Font,justify= 'center',foreground='red')
                        WarningLabel.place(x=420,y=10 + (numCycle + 1)*35, height = 30,)
                
                # Add Save PDF Button
                ProceedButton = tk.Button(popup, text="Proceed", command= lambda: [ReadCycleSelectionRight(), self.popup.destroy()], font=Small_Font, justify = 'center')#anchor = 'se')
                ProceedButton.place(x=10,y=200-60,width=600-100,height=50) 
                # Exit Button
                CancelButton = tk.Button(popup, text="Cancel", command=lambda: cancelRight(), font=Small_Font, justify = 'center')
                CancelButton.place(x=600-80,y=200-60,width = 70, height = 50)
                
                def cancelRight():
                    popup.destroy
                    sys.exit()
                    
                def ReadCycleSelectionRight():
                    global SelectedCycleIndex 
                    SelectedCycleIndex = numCycleIndex.get()
                    RightStrike1 = 0.
                    RightStrike2 = 0.
                    RightToeOff = 0.
                    RightOppositeToeOff = 0.
                    RightOppositeFootStrike = 0.
                    RightStrike1 = sorted(RightFootStrikeEventFrames)[SelectedCycleIndex ]
                    RightStrike2 = sorted(RightFootStrikeEventFrames)[SelectedCycleIndex  + 1]
                    for i in range(len(RightFootOffEventFrames)):
                        if RightFootOffEventFrames[i] > RightStrike1 and RightFootOffEventFrames[i] < RightStrike2:
                            RightToeOff = RightFootOffEventFrames[i]
                    for i in range(len(LeftFootOffEventFrames)):
                         if LeftFootOffEventFrames[i] > RightStrike1 and LeftFootOffEventFrames[i] < RightToeOff:
                            RightOppositeToeOff = LeftFootOffEventFrames[i]
                    for i in range(len(LeftFootStrikeEventFrames)):
                         if LeftFootStrikeEventFrames[i] > RightStrike1 and LeftFootStrikeEventFrames[i] < RightToeOff:
                            RightOppositeFootStrike = LeftFootStrikeEventFrames[i] 
                    if RightStrike1 == 0 or RightStrike2 == 0 or RightToeOff == 0 or RightOppositeToeOff == 0 or RightOppositeFootStrike == 0:
                        ProceedButton.place_forget()
                    else:
                        ProceedButton.place(x=10,y=200-60,width=600-100,height=50)
                        
                ReadCycleSelectionRight()
                popup.mainloop()
                
                RightStrike1 = sorted(RightFootStrikeEventFrames)[SelectedCycleIndex ]
                RightStrike2 = sorted(RightFootStrikeEventFrames)[SelectedCycleIndex  + 1]
                for i in range(len(RightFootOffEventFrames)):
                    if RightFootOffEventFrames[i] > RightStrike1 and RightFootOffEventFrames[i] < RightStrike2:
                        RightToeOff = RightFootOffEventFrames[i]
                for i in range(len(LeftFootOffEventFrames)):
                     if LeftFootOffEventFrames[i] > RightStrike1 and LeftFootOffEventFrames[i] < RightToeOff:
                        RightOppositeToeOff = LeftFootOffEventFrames[i]
                for i in range(len(LeftFootStrikeEventFrames)):
                     if LeftFootStrikeEventFrames[i] > RightStrike1 and LeftFootStrikeEventFrames[i] < RightToeOff:
                        RightOppositeFootStrike = LeftFootStrikeEventFrames[i] 
                
                
            if len(RightFootStrikeEventFrames) == 2:
                # Right Gait Cycle Found
                RightStrike1 = min(RightFootStrikeEventFrames[0],RightFootStrikeEventFrames[1])
                RightStrike2 = max(RightFootStrikeEventFrames[0],RightFootStrikeEventFrames[1])
                for i in range(len(RightFootOffEventFrames)):
                    if RightFootOffEventFrames[i] > RightStrike1 and RightFootOffEventFrames[i] < RightStrike2:
                        RightToeOff = RightFootOffEventFrames[i]
                for i in range(len(LeftFootOffEventFrames)):
                     if LeftFootOffEventFrames[i] > RightStrike1 and LeftFootOffEventFrames[i] < RightToeOff:
                        RightOppositeToeOff = LeftFootOffEventFrames[i]
                for i in range(len(LeftFootStrikeEventFrames)):
                     if LeftFootStrikeEventFrames[i] > RightStrike1 and LeftFootStrikeEventFrames[i] < RightToeOff:
                        RightOppositeFootStrike = LeftFootStrikeEventFrames[i]
                if RightOppositeFootStrike == 0 or RightOppositeToeOff == 0:
                    popup = tk.Tk()
                    popup.resizable(0,0)
                    AppWidth = 400
                    AppHeight= 50
                    ScreenWidth = 1600#self.winfo_screenwidth()
                    ScreenHeight = 1000#self.winfo_screenheight()
                    x=(ScreenWidth/2) - (AppWidth/2)
                    y=(ScreenHeight/2)- (AppHeight/2) #Put the App at center of Monitor
                    popup.geometry('%dx%d+%d+%d' % (AppWidth, AppHeight, x, y))
                    popup.title('Warning')
                    WarningMessage = tk.Label(popup,text="Right Side: Missing Gait Events!!! \n Add events and Rerun CreateGCD pipeline", font=Small_Font,justify= 'center',foreground='red')
                    WarningMessage.pack()
                    popup.mainloop()
            
            #print str(RightStrike1) + ' \t' + str(RightOppositeToeOff) + ' \t' + str(RightOppositeFootStrike) + ' \t' + str(RightToeOff) + ' \t' + str(RightStrike2) + '\n'
            # Compute Stride Temporal Parameters
            RightAnkleMarker_Strike1 = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.RightLateralAnkleMarkerName, RightStrike1)[0:3])
            RightAnkleMarker_Strike2 = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.RightLateralAnkleMarkerName, RightStrike2)[0:3])
            LeftAnkleMarker_OppositeFootContact = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.LeftLateralAnkleMarkerName, RightOppositeFootStrike)[0:3])
            LeftAnkleMarker_OppositeToeOff = np.array(vicon.GetTrajectoryAtFrame(SubjectName, self.LeftLateralAnkleMarkerName, RightOppositeToeOff)[0:3])
            RightStrideLength = np.linalg.norm(RightAnkleMarker_Strike2 - RightAnkleMarker_Strike1) # mm
            RightStrideLength_CM = RightStrideLength/10 # cm
            RightStepLength = np.linalg.norm(RightAnkleMarker_Strike2 - LeftAnkleMarker_OppositeFootContact) # mm
            RightStepLength_CM = RightStepLength/10 # cm
            RightStrideTime = (RightStrike2 - RightStrike1) / MarkerFrameRate # Seconds
            RightStepTime = (RightStrike2 - RightToeOff) / MarkerFrameRate # Seconds
            RightCadence_StepsPerMin = (1/RightStrideTime) * 2 * 60 # Steps/min
            RightCadence = (1/RightStrideTime) # /sec
            RightSpeed = RightStrideLength / RightStrideTime # mm/sec
            RightSpeed_CMPerSec = RightStrideLength / (RightStrideTime * 10) # cm/sec
            
            RightFootOff=100*(float(RightToeOff)-float(RightStrike1))/(float(RightStrike2)-float(RightStrike1))
            RightOppositeFootOff=100*(float(RightOppositeToeOff)-float(RightStrike1))/(float(RightStrike2)-float(RightStrike1))
            RightOppositeFootContact=100*(float(RightOppositeFootStrike)-float(RightStrike1))/(float(RightStrike2)-float(RightStrike1))
            RightStance = RightFootOff
            RightDoubleSupport1 = 100*(float(RightOppositeToeOff)-float(RightStrike1))/(float(RightStrike2)-float(RightStrike1))
            RightSingleSupport  = 100*(float(RightOppositeFootStrike)-float(RightOppositeToeOff))/(float(RightStrike2)-float(RightStrike1))
            RightDoubleSupport2 = 100*(float(RightToeOff)-float(RightOppositeFootStrike))/(float(RightStrike2)-float(RightStrike1))
            RightSwing = 100*(float(RightStrike2)-float(RightToeOff))/(float(RightStrike2)-float(RightStrike1))
            RightDoubleSupport  = RightDoubleSupport1 + RightDoubleSupport2
            
            # Compute GCD Variables
            [RightTrunkTilt,RightTrunkObliquity,RightTrunkRotation]     = ComputeGCDVariable('RTrunkAngles' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightPelvicTilt,RightPelvicObliquity,RightPelvicRotation]  = ComputeGCDVariable('RPelvisAngles', NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightHipFlexExt,RightHipAbAdduct,RightHipRotation]         = ComputeGCDVariable('RHipAngles'   , NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightKneeFlexExt,RightKneeValgVar,RightKneeRotation]       = ComputeGCDVariable('RKneeAngles'  , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,DummyY,RightKneeRotation_Proximal]      = ComputeGCDVariable('RKneeAnglesProximal'  , NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightDorsiPlanFlex,DummyY,RightFootRotation]               = ComputeGCDVariable('RAnkleAngles' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightFootSagittalInclination,DummyY,RightFootProgression]          = ComputeGCDVariable('RFootProgressAngles'  , NumPointsPerGraph, RightStrike1, RightStrike2)
            # Compute Pelvis, Knee and Ankle Progression GCD Variables
            [RightFemurSagittalInclination,DummyY,RightFemurProgression]        = ComputeGCDVariable('RThighAngles'  , NumPointsPerGraph, RightStrike1, RightStrike2)
            [RightTibiaSagittalInclination,DummyY,RightTibiaProgression]        = ComputeGCDVariable('RShankAngles'  , NumPointsPerGraph, RightStrike1, RightStrike2)
            
            # Muscle Length 
            [DummyX,RightGluteusMaxLength,DummyZ]    = ComputeGCDVariable('GluteusMaxLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightIlioPsoasLength,DummyZ]    = ComputeGCDVariable('IlioPsoasLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightRectFemLength,DummyZ]    = ComputeGCDVariable('RectFemLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightMedHamstringLength,DummyZ]    = ComputeGCDVariable('MedHamstringLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightLatHamstringLength,DummyZ]    = ComputeGCDVariable('LatHamstringLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightGastrocLength,DummyZ]    = ComputeGCDVariable('GastrocLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightSoleusLength,DummyZ]    = ComputeGCDVariable('SoleusLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightTibPostLength,DummyZ]    = ComputeGCDVariable('TibPostLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightPeronealLength,DummyZ]    = ComputeGCDVariable('PeronealLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightVastusLatLength,DummyZ]    = ComputeGCDVariable('VastusLatLength' , NumPointsPerGraph, RightStrike1, RightStrike2)
            # Muscle Velocity 
            [DummyX,RightGluteusMaxVelocity,DummyZ]    = ComputeGCDVariable('GluteusMaxVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightIlioPsoasVelocity,DummyZ]    = ComputeGCDVariable('IlioPsoasVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightRectFemVelocity,DummyZ]    = ComputeGCDVariable('RectFemVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightMedHamstringVelocity,DummyZ]    = ComputeGCDVariable('MedHamstringVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightLatHamstringVelocity,DummyZ]    = ComputeGCDVariable('LatHamstringVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightGastrocVelocity,DummyZ]    = ComputeGCDVariable('GastrocVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightSoleusVelocity,DummyZ]    = ComputeGCDVariable('SoleusVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightTibPostVelocity,DummyZ]    = ComputeGCDVariable('TibPostVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightPeronealVelocity,DummyZ]    = ComputeGCDVariable('PeronealVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            [DummyX,RightVastusLatVelocity,DummyZ]    = ComputeGCDVariable('VastusLatVelocity' , NumPointsPerGraph, RightStrike1, RightStrike2)
            
            # Check if Kinetics Data exist
            if 'RAnklePowerComponents' in ModelOutputs:
                [RightHipFlexExtMoment,RightHipAbAdductMoment,RightHipRotationMoment]      = ComputeGCDVariable('RHipMoment'   , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightKneeFlexExtMoment,RightKneeValgVarMoment,RightKneeRotationMoment]    = ComputeGCDVariable('RKneeMoment'  , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightDorsiPlanFlexMoment,RightFootAbAdductMoment,RightFootRotationMoment] = ComputeGCDVariable('RAnkleMoment' , NumPointsPerGraph, RightStrike1, RightStrike2)
                
                [RightHipFlexExtPower,RightHipAbAdductPower,RightHipRotationPower]         = ComputeGCDVariable('RHipPowerComponents'    , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightKneeFlexExtPower,RightKneeValgVarPower,RightKneeRotationPower]       = ComputeGCDVariable('RKneePowerComponents'   , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightDorsiPlanFlexPower,RightFootAbAdductPower,RightFootRotationPower]    = ComputeGCDVariable('RAnklePowerComponents'  , NumPointsPerGraph, RightStrike1, RightStrike2)
             
                [DummyX,DummyY,RightHipPowerTotal]         = ComputeGCDVariable('RHipPower'    , NumPointsPerGraph, RightStrike1, RightStrike2)
                [DummyX,DummyY,RightKneePowerTotal]       = ComputeGCDVariable('RKneePower'   , NumPointsPerGraph, RightStrike1, RightStrike2)
                [DummyX,DummyY,RightAnklePowerTotal]    = ComputeGCDVariable('RAnklePower'  , NumPointsPerGraph, RightStrike1, RightStrike2)
                
                # Check for Force Plate Hits
                RightForcePlate_DeviceID = 0 #Default Value if Force Plate Hit is not Found
                DeviceIDs = vicon.GetDeviceIDs()
                for DeviceID in DeviceIDs:
                    [name, type, rate, deviceOutputIDs, forceplate, eyetracker] = vicon.GetDeviceDetails(DeviceID)
                    if forceplate.Context == 'Right':
                        RightForcePlate_DeviceID = DeviceID
                        RightForcePlate = forceplate
                [RightGRFx, RightGRFy, RightGRFz, RightGRTz, RightCOPx, RightCOPy] = ComputeGCDVariableFP_Component(RightForcePlate,RightForcePlate_DeviceID,NumPointsPerGraph,RightStrike1,RightStrike2)
                
                RightAnkleVector_Strike1_To_Strike2 = RightAnkleMarker_Strike2 - RightAnkleMarker_Strike1
                if abs(RightAnkleVector_Strike1_To_Strike2[0]) > abs(RightAnkleVector_Strike1_To_Strike2[1]):
                    if RightAnkleVector_Strike1_To_Strike2[0] > 0: 
                        # Walking Direction +X
                        RightGRF_Anterior   = RightGRFx
                        RightGRF_Medial     = RightGRFy
                        RightGRF_Vertical   = RightGRFz
                        RightGRT_Vertical   = RightGRTz
                    else: 
                        # Walking Direction -X
                        RightGRF_Anterior   = -RightGRFx
                        RightGRF_Medial     = -RightGRFy
                        RightGRF_Vertical   = RightGRFz
                        RightGRT_Vertical   = RightGRTz
                else:
                    if RightAnkleVector_Strike1_To_Strike2[1] > 0: 
                        # Walking Direction +Y
                        RightGRF_Anterior   = RightGRFy
                        RightGRF_Medial     = -RightGRFx
                        RightGRF_Vertical   = RightGRFz
                        RightGRT_Vertical   = RightGRTz
                    else:
                        # Walking Direction -Y
                        RightGRF_Anterior   = -RightGRFy
                        RightGRF_Medial     = RightGRFx
                        RightGRF_Vertical   = RightGRFz
                        RightGRT_Vertical   = RightGRTz
             
            # Check if EMG Data exist
            EMG_DigitalDeviceID = 0
            EMG_AnalogDeviceID = 0
            EMG_DigitalDeviceOutputIDs = 0
            EMG_AnalogDeviceOutputIDs = 0
            EMG_Digital = False
            EMG_Analog = False
            DeviceIDs = vicon.GetDeviceIDs()
            try:
                for DeviceID in DeviceIDs:
                    [Device_name, Device_type, Device_rate, Device_deviceOutputIDs, Device_forceplate, Device_eyetracker] = vicon.GetDeviceDetails(DeviceID)
                    if Device_type == 'Other':
                        name, output_type, unit, ready, channelNames, channelIDs = vicon.GetDeviceOutputDetails(DeviceID, Device_deviceOutputIDs[0])
                        if 'Potential' not in output_type: # Skip instrumented device such as Walker, Transducer
                            if 'Digital' in output_type: # Noraxon
                                EMG_Digital = True
                                EMG_DigitalDeviceID = DeviceID
                                EMG_DigitalDeviceOutputIDs = Device_deviceOutputIDs
                            else:
                                if 'volt' in unit: # MLS or Delsys
                                    if len(channelNames) > 1: # MLS / Analog
                                        EMG_Analog = True
                                        EMG_AnalogDeviceID = DeviceID
                                        EMG_AnalogDeviceOutputIDs = Device_deviceOutputIDs
                                    else:
                                       if 'IM' in channelNames[0]: # Delsys
                                           EMG_Digital = True
                                           EMG_DigitalDeviceID = DeviceID
                                           EMG_DigitalDeviceOutputIDs = Device_deviceOutputIDs
            except:
                pass
                           
            if EMG_DigitalDeviceID != 0 or EMG_AnalogDeviceID != 0:
                RightRectusFemorisEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightRectusFemorisEMGName,     NumPointsPerGraph,RightStrike1,RightStrike2)
                RightVasltusLateralisEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightVasltusLateralisEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                RightMedialHamstringsEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightMedialHamstringsEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                RightGastrocnemiusEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightGastrocnemiusEMGName,     NumPointsPerGraph,RightStrike1,RightStrike2)
                RightTibialisAnteriorEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightTibialisAnteriorEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                # Lexington
                try:
                    RightGluteusMaximusEMG   = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightGluteusMaximusEMGName,    NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
                try:
                    RightGluteusMediusEMG    = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightGluteusMediusEMGName,     NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
                try:
                    RightAdductorsEMG        = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightAdductorsEMGName,         NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
                # Montreal
                try:
                    RightVasltusMedialisEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightVasltusMedialisEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
                try:
                    RightLateralHamstringsEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightLateralHamstringsEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
                try:
                    RightPeroneusLongusEMG = ComputeGCDVariableEMG(EMG_Digital,EMG_Analog,EMG_DigitalDeviceID,EMG_AnalogDeviceID,EMG_DigitalDeviceOutputIDs,EMG_AnalogDeviceOutputIDs,self.RightPeroneusLongusEMGName,  NumPointsPerGraph,RightStrike1,RightStrike2)
                except:
                    pass
            
            # Check if Foot Model data exists
            if self.valueRightFootModelCheck == '1':
                [RightHindFootTilt,RightHindFootObliquity,RightHindFootRotation]                    = ComputeGCDVariable('RHFGA' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightForeFootTilt,RightForeFootObliquity,RightForeFootRotation]                    = ComputeGCDVariable('RFFGA' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightAnkleComplexDorsiPlanFlex,RightAnkleComplexValgVar,RightAnkleComplexRotation] = ComputeGCDVariable('RANKA' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightMidFootDorsiPlanFlex,RightMidFootSupPron,RightMidFootAbAdduct]                = ComputeGCDVariable('RMDFA' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [RightToeFlexExt,DummyY,RightToeValgVar]                                            = ComputeGCDVariable('RHLXA' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [DummyX,RightSupination,DummyZ]                                                     = ComputeGCDVariable('Supination' , NumPointsPerGraph, RightStrike1, RightStrike2)
                [DummyX,RightSkew,DummyZ]                                                           = ComputeGCDVariable('Skew'  , NumPointsPerGraph, RightStrike1, RightStrike2)
                
        
        # Write Temporal Variables in GCD File
        if len(LeftFootStrikeEventFrames) >= 2:
            WriteSingleValueToGCD(GCDFile,'LeftStrideLength',LeftStrideLength)
            WriteSingleValueToGCD(GCDFile,'LeftStrideLength_CM',LeftStrideLength_CM)
            WriteSingleValueToGCD(GCDFile,'LeftStepLength',LeftStepLength)
            WriteSingleValueToGCD(GCDFile,'LeftStepLength_CM',LeftStepLength_CM)
            WriteSingleValueToGCD(GCDFile,'LeftStrideTime',LeftStrideTime)
            WriteSingleValueToGCD(GCDFile,'LeftStepTime',LeftStepTime)
            WriteSingleValueToGCD(GCDFile,'LeftCadence',LeftCadence)
            WriteSingleValueToGCD(GCDFile,'LeftCadence_StepsPerMin',LeftCadence_StepsPerMin)           
            WriteSingleValueToGCD(GCDFile,'LeftSpeed',LeftSpeed)
            WriteSingleValueToGCD(GCDFile,'LeftSpeed_CMPerSec',LeftSpeed_CMPerSec)
            
            WriteSingleValueToGCD(GCDFile,'LeftFootOff',LeftFootOff)
            WriteSingleValueToGCD(GCDFile,'LeftOppositeFootOff',LeftOppositeFootOff)
            WriteSingleValueToGCD(GCDFile,'LeftOppositeFootContact',LeftOppositeFootContact)
            WriteSingleValueToGCD(GCDFile,'LeftStance',LeftStance)
            WriteSingleValueToGCD(GCDFile,'LeftDoubleSupport1',LeftDoubleSupport1)
            WriteSingleValueToGCD(GCDFile,'LeftSingleSupport',LeftSingleSupport)
            WriteSingleValueToGCD(GCDFile,'LeftDoubleSupport2',LeftDoubleSupport2)
            WriteSingleValueToGCD(GCDFile,'LeftSwing',LeftSwing)
            WriteSingleValueToGCD(GCDFile,'LeftDoubleSupport',LeftDoubleSupport)
            
            
        if len(RightFootStrikeEventFrames) >= 2:     
            WriteSingleValueToGCD(GCDFile,'RightStrideLength',RightStrideLength)
            WriteSingleValueToGCD(GCDFile,'RightStrideLength_CM',RightStrideLength_CM)
            WriteSingleValueToGCD(GCDFile,'RightStepLength',RightStepLength)
            WriteSingleValueToGCD(GCDFile,'RightStepLength_CM',RightStepLength_CM)
            WriteSingleValueToGCD(GCDFile,'RightStrideTime',RightStrideTime)
            WriteSingleValueToGCD(GCDFile,'RightStepTime',RightStepTime)
            WriteSingleValueToGCD(GCDFile,'RightCadence',RightCadence)
            WriteSingleValueToGCD(GCDFile,'RightCadence_StepsPerMin',RightCadence_StepsPerMin)
            WriteSingleValueToGCD(GCDFile,'RightSpeed',RightSpeed)
            WriteSingleValueToGCD(GCDFile,'RightSpeed_CMPerSec',RightSpeed_CMPerSec)
            
            WriteSingleValueToGCD(GCDFile,'RightFootOff',RightFootOff)
            WriteSingleValueToGCD(GCDFile,'RightOppositeFootOff',RightOppositeFootOff)
            WriteSingleValueToGCD(GCDFile,'RightOppositeFootContact',RightOppositeFootContact)
            WriteSingleValueToGCD(GCDFile,'RightStance',RightStance)
            WriteSingleValueToGCD(GCDFile,'RightDoubleSupport1',RightDoubleSupport1)
            WriteSingleValueToGCD(GCDFile,'RightSingleSupport',RightSingleSupport)
            WriteSingleValueToGCD(GCDFile,'RightDoubleSupport2',RightDoubleSupport2)
            WriteSingleValueToGCD(GCDFile,'RightSwing',RightSwing)
            WriteSingleValueToGCD(GCDFile,'RightDoubleSupport',RightDoubleSupport)
            
        # Write Angles in GCD File
        if len(LeftFootStrikeEventFrames) >= 2:
            WriteArrayToGCD(GCDFile,'LeftTrunkObliquity',LeftTrunkObliquity)
            WriteArrayToGCD(GCDFile,'LeftTrunkTilt',LeftTrunkTilt)
            WriteArrayToGCD(GCDFile,'LeftTrunkRotation',LeftTrunkRotation)
            WriteArrayToGCD(GCDFile,'LeftPelvicObliquity',LeftPelvicObliquity)
            WriteArrayToGCD(GCDFile,'LeftPelvicTilt',LeftPelvicTilt)
            WriteArrayToGCD(GCDFile,'LeftPelvicRotation',LeftPelvicRotation)
            WriteArrayToGCD(GCDFile,'LeftHipAbAdduct',LeftHipAbAdduct)
            WriteArrayToGCD(GCDFile,'LeftHipFlexExt',LeftHipFlexExt)
            WriteArrayToGCD(GCDFile,'LeftHipRotation',LeftHipRotation)
            WriteArrayToGCD(GCDFile,'LeftKneeValgVar',LeftKneeValgVar)
            WriteArrayToGCD(GCDFile,'LeftKneeFlexExt',LeftKneeFlexExt)
            WriteArrayToGCD(GCDFile,'LeftKneeRotation',LeftKneeRotation)
            WriteArrayToGCD(GCDFile,'LeftKneeRotation_Proximal',LeftKneeRotation_Proximal)
            WriteArrayToGCD(GCDFile,'LeftDorsiPlanFlex',LeftDorsiPlanFlex)
            WriteArrayToGCD(GCDFile,'LeftFootRotation',LeftFootRotation)
            WriteArrayToGCD(GCDFile,'LeftFootProgression',LeftFootProgression)
            # Progression Angles generated for MAPS Compatability
            WriteArrayToGCD(GCDFile,'LeftPelvicProgressAngle',LeftPelvicRotation)
            WriteArrayToGCD(GCDFile,'LeftKneeProgressAngle',LeftFemurProgression)
            WriteArrayToGCD(GCDFile,'LeftAnkleProgressAngle',LeftTibiaProgression)
            # Thigh and Shank Progression as Standard Output Name
            WriteArrayToGCD(GCDFile,'LeftFemurRotation',LeftFemurProgression)
            WriteArrayToGCD(GCDFile,'LeftTibiaRotation',LeftTibiaProgression)
            # Thigh, Shank, and Foot Inclination Angles
            WriteArrayToGCD(GCDFile,'LeftFemurSagittalInclination',LeftFemurSagittalInclination)
            WriteArrayToGCD(GCDFile,'LeftTibiaSagittalInclination',LeftTibiaSagittalInclination)
            WriteArrayToGCD(GCDFile,'LeftFootSagittalInclination',LeftFootSagittalInclination)
            
            
            # Muscle Length
            WriteArrayToGCD(GCDFile,'LeftGluteusMaxLength',LeftGluteusMaxLength)
            WriteArrayToGCD(GCDFile,'LeftIlioPsoasLength',LeftIlioPsoasLength)
            WriteArrayToGCD(GCDFile,'LeftRectFemLength',LeftRectFemLength)
            WriteArrayToGCD(GCDFile,'LeftMedHamstringLength',LeftMedHamstringLength)
            WriteArrayToGCD(GCDFile,'LeftLatHamstringLength',LeftLatHamstringLength)
            WriteArrayToGCD(GCDFile,'LeftGastrocLength',LeftGastrocLength)
            WriteArrayToGCD(GCDFile,'LeftSoleusLength',LeftSoleusLength)
            WriteArrayToGCD(GCDFile,'LeftTibPostLength',LeftTibPostLength)
            WriteArrayToGCD(GCDFile,'LeftPeronealLength',LeftPeronealLength)
            WriteArrayToGCD(GCDFile,'LeftVastLatLength',LeftVastusLatLength)
            # Muscle Velocity
            WriteArrayToGCD(GCDFile,'LeftGluteusMaxVelocity',LeftGluteusMaxVelocity)
            WriteArrayToGCD(GCDFile,'LeftIlioPsoasVelocity',LeftIlioPsoasVelocity)
            WriteArrayToGCD(GCDFile,'LeftRectFemVelocity',LeftRectFemVelocity)
            WriteArrayToGCD(GCDFile,'LeftMedHamstringVelocity',LeftMedHamstringVelocity)
            WriteArrayToGCD(GCDFile,'LeftLatHamstringVelocity',LeftLatHamstringVelocity)
            WriteArrayToGCD(GCDFile,'LeftGastrocVelocity',LeftGastrocVelocity)
            WriteArrayToGCD(GCDFile,'LeftSoleusVelocity',LeftSoleusVelocity)
            WriteArrayToGCD(GCDFile,'LeftTibPostVelocity',LeftTibPostVelocity)
            WriteArrayToGCD(GCDFile,'LeftPeronealVelocity',LeftPeronealVelocity)
            WriteArrayToGCD(GCDFile,'LeftVastLatVelocity',LeftVastusLatVelocity)
            
            
            
            # Check if Kinetics Data exist
            if 'LAnklePowerComponents' in ModelOutputs:
                WriteArrayToGCD(GCDFile,'LeftHipFlexExtMoment',LeftHipFlexExtMoment)
                WriteArrayToGCD(GCDFile,'LeftHipAbAdductMoment',LeftHipAbAdductMoment)
                WriteArrayToGCD(GCDFile,'LeftHipRotationMoment',LeftHipRotationMoment)
                WriteArrayToGCD(GCDFile,'LeftKneeFlexExtMoment',LeftKneeFlexExtMoment)
                WriteArrayToGCD(GCDFile,'LeftKneeValgVarMoment',LeftKneeValgVarMoment)
                WriteArrayToGCD(GCDFile,'LeftKneeRotationMoment',LeftKneeRotationMoment)
                WriteArrayToGCD(GCDFile,'LeftDorsiPlanFlexMoment',LeftDorsiPlanFlexMoment)
                WriteArrayToGCD(GCDFile,'LeftFootAbAdductMoment',LeftFootAbAdductMoment)
                WriteArrayToGCD(GCDFile,'LeftFootRotationMoment',LeftFootRotationMoment)
                
                WriteArrayToGCD(GCDFile,'LeftHipPower',LeftHipPowerTotal)
                WriteArrayToGCD(GCDFile,'LeftHipFlexExtPower',LeftHipFlexExtPower)
                WriteArrayToGCD(GCDFile,'LeftHipAbAdductPower',LeftHipAbAdductPower)
                WriteArrayToGCD(GCDFile,'LeftHipRotationPower',LeftHipRotationPower)
                WriteArrayToGCD(GCDFile,'LeftKneePower',LeftKneePowerTotal)
                WriteArrayToGCD(GCDFile,'LeftKneeFlexExtPower',LeftKneeFlexExtPower)
                WriteArrayToGCD(GCDFile,'LeftKneeValgVarPower',LeftKneeValgVarPower)
                WriteArrayToGCD(GCDFile,'LeftKneeRotationPower',LeftKneeRotationPower)
                WriteArrayToGCD(GCDFile,'LeftAnklePower',LeftAnklePowerTotal)
                WriteArrayToGCD(GCDFile,'LeftDorsiPlanFlexPower',LeftDorsiPlanFlexPower)
                WriteArrayToGCD(GCDFile,'LeftFootAbAdductPower',LeftFootAbAdductPower)
                WriteArrayToGCD(GCDFile,'LeftFootRotationPower',LeftFootRotationPower)
                
                WriteArrayToGCD(GCDFile,'LeftGRF_Anterior',LeftGRF_Anterior)
                WriteArrayToGCD(GCDFile,'LeftGRF_Medial',LeftGRF_Medial)
                WriteArrayToGCD(GCDFile,'LeftGRF_Vertical',LeftGRF_Vertical)
                WriteArrayToGCD(GCDFile,'LeftGRT_Vertical',LeftGRT_Vertical)
                
                WriteArrayToGCD(GCDFile,'LeftCOPx',LeftCOPx)
                WriteArrayToGCD(GCDFile,'LeftCOPy',LeftCOPy)
                
            
            # Check if EMG Data Exists
            if EMG_DigitalDeviceID != 0 or EMG_AnalogDeviceID != 0:         
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLRectFem',LeftRectusFemorisEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLVastLat',LeftVasltusLateralisEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLMedHams',LeftMedialHamstringsEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLGasTroc',LeftGastrocnemiusEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLTibAnte',LeftTibialisAnteriorEMG, 80)
                # Lexington
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLGlutMax',LeftGluteusMaximusEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLGlutMed',LeftGluteusMediusEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLAdducto',LeftAdductorsEMG, 80)
                except:
                    pass
                # Montreal
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLVastMed',LeftVasltusMedialisEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLLatHams',LeftLateralHamstringsEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'LeftRawLPerLong',LeftPeroneusLongusEMG, 80)  
                except:
                    pass
                
            # Check if Foot Model data exists
            if self.valueLeftFootModelCheck == '1':
                WriteArrayToGCD(GCDFile,'LeftHindFootTilt',LeftHindFootTilt)
                WriteArrayToGCD(GCDFile,'LeftHindFootObliquity',LeftHindFootObliquity)
                WriteArrayToGCD(GCDFile,'LeftHindFootRotation',LeftHindFootRotation)
                WriteArrayToGCD(GCDFile,'LeftForeFootTilt',LeftForeFootTilt)
                WriteArrayToGCD(GCDFile,'LeftForeFootRotation',LeftForeFootRotation)
                WriteArrayToGCD(GCDFile,'LeftAnkleComplexDorsiPlanFlex',LeftAnkleComplexDorsiPlanFlex)
                WriteArrayToGCD(GCDFile,'LeftAnkleComplexValgVar',LeftAnkleComplexValgVar)
                WriteArrayToGCD(GCDFile,'LeftAnkleComplexRotation',LeftAnkleComplexRotation)
                WriteArrayToGCD(GCDFile,'LeftMidFootDorsiPlanFlex',LeftMidFootDorsiPlanFlex)
                WriteArrayToGCD(GCDFile,'LeftMidFootSupPron',LeftMidFootSupPron)
                WriteArrayToGCD(GCDFile,'LeftMidFootAbAdduct',LeftMidFootAbAdduct)
                WriteArrayToGCD(GCDFile,'LeftHalDorsiPlanFlex',LeftToeFlexExt)
                WriteArrayToGCD(GCDFile,'LeftHalValgVar',LeftToeValgVar)
                WriteArrayToGCD(GCDFile,'LeftSupination',LeftSupination)
                WriteArrayToGCD(GCDFile,'LeftSkew',LeftSkew)
                
                
            
        if len(RightFootStrikeEventFrames) >= 2:       
            WriteArrayToGCD(GCDFile,'RightTrunkObliquity',RightTrunkObliquity)
            WriteArrayToGCD(GCDFile,'RightTrunkTilt',RightTrunkTilt)
            WriteArrayToGCD(GCDFile,'RightTrunkRotation',RightTrunkRotation)
            WriteArrayToGCD(GCDFile,'RightPelvicObliquity',RightPelvicObliquity)
            WriteArrayToGCD(GCDFile,'RightPelvicTilt',RightPelvicTilt)
            WriteArrayToGCD(GCDFile,'RightPelvicRotation',RightPelvicRotation)
            WriteArrayToGCD(GCDFile,'RightHipAbAdduct',RightHipAbAdduct)
            WriteArrayToGCD(GCDFile,'RightHipFlexExt',RightHipFlexExt)
            WriteArrayToGCD(GCDFile,'RightHipRotation',RightHipRotation)
            WriteArrayToGCD(GCDFile,'RightKneeValgVar',RightKneeValgVar)
            WriteArrayToGCD(GCDFile,'RightKneeFlexExt',RightKneeFlexExt)
            WriteArrayToGCD(GCDFile,'RightKneeRotation',RightKneeRotation)
            WriteArrayToGCD(GCDFile,'RightKneeRotation_Proximal',RightKneeRotation_Proximal)
            WriteArrayToGCD(GCDFile,'RightDorsiPlanFlex',RightDorsiPlanFlex)
            WriteArrayToGCD(GCDFile,'RightFootRotation',RightFootRotation)
            WriteArrayToGCD(GCDFile,'RightFootProgression',RightFootProgression)
            # Progression Angles generated for MAPS Compatability
            WriteArrayToGCD(GCDFile,'RightPelvicProgressAngle',RightPelvicRotation)
            WriteArrayToGCD(GCDFile,'RightKneeProgressAngle',RightFemurProgression)
            WriteArrayToGCD(GCDFile,'RightAnkleProgressAngle',RightTibiaProgression)
            # Thigh and Shank Progression as Standard Output Name
            WriteArrayToGCD(GCDFile,'RightFemurRotation',RightFemurProgression)
            WriteArrayToGCD(GCDFile,'RightTibiaRotation',RightTibiaProgression)
            # Thigh, Shank, and Foot Inclination Angles
            WriteArrayToGCD(GCDFile,'RightFemurSagittalInclination',RightFemurSagittalInclination)
            WriteArrayToGCD(GCDFile,'RightTibiaSagittalInclination',RightTibiaSagittalInclination)
            WriteArrayToGCD(GCDFile,'RightFootSagittalInclination',RightFootSagittalInclination)
            
            
            # Muscle Length
            WriteArrayToGCD(GCDFile,'RightGluteusMaxLength',RightGluteusMaxLength)
            WriteArrayToGCD(GCDFile,'RightIlioPsoasLength',RightIlioPsoasLength)
            WriteArrayToGCD(GCDFile,'RightRectFemLength',RightRectFemLength)
            WriteArrayToGCD(GCDFile,'RightMedHamstringLength',RightMedHamstringLength)
            WriteArrayToGCD(GCDFile,'RightLatHamstringLength',RightLatHamstringLength)
            WriteArrayToGCD(GCDFile,'RightGastrocLength',RightGastrocLength)
            WriteArrayToGCD(GCDFile,'RightSoleusLength',RightSoleusLength)
            WriteArrayToGCD(GCDFile,'RightTibPostLength',RightTibPostLength)
            WriteArrayToGCD(GCDFile,'RightPeronealLength',RightPeronealLength)
            WriteArrayToGCD(GCDFile,'RightVastLatLength',RightVastusLatLength)
            # Muscle Velocity
            WriteArrayToGCD(GCDFile,'RightGluteusMaxVelocity',RightGluteusMaxVelocity)
            WriteArrayToGCD(GCDFile,'RightIlioPsoasVelocity',RightIlioPsoasVelocity)
            WriteArrayToGCD(GCDFile,'RightRectFemVelocity',RightRectFemVelocity)
            WriteArrayToGCD(GCDFile,'RightMedHamstringVelocity',RightMedHamstringVelocity)
            WriteArrayToGCD(GCDFile,'RightLatHamstringVelocity',RightLatHamstringVelocity)
            WriteArrayToGCD(GCDFile,'RightGastrocVelocity',RightGastrocVelocity)
            WriteArrayToGCD(GCDFile,'RightSoleusVelocity',RightSoleusVelocity)
            WriteArrayToGCD(GCDFile,'RightTibPostVelocity',RightTibPostVelocity)
            WriteArrayToGCD(GCDFile,'RightPeronealVelocity',RightPeronealVelocity)
            WriteArrayToGCD(GCDFile,'RightVastLatVelocity',RightVastusLatVelocity)
            
            # Check if Kinetics Data exist
            if 'RAnklePowerComponents' in ModelOutputs:
                WriteArrayToGCD(GCDFile,'RightHipFlexExtMoment',RightHipFlexExtMoment)
                WriteArrayToGCD(GCDFile,'RightHipAbAdductMoment',RightHipAbAdductMoment)
                WriteArrayToGCD(GCDFile,'RightHipRotationMoment',RightHipRotationMoment)
                WriteArrayToGCD(GCDFile,'RightKneeFlexExtMoment',RightKneeFlexExtMoment)
                WriteArrayToGCD(GCDFile,'RightKneeValgVarMoment',RightKneeValgVarMoment)
                WriteArrayToGCD(GCDFile,'RightKneeRotationMoment',RightKneeRotationMoment)
                WriteArrayToGCD(GCDFile,'RightDorsiPlanFlexMoment',RightDorsiPlanFlexMoment)
                WriteArrayToGCD(GCDFile,'RightFootAbAdductMoment',RightFootAbAdductMoment)
                WriteArrayToGCD(GCDFile,'RightFootRotationMoment',RightFootRotationMoment)
                
                WriteArrayToGCD(GCDFile,'RightHipPower',RightHipPowerTotal)
                WriteArrayToGCD(GCDFile,'RightHipFlexExtPower',RightHipFlexExtPower)
                WriteArrayToGCD(GCDFile,'RightHipAbAdductPower',RightHipAbAdductPower)
                WriteArrayToGCD(GCDFile,'RightHipRotationPower',RightHipRotationPower)
                WriteArrayToGCD(GCDFile,'RightKneePower',RightKneePowerTotal)
                WriteArrayToGCD(GCDFile,'RightKneeFlexExtPower',RightKneeFlexExtPower)
                WriteArrayToGCD(GCDFile,'RightKneeValgVarPower',RightKneeValgVarPower)
                WriteArrayToGCD(GCDFile,'RightKneeRotationPower',RightKneeRotationPower)
                WriteArrayToGCD(GCDFile,'RightAnklePower',RightAnklePowerTotal)
                WriteArrayToGCD(GCDFile,'RightDorsiPlanFlexPower',RightDorsiPlanFlexPower)
                WriteArrayToGCD(GCDFile,'RightFootAbAdductPower',RightFootAbAdductPower)
                WriteArrayToGCD(GCDFile,'RightFootRotationPower',RightFootRotationPower)
                
                WriteArrayToGCD(GCDFile,'RightGRF_Anterior',RightGRF_Anterior)
                WriteArrayToGCD(GCDFile,'RightGRF_Medial',RightGRF_Medial)
                WriteArrayToGCD(GCDFile,'RightGRF_Vertical',RightGRF_Vertical)
                WriteArrayToGCD(GCDFile,'RightGRT_Vertical',RightGRT_Vertical)
                
                WriteArrayToGCD(GCDFile,'RightCOPx',RightCOPx)
                WriteArrayToGCD(GCDFile,'RightCOPy',RightCOPy)
                

            # Check if EMG Data Exists                  
            if EMG_DigitalDeviceID != 0 or EMG_AnalogDeviceID != 0:   
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRRectFem',RightRectusFemorisEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRVastLat',RightVasltusLateralisEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRMedHams',RightMedialHamstringsEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRGasTroc',RightGastrocnemiusEMG, 80)
                WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRTibAnte',RightTibialisAnteriorEMG, 80)
                # Lexington
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRGlutMax',RightGluteusMaximusEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRGlutMed',RightGluteusMediusEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRAdducto',RightAdductorsEMG, 80)  
                except:
                    pass
                # Montreal
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRVastMed',RightVasltusMedialisEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRLatHams',RightLateralHamstringsEMG, 80)
                except:
                    pass
                try:
                    WriteArrayToGCD_ComputeEMGenvelope(GCDFile,'RightRawRPerLong',RightPeroneusLongusEMG, 80)  
                except:
                    pass
            
            # Check if Foot Model data exists
            if self.valueRightFootModelCheck == '1':
                WriteArrayToGCD(GCDFile,'RightHindFootTilt',RightHindFootTilt)
                WriteArrayToGCD(GCDFile,'RightHindFootObliquity',RightHindFootObliquity)
                WriteArrayToGCD(GCDFile,'RightHindFootRotation',RightHindFootRotation)
                WriteArrayToGCD(GCDFile,'RightForeFootTilt',RightForeFootTilt)
                WriteArrayToGCD(GCDFile,'RightForeFootRotation',RightForeFootRotation)
                WriteArrayToGCD(GCDFile,'RightAnkleComplexDorsiPlanFlex',RightAnkleComplexDorsiPlanFlex)
                WriteArrayToGCD(GCDFile,'RightAnkleComplexValgVar',RightAnkleComplexValgVar)
                WriteArrayToGCD(GCDFile,'RightAnkleComplexRotation',RightAnkleComplexRotation)
                WriteArrayToGCD(GCDFile,'RightMidFootDorsiPlanFlex',RightMidFootDorsiPlanFlex)
                WriteArrayToGCD(GCDFile,'RightMidFootSupPron',RightMidFootSupPron)
                WriteArrayToGCD(GCDFile,'RightMidFootAbAdduct',RightMidFootAbAdduct)
                WriteArrayToGCD(GCDFile,'RightHalDorsiPlanFlex',RightToeFlexExt)
                WriteArrayToGCD(GCDFile,'RightHalValgVar',RightToeValgVar)
                WriteArrayToGCD(GCDFile,'RightSupination',RightSupination)
                WriteArrayToGCD(GCDFile,'RightSkew',RightSkew)

        
        
        GCDFile.close()
        
#Calls the main Function
CreateGCD_Main()
