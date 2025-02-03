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
# Static Model computes posture and stores Technical to Anatomical Coordinate Transformaion

Created on Thu Feb 01 11:09:51 2018
Last Update: Aug 26, 2024

@author: psaraswat
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
VersionNumber = 'Py3_v1.3'

import os.path
import sys
import datetime

import tkinter as tk     ## Python 3.x

#import tkFileDialog
from tkinter import filedialog

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import reportlab.lib.colors as reportlabColors

import numpy as np

#import Vicon Nexus Subroutines
from viconnexusapi import ViconNexus
vicon = ViconNexus.ViconNexus()

#import Common Vector/Matrix Operations Modules
import Py3_MathModules as math
import Py3_GaitModules as gait

UserPreferencesFileName = 'M:\\MAL Use Only\\MAL Software Program Files\\Python\\Py3_UserPreferences.py'

# First Argument is the command name, second argument is the testing condition
DefaultTestingCondition = 'BF'
TestingCondition = DefaultTestingCondition
if len(sys.argv) > 1:
    TestingCondition = sys.argv[1]

#print(vicon.GetSubjectNames())
SubjectName = vicon.GetSubjectNames()[0]
FilePath, FileName = vicon.GetTrialName()
#StaticDataFileName = FilePath + 'Static_BF_' + SubjectName + '.py'
# Condition- Barefoot (BF) string read as Script Argument
StaticDataFileName = FilePath + 'Static_' + TestingCondition + '_' + SubjectName + '.py'
SittingFootStaticDataFileName = FilePath + 'SittingFootStatic_' + TestingCondition + '_' + SubjectName + '.py' 
      
#Height and Width of App Display
AppHeight=950 
AppWidth=800 
#Default font for display
Large_Font= "Calibri 14 bold" #("Calibri", 20)
Small_Font_Bold = "Calibri 12 bold"
Small_Font= ("Calibri", 12)
Smaller_Font= ("Calibri", 10)
Bold_Small_Font="Calibri 14 bold"

#This is the main function and has references to all the forms
class Static_Main(tk.Tk):
    #This __init__ part of the code runs everytime
    def __init__(self):
        
        tk.Tk.__init__(self)
        # Specify title of Form
        tk.Tk.wm_title(self, "Static")
        
        #Create a dictionary of frames/forms
        self.frames = {} 
        frames = (PatientInfo_Page, QAreport_Page, StaticSubjectCalibrationReport_Page)
        #Specify all the form names
        for F in frames:
            frame = F(self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame
    
        #Initialize the first form
        self.frames[PatientInfo_Page].tkraise()
        self.frames[PatientInfo_Page].build_UI()
        
class PatientInfo_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=AppWidth, height=AppHeight)
        self.parent = parent
        self.grid()
         
    def build_UI(self):    
        # Crete a Canvas to draw section on forms
        SectionCanvas = tk.Canvas(self, width=AppWidth, height=AppHeight)
        SectionCanvas.pack()
        
        # Proceed button chnages the form display to QA Report and saves data
        ProceedButton = tk.Button(self, text="Save &" + '\n'+ "Proceed",font=Small_Font,  justify = 'center', command= lambda: [saveSubjectData(),self.parent.frames[QAreport_Page].tkraise(),self.parent.frames[QAreport_Page].build_UI()])
        ProceedButton.place(x=700,y=20,width=90,height=810)
        # Quite buton closes app
        QuitButton = tk.Button(self,text="Quit",font=Small_Font, command=lambda: quit())
        QuitButton.place(x=700,y=840,width=90,height=90) 

# =============================================================================
#       Patient Information widgets are created here 
# =============================================================================       

        # Draw box to identify Patient Information region
        SectionCanvas.create_rectangle(20, 20, 680, 250)
        
        #Create all the labels, buttons and entry widgets and specify their location on form
        PatientInformationTitle = tk.Label(self, text="Patient Information", font=Large_Font)
        PatientInformationTitle.place(x=50,y=0)
                
        FirstNameLabel = tk.Label(self, text="First Name", font=Small_Font)
        FirstNameLabel.place(x=50,y=40)
        LastNameLabel = tk.Label(self, text="Last Name", font=Small_Font)
        LastNameLabel.place(x=350,y=40)
        FirstName = tk.Entry(self)
        FirstName.place(x=50,y=60,width=250,height=20)
        LastName = tk.Entry(self)
        LastName.place(x=350,y=60,width=300,height=20)
        
        PatientNumberLabel = tk.Label(self, text="Patient Number", font=Small_Font) 
        PatientNumberLabel.place(x=50,y=90)
        PatientNumber = tk.Entry(self)
        PatientNumber.place(x=50,y=110,width=250,height=20)
        
        DateOfBirthLabel = tk.Label(self, text="Date Of Birth", font=Small_Font) 
        DateOfBirthLabel.place(x=350,y=90)
        DateOptions = ["01","02","03","04","05","06","07","08","09","10",
                       "11","12","13","14","15","16","17","18","19","20",
                       "21","22","23","24","25","26","27","28","29","30","31"]
        Date = tk.StringVar(self)
        Date.set(DateOptions[0]) # default value
        DateDropDown = tk.OptionMenu(self, Date, *DateOptions)
        DateDropDown.place(x=350,y=110,width=50,height=25)
        MonthOptions = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        Month = tk.StringVar(self)
        Month.set(MonthOptions[0]) # default value
        MonthDropDown = tk.OptionMenu(self, Month, *MonthOptions)
        MonthDropDown.place(x=410,y=110,width=80,height=25)
        YearOptions = ["1981","1982","1983","1984","1985","1986","1987","1988","1989","1990",
                       "1991","1992","1993","1994","1995","1996","1997","1998","1999","2000",
                       "2001","2002","2003","2004","2005","2006","2007","2008","2009","2010",
                       "2011","2012","2013","2014","2015","2016","2017","2018","2019","2020",
                       "2021","2022","2023","2024","2025","2026","2027","2028","2029","2030"]
        Year = tk.StringVar(self)
        Year.set(YearOptions[0]) # default value
        YearDropDown = tk.OptionMenu(self, Year, *YearOptions)
        YearDropDown.place(x=500,y=110,width=80,height=25)
 
######## Remove Diagnosis from the form ##############################################################   
#        DiagnosisLabel = tk.Label(self, text="Diagnosis", font=Small_Font) 
#        DiagnosisLabel.place(x=50,y=190)
#        
#        DiagnosisOptions = ["Cerebral Palsy","Cerebral Palsy- Diplegia","Cerebral Palsy- Hemiplegia",
#                            "Other"]
#        Diagnosis = tk.StringVar(self)
#        Diagnosis.set(DiagnosisOptions[0]) # default value
#        DiagnosisDropDown = tk.OptionMenu(self, Diagnosis, *DiagnosisOptions)
#        DiagnosisDropDown.place(x=50,y=210,width=250,height=25)
#######################################################################################################
        
        StaticForwardDirectionLabel = tk.Label(self, text="Static Forward Direction", font=Small_Font) 
        StaticForwardDirectionLabel.place(x=50,y=190)
        
        StaticForwardDirectionOptions = ["+X","-X","+Y","-Y"]
        StaticForwardDirection = tk.StringVar(self)
        if os.path.exists(StaticDataFileName):
            exec(open(StaticDataFileName).read())
        else:
            exec(open(UserPreferencesFileName).read())
        #StaticForwardDirection.set(StaticForwardDirectionOptions[0]) # default value
        StaticForwardDirection.set(self.StaticForwardDirection)
        StaticForwardDirectionDropDown = tk.OptionMenu(self, StaticForwardDirection, *StaticForwardDirectionOptions)
        StaticForwardDirectionDropDown.place(x=50,y=210,width=250,height=25)
        
        
        AssistiveDeviceLabel = tk.Label(self, text="AssistiveDevice", font=Small_Font) 
        AssistiveDeviceLabel.place(x=350,y=190)
        AssistiveDeviceOptions = ["None","Walker","Walker - Wheeled","Walker - Pickup",
                                  "Crutches","Crutches - Axillary","Crutches - Loftstrand",
                                  "Cane","Bobath Poles","Hand-Held","Other"]
        AssistiveDevice = tk.StringVar(self)
        AssistiveDevice.set(AssistiveDeviceOptions[0]) # default value
        AssistiveDeviceDropDown = tk.OptionMenu(self, AssistiveDevice, *AssistiveDeviceOptions)
        AssistiveDeviceDropDown.place(x=350,y=210,width=250,height=25)
        
        TrialActivityLabel = tk.Label(self, text="Trial Activity", font=Small_Font) 
        TrialActivityLabel.place(x=50,y=140)
        TrialActivityOptions = ["Static","Walking - Fast","Walking - Heel-Toe","Running","Sprinting",
                                "Stair Ascent","Stair Descent","Sit-To-Stand","Other"]
        TrialActivity = tk.StringVar(self)
        TrialActivity.set(TrialActivityOptions[0]) # default value
        TrialActivityDropDown = tk.OptionMenu(self, TrialActivity, *TrialActivityOptions)
        TrialActivityDropDown.place(x=50,y=160,width=250,height=25)
        
        TrialModifierLabel = tk.Label(self, text="TrialModifier", font=Small_Font) 
        TrialModifierLabel.place(x=350,y=140)
        TrialModifierOptions = ["Barefoot","B AFO-PLS","L AFO-PLS","R AFO-PLS",
                                "B AFO-Solid","L AFO-Solid","R AFO-Solid",
                                "B AFO-FR","L AFO-FR","R AFO-FR",
                                "B AFO-Artic","L AFO-Artic","R AFO-Artic",
                                "L LIFT","R LIFT","B SMO","L SMO","R SMO",
                                "B UCBL","L UCBL","R UCBL",
                                "KAFO","HKAFO","RGO","Parawalker","Shoes Only","Other"]
        TrialModifier = tk.StringVar(self)
        TrialModifier.set(TrialModifierOptions[0]) # default value
        TrialModifierDropDown = tk.OptionMenu(self, TrialModifier, *TrialModifierOptions)
        TrialModifierDropDown.place(x=350,y=160,width=250,height=25)
        
        StaticFrameNumberLabel = tk.Label(self, text="Static Frame Number", font=Small_Font)
        StaticFrameNumberLabel.place(x=450,y=255)
        StaticFrameNumber = tk.Entry(self, justify='center')
        StaticFrameNumber.place(x=600,y=255,width=40,height=20)
# =============================================================================
#       Anthropometric Parameters widgets are created here
# =============================================================================
        # Draw box to identify Anthropometric Parameters region
        SectionCanvas.create_rectangle(20, 280, 680, 715)
        
        AnthropometricParametersTitle = tk.Label(self, text="Anthropometric Parameters", font=Large_Font)
        AnthropometricParametersTitle.place(x=50,y=260)
        
        StaticFileLabel = tk.Label(self, text="Static File", font=Small_Font)
        StaticFileLabel.place(x=50,y=300)
        StaticFile = tk.Entry(self)
        StaticFile.place(x=50,y=320,width=100,height=20)
        
        AnthropometricFileLabel = tk.Label(self, text="Anthropometric File", font=Small_Font)
        AnthropometricFileLabel.place(x=200,y=300)
        #AnthropometricFile = tk.Entry(self)
        AnthropometricFile = tk.Label(self, text="-", font=Smaller_Font)
        AnthropometricFile.place(x=200,y=320)

        DateOfDataCaptureLabel = tk.Label(self, text="Date Of Data Capture", font=Small_Font) 
        DateOfDataCaptureLabel.place(x=400,y=300)
        #Find current date
        now = datetime.datetime.now()
        DataCollectionDate = tk.StringVar(self)
        DataCollectionDate.set(DateOptions[int(now.day)-1]) # default value
        DataCollectionDateDropDown = tk.OptionMenu(self, DataCollectionDate, *DateOptions)
        DataCollectionDateDropDown.place(x=400,y=320,width=50,height=25)
        DataCollectionMonth = tk.StringVar(self)
        DataCollectionMonth.set(MonthOptions[int(now.month)-1]) # default value
        DataCollectionMonthDropDown = tk.OptionMenu(self, DataCollectionMonth, *MonthOptions)
        DataCollectionMonthDropDown.place(x=460,y=320,width=80,height=25)
        DataCollectionYearOptions = ["1991","1992","1993","1994","1995","1996","1997","1998","1999","2000",
                                     "2001","2002","2003","2004","2005","2006","2007","2008","2009","2010",
                                     "2011","2012","2013","2014","2015","2016","2017","2018","2019","2020",
                                     "2021","2022","2023","2024","2025","2026","2027","2028","2029","2030"]
        DataCollectionYear = tk.StringVar(self)
        DataCollectionYear.set(YearOptions[int(now.year)-1981]) # default value
        DataCollectionYearDropDown = tk.OptionMenu(self, DataCollectionYear, *DataCollectionYearOptions)
        DataCollectionYearDropDown.place(x=550,y=320,width=80,height=25)
        
        BodyMassUnitLabel = tk.Label(self, text='kg', font=Small_Font)
        BodyMassUnitLabel.place(x=50,y=360)
        BodyMassLabel = tk.Label(self, text='BodyMass', font=Small_Font)
        BodyMassLabel.place(x=350,y=360)
        BodyMass = tk.Entry(self,justify='center')
        BodyMass.place(x=250,y=360,width=80,height=20)
        
        HeightUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        HeightUnitLabel.place(x=50,y=385)
        HeightLabel = tk.Label(self, text='Height', font=Small_Font)
        HeightLabel.place(x=350,y=385)
        Height = tk.Entry(self,justify='center')
        Height.place(x=250,y=385,width=80,height=20)
        
        ASISdistUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        ASISdistUnitLabel.place(x=50,y=410)
        ASISdistLabel = tk.Label(self, text='ASIS-to-ASIS Distance', font=Small_Font)
        ASISdistLabel.place(x=350,y=410)
        ASISdist = tk.Entry(self,justify='center')
        ASISdist.place(x=250,y=410,width=80,height=20)
        
        LeftSideLabel = tk.Label(self, text='Left', font=Small_Font)
        LeftSideLabel.place(x=150,y=430)
        RightSideLabel = tk.Label(self, text='Right', font=Small_Font)
        RightSideLabel.place(x=250,y=430)
        
        LegLengthUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        LegLengthUnitLabel.place(x=50,y=460)
        LegLengthLabel = tk.Label(self, text='Leg Length', font=Small_Font)
        LegLengthLabel.place(x=350,y=460)
        LeftLegLength = tk.Entry(self,justify='center')
        LeftLegLength.place(x=150,y=460,width=80,height=20)
        RightLegLength = tk.Entry(self,justify='center')
        RightLegLength.place(x=250,y=460,width=80,height=20)
        
        KneeWidthUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        KneeWidthUnitLabel.place(x=50,y=485)
        KneeWidthLabel = tk.Label(self, text='Knee Width', font=Small_Font)
        KneeWidthLabel.place(x=350,y=485)
        LeftKneeWidth = tk.Entry(self,justify='center')
        LeftKneeWidth.place(x=150,y=485,width=80,height=20)
        RightKneeWidth = tk.Entry(self,justify='center')
        RightKneeWidth.place(x=250,y=485,width=80,height=20)
        
        AnkleWidthUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        AnkleWidthUnitLabel.place(x=50,y=510)
        AnkleWidthLabel = tk.Label(self, text='Ankle Width', font=Small_Font)
        AnkleWidthLabel.place(x=350,y=510)
        LeftAnkleWidth = tk.Entry(self,justify='center')
        LeftAnkleWidth.place(x=150,y=510,width=80,height=20)
        RightAnkleWidth = tk.Entry(self,justify='center')
        RightAnkleWidth.place(x=250,y=510,width=80,height=20)
        
        ASIStoGTdistUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        ASIStoGTdistUnitLabel.place(x=50,y=535)
        ASIStoGTdistLabel = tk.Label(self, text='ASIS-to-GT Distance', font=Small_Font)
        ASIStoGTdistLabel.place(x=350,y=535)
        LeftASIStoGTdist = tk.Entry(self,justify='center')
        LeftASIStoGTdist.place(x=150,y=535,width=80,height=20)
        RightASIStoGTdist = tk.Entry(self,justify='center')
        RightASIStoGTdist.place(x=250,y=535,width=80,height=20)
        
        #Draw box for Foot Model
        SectionCanvas.create_rectangle(40, 575, 660, 710, outline='grey')
        
        FootModelTitle = tk.Label(self, text="Foot Model", font=Small_Font)
        FootModelTitle.place(x=75,y=562)
        
        self.LeftFootModelCheck=tk.IntVar()
        self.LeftFootModelCheck.set('0')
        LeftFootModelCheckButton = tk.Checkbutton(self, text='Left', variable=self.LeftFootModelCheck, font=Small_Font)
        LeftFootModelCheckButton.place(x=150,y=580)
        
        self.RightFootModelCheck=tk.IntVar()
        self.RightFootModelCheck.set('0')
        RightFootModelCheckButton = tk.Checkbutton(self, text='Right', variable=self.RightFootModelCheck, font=Small_Font)
        RightFootModelCheckButton.place(x=250,y=580)
        
        HindfootVarusUnitLabel = tk.Label(self, text='deg', font=Small_Font)
        HindfootVarusUnitLabel.place(x=50,y=610)
        HindfootVarusLabel = tk.Label(self, text='Hindfoot Varus/Valgus', font=Small_Font)
        HindfootVarusLabel.place(x=350,y=610)
        LeftHindfootVarus = tk.Entry(self,justify='center')
        LeftHindfootVarus.place(x=150,y=610,width=80,height=20)
        RightHindfootVarus = tk.Entry(self,justify='center')
        RightHindfootVarus.place(x=250,y=610,width=80,height=20)
        
        CalcanealPitchUnitLabel = tk.Label(self, text='deg', font=Small_Font)
        CalcanealPitchUnitLabel.place(x=50,y=635)
        CalcanealPitchLabel = tk.Label(self, text='Calcaneal Pitch', font=Small_Font)
        CalcanealPitchLabel.place(x=350,y=635)
        LeftCalcanealPitch = tk.Entry(self,justify='center')
        LeftCalcanealPitch.place(x=150,y=635,width=80,height=20)
        RightCalcanealPitch = tk.Entry(self,justify='center')
        RightCalcanealPitch.place(x=250,y=635,width=80,height=20)
        
        HindfootProgressionUnitLabel = tk.Label(self, text='deg', font=Small_Font)
        HindfootProgressionUnitLabel.place(x=50,y=660)
        HindfootProgressionLabel = tk.Label(self, text='Hindfoot Progression', font=Small_Font)
        HindfootProgressionLabel.place(x=350,y=660)
        LeftHindfootProgression = tk.Entry(self,justify='center')
        LeftHindfootProgression.place(x=150,y=660,width=80,height=20)
        RightHindfootProgression = tk.Entry(self,justify='center')
        RightHindfootProgression.place(x=250,y=660,width=80,height=20)
        
        FirstMetatarsalPitchUnitLabel = tk.Label(self, text='deg', font=Small_Font)
        FirstMetatarsalPitchUnitLabel.place(x=50,y=685)
        FirstMetatarsalPitchLabel = tk.Label(self, text='First Metatarsal Pitch', font=Small_Font)
        FirstMetatarsalPitchLabel.place(x=350,y=685)
        LeftFirstMetatarsalPitch = tk.Entry(self,justify='center')
        LeftFirstMetatarsalPitch.place(x=150,y=685,width=80,height=20)
        RightFirstMetatarsalPitch = tk.Entry(self,justify='center')
        RightFirstMetatarsalPitch.place(x=250,y=685,width=80,height=20)
        
        
        
# =============================================================================
#       Test Conditions widgets are created here
# =============================================================================
        # Draw box to identify Test Conditions region
        SectionCanvas.create_rectangle(20, 745, 680, 945)
        
        TestConditionsTitle = tk.Label(self, text="Special Test Conditions", font=Large_Font)
        TestConditionsTitle.place(x=50,y=725)
        
        #Draw box for plantigrade condition
        SectionCanvas.create_rectangle(40, 765, 660, 800, dash=1)
        
        PlantigradeLabel = tk.Label(self, text='Subject Plantigrade during Static Trial', font=Small_Font)
        PlantigradeLabel.place(x=350,y=770)
        self.LeftPlantigradeCheck=tk.IntVar()
        self.LeftPlantigradeCheck.set('1')
        LeftPlantigradeCheckButton = tk.Checkbutton(self, text='Left', variable=self.LeftPlantigradeCheck, font=Small_Font)
        LeftPlantigradeCheckButton.place(x=150,y=770)
        self.RightPlantigradeCheck=tk.IntVar()
        self.RightPlantigradeCheck.set('1')
        RighttPlantigradeCheckButton = tk.Checkbutton(self, text='Right',variable=self.RightPlantigradeCheck, font=Small_Font)
        RighttPlantigradeCheckButton.place(x=250,y=770)
        
        #Draw box for shod condition
        SectionCanvas.create_rectangle(40, 810, 520, 890, dash=1)
        
        self.SubjectShodCheck = tk.IntVar()
        SujectShodCheckButton = tk.Checkbutton(self, text='Subject Shod (with or without orthoses)', variable=self.SubjectShodCheck, font=Small_Font)        
        SujectShodCheckButton.place(x=150,y=815)
        SoleThicknessUnitLabel = tk.Label(self, text='mm', font=Small_Font)
        SoleThicknessUnitLabel.place(x=50,y=860)
        SoleThicknessDescriptionLine1Label = tk.Label(self, text='Difference in sole thicknes', font=Smaller_Font)
        SoleThicknessDescriptionLine2Label = tk.Label(self, text='between heel and toes (mm)', font=Smaller_Font)
        SoleThicknessDescriptionLine1Label.place(x=350,y=840)
        SoleThicknessDescriptionLine2Label.place(x=350,y=860)
        LeftSoleThicknessLabel = tk.Label(self, text='Left', font=Small_Font)
        LeftSoleThicknessLabel.place(x=150,y=840)
        RightSoleThicknessLabel = tk.Label(self, text='Right', font=Small_Font)
        RightSoleThicknessLabel.place(x=250,y=840)
        LeftSoleThickness = tk.Entry(self,justify='center')
        LeftSoleThickness.place(x=150,y=860,width=80,height=20)
        RightSoleThickness = tk.Entry(self,justify='center')
        RightSoleThickness.place(x=250,y=860,width=80,height=20)
        
        #Draw box for Medial Knee Marker or KAD Option
        SectionCanvas.create_rectangle(530, 810, 660, 890, dash=1)
        
        KneeAlignmentLabel = tk.Label(self,text='Knee Option', font = Small_Font)
        KneeAlignmentLabel.place(x=535, y=815)
        self.KneeAlignmentCheck = tk.IntVar()
        self.KneeAlignmentCheck.set('1')
        KneeAlignmentCheckButton0 = tk.Radiobutton(self, text='KAD',variable=self.KneeAlignmentCheck, value=0, font=Small_Font)
        KneeAlignmentCheckButton1 = tk.Radiobutton(self, text='M/L Markers',variable=self.KneeAlignmentCheck, value=1, font=Small_Font)
        KneeAlignmentCheckButton0.place(x=535,y=835)
        KneeAlignmentCheckButton1.place(x=535,y=855)
        
        
        #Draw box for Pelvic Fix Option
        SectionCanvas.create_rectangle(40, 900, 660, 940, dash=1)
        
        PelvicFixLabel = tk.Label(self, text='Apply Pelvic Fix Option', font=Small_Font)
        PelvicFixLabel.place(x=350,y=905)
        self.PelvicFixCheck=tk.IntVar()
        self.PelvicFixCheck.set('0')
        PelvicFixCheckButton0 = tk.Radiobutton(self, text='N/A',variable=self.PelvicFixCheck, value=0, font=Small_Font)
        PelvicFixCheckButton1 = tk.Radiobutton(self, text='Iliac',variable=self.PelvicFixCheck, value=1, font=Small_Font)
        PelvicFixCheckButton2 = tk.Radiobutton(self, text='Triad',variable=self.PelvicFixCheck, value=2, font=Small_Font)
        PelvicFixCheckButton0.place(x=50,y=905)
        PelvicFixCheckButton1.place(x=150,y=905)
        PelvicFixCheckButton2.place(x=250,y=905)
               
# =========================================================================================
#       Read Parameters from Nexus or existing Static Parameters File and tabulate parameters    
# =========================================================================================
        SubjectName = vicon.GetSubjectNames()[0]
        FilePath, FileName = vicon.GetTrialName()
        StartFrame, EndFrame = vicon.GetTrialRegionOfInterest()
        
        if os.path.exists(StaticDataFileName):
            # Execute Static File to read stored parameters values
            exec(open(StaticDataFileName).read())
            # Put in stored values onto display
            FirstName.insert(0,self.valueFirstName)
            LastName.insert(0,self.valueLastName)
            PatientNumber.insert(0,self.valuePatientNumber)
            Date.set(self.valueDateOfBirth_Day)
            Month.set(self.valueDateOfBirth_Month)
            Year.set(self.valueDateOfBirth_Year)
            TrialActivity.set(self.valueTrialActivity)
            TrialModifier.set(self.valueTrialModifier)
            AssistiveDevice.set(self.valueAssistiveDevice)
            
            #StaticFile.insert(0,self.valueStaticFile)
            # Always Use current File Name as Static FileName-
            StaticFile.insert(0,FileName)
            
            #AnthropometricFile.insert(0,self.valueAnthropometricFile)
            AnthropometricFile['text'] = self.valueAnthropometricFile
            DataCollectionDate.set(self.valueDataCollectionDate_Day)
            DataCollectionMonth.set(self.valueDataCollectionDate_Month)
            DataCollectionYear.set(self.valueDataCollectionDate_Year)
            BodyMass.insert(0,self.valueBodyMass)
            Height.insert(0,self.valueHeight)
            ASISdist.insert(0,self.valueASISdist)
            LeftLegLength.insert(0,self.valueLeftLegLength)
            RightLegLength.insert(0,self.valueRightLegLength)
            LeftKneeWidth.insert(0,self.valueLeftKneeWidth)
            RightKneeWidth.insert(0,self.valueRightKneeWidth)
            LeftAnkleWidth.insert(0,self.valueLeftAnkleWidth)
            RightAnkleWidth.insert(0,self.valueRightAnkleWidth)
            LeftASIStoGTdist.insert(0,self.valueLeftASIStoGTdist)
            RightASIStoGTdist.insert(0,self.valueRightASIStoGTdist)
            self.LeftFootModelCheck.set(self.valueLeftFootModelCheck)
            self.RightFootModelCheck.set(self.valueRightFootModelCheck)
            LeftHindfootVarus.insert(0,self.valueLeftHindfootVarus)
            RightHindfootVarus.insert(0,self.valueRightHindfootVarus)
            # Hindfoot Progression values wouldn't exist in older Static File so leave emppy if unavailable
            try:
                LeftHindfootProgression.insert(0,self.valueLeftHindfootProgression)
            except:
                pass
            try:
                RightHindfootProgression.insert(0,self.valueRightHindfootProgression)
            except:
                pass
            LeftFirstMetatarsalPitch.insert(0,self.valueLeftFirstMetatarsalPitch)
            RightFirstMetatarsalPitch.insert(0,self.valueRightFirstMetatarsalPitch)
            LeftCalcanealPitch.insert(0,self.valueLeftCalcanealPitch)
            RightCalcanealPitch.insert(0,self.valueRightCalcanealPitch)
            self.LeftPlantigradeCheck.set(self.valueLeftPlantigradeCheck)
            self.RightPlantigradeCheck.set(self.valueRightPlantigradeCheck)
            # Write Sole Thickness values only when subjet is shod
            if self.valueSujectShodCheck == '1':
                self.SubjectShodCheck.set(self.valueSujectShodCheck)
                LeftSoleThickness.insert(0,self.valueLeftSoleThickness)
                RightSoleThickness.insert(0,self.valueRightSoleThickness)
            self.PelvicFixCheck.set(self.valuePelvicFixCheck)   
            try:# If KAD option exist
                self.KneeAlignmentCheck.set(self.valueKneeAlignmentCheck)   
            except:# Default if KAD option not found in Py file
                self.KneeAlignmentCheck.set('0')
            try:# If Static Frame Option exists
                StaticFrameNumber.insert(0,self.valueStaticFrameNumber)
            except:# Default if Static Frame Number not found in Py file
                StaticFrameNumber.insert(0,StartFrame + 20) # Default to 20th frame.
        else:
            # If Static parmaeters file doesn't exist, read parameters values from Nexus
            PatientNumber.insert(0,SubjectName)
            StaticFile.insert(0,FileName)
            StaticFrameNumber.insert(0,StartFrame + 20) # Default to 20th frame.
            # Update Date Collection Date
            SystemFileName = FileName + '.x1d'
            now = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(FilePath,SystemFileName)))
            DataCollectionDate.set(DateOptions[int(now.day)-1]) # File Creation Date
            DataCollectionMonth.set(MonthOptions[int(now.month)-1]) # File Creation Date
            DataCollectionYear.set(YearOptions[int(now.year)-1981]) # File Creation Date
            if vicon.GetSubjectParam(SubjectName, 'Bodymass')[1] is True:
                BodyMass.insert(0,round(vicon.GetSubjectParam( SubjectName, 'Bodymass' )[0],2))
            if vicon.GetSubjectParam(SubjectName, 'Height')[1] is True:
                Height.insert(0,int(vicon.GetSubjectParam( SubjectName, 'Height' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'InterAsisDistance')[1] is True:
                ASISdist.insert(0,int(vicon.GetSubjectParam( SubjectName, 'InterAsisDistance' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'LeftLegLength')[1] is True:
                LeftLegLength.insert(0,int(vicon.GetSubjectParam( SubjectName, 'LeftLegLength' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'RightLegLength')[1] is True:
                RightLegLength.insert(0,int(vicon.GetSubjectParam( SubjectName, 'RightLegLength' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'LeftKneeWidth')[1] is True:
                LeftKneeWidth.insert(0,int(vicon.GetSubjectParam( SubjectName, 'LeftKneeWidth' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'RightKneeWidth')[1] is True:
                RightKneeWidth.insert(0,int(vicon.GetSubjectParam( SubjectName, 'RightKneeWidth' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'LeftAnkleWidth')[1] is True:
                LeftAnkleWidth.insert(0,int(vicon.GetSubjectParam( SubjectName, 'LeftAnkleWidth' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'RightAnkleWidth')[1] is True:
                RightAnkleWidth.insert(0,int(vicon.GetSubjectParam( SubjectName, 'RightAnkleWidth' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'LeftAsisTrocanterDistance')[1] is True:
                LeftASIStoGTdist.insert(0,int(vicon.GetSubjectParam( SubjectName, 'LeftAsisTrocanterDistance' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'RightAsisTrocanterDistance')[1] is True:
                RightASIStoGTdist.insert(0,int(vicon.GetSubjectParam( SubjectName, 'RightAsisTrocanterDistance' )[0]))
            # Read Foot Model Parameters
            if vicon.GetSubjectParam(SubjectName, 'LeftVarValAngle')[1] is True:
                LeftHindfootVarus.insert(0,int(round(vicon.GetSubjectParam( SubjectName, 'LeftVarValAngle' )[0],0)))
                self.LeftFootModelCheck.set('1')
            if vicon.GetSubjectParam(SubjectName, 'RightVarValAngle')[1] is True:
                RightHindfootVarus.insert(0,int(round(vicon.GetSubjectParam( SubjectName, 'RightVarValAngle' )[0],0)))
                self.RightFootModelCheck.set('1')
            if vicon.GetSubjectParam(SubjectName, 'Left1stRayPitch')[1] is True:
                LeftFirstMetatarsalPitch.insert(0,int(vicon.GetSubjectParam( SubjectName, 'Left1stRayPitch' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'Right1stRayPitch')[1] is True:
                RightFirstMetatarsalPitch.insert(0,int(vicon.GetSubjectParam( SubjectName, 'Right1stRayPitch' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'LeftCalcanealPitch')[1] is True:
                LeftCalcanealPitch.insert(0,int(vicon.GetSubjectParam( SubjectName, 'LeftCalcanealPitch' )[0]))
            if vicon.GetSubjectParam(SubjectName, 'RightCalcanealPitch')[1] is True:
                RightCalcanealPitch.insert(0,int(vicon.GetSubjectParam( SubjectName, 'RightCalcanealPitch' )[0]))
            #############################    
            # Read Calcaneal Pitch and Varus Valgus from Sitting Foot Static, if exists
            if os.path.exists(SittingFootStaticDataFileName):
                # Execute Static File to read stored parameters values
                exec(open(SittingFootStaticDataFileName).read())
                LeftCalcanealPitch.delete(0,tk.END)
                RightCalcanealPitch.delete(0,tk.END)
                LeftCalcanealPitch.insert(0,self.valueLeftCalcanealPitch)
                RightCalcanealPitch.insert(0,self.valueRightCalcanealPitch)
                
                LeftHindfootVarus.delete(0,tk.END)
                RightHindfootVarus.delete(0,tk.END)
                LeftHindfootVarus.insert(0,self.valueLeftHindfootVarus)
                RightHindfootVarus.insert(0,self.valueRightHindfootVarus)
                
                LeftHindfootProgression.delete(0,tk.END)
                RightHindfootProgression.delete(0,tk.END)
                try:
                    LeftHindfootProgression.insert(0,self.valueLeftHindfootProgression)
                except:
                    pass
                try:
                    RightHindfootProgression.insert(0,self.valueRightHindfootProgression)
                except:
                    pass
                
            ##############################
            if vicon.GetSubjectParam(SubjectName, 'Bodymass')[1] is False:
                # Calculate BodyMass from Force Plate
                DeviceNames = vicon.GetDeviceNames()
                
                for i in range(len(DeviceNames)):
                    # For Static trial, subject stands on Force Plate 1 "FP1"
                    if str.split(DeviceNames[i])[0] == "FP1":
                        StaticForcePlateName = DeviceNames[i]
                DeviceID = vicon.GetDeviceIDFromName(StaticForcePlateName)
                DeviceOutputID = vicon.GetDeviceOutputIDFromName(DeviceID,'Force')
                ChannelID = vicon.GetDeviceChannelIDFromName(DeviceID, DeviceOutputID, 'Fz' )
                FP1_Fz=vicon.GetDeviceChannel(DeviceID,DeviceOutputID,ChannelID)
                Max_FP1_Fz=round(-np.average(FP1_Fz[0])/9.81,2)
                
                for i in range(len(DeviceNames)):
                    # For multi-segment foot Static trial, subject stands on Force Plate 2 "FP2"
                    if str.split(DeviceNames[i])[0] == "FP2":
                        StaticForcePlateName = DeviceNames[i]
                DeviceID = vicon.GetDeviceIDFromName(StaticForcePlateName)
                DeviceOutputID = vicon.GetDeviceOutputIDFromName(DeviceID,'Force')
                ChannelID = vicon.GetDeviceChannelIDFromName(DeviceID, DeviceOutputID, 'Fz' )
                FP2_Fz=vicon.GetDeviceChannel(DeviceID,DeviceOutputID,ChannelID)
                Max_FP2_Fz=round(-np.average(FP2_Fz[0])/9.81,2)
                
                BodyMass.insert(0,max(Max_FP1_Fz,Max_FP2_Fz))
                # Write the Body Mass value in Nexus Parameters
                vicon.SetSubjectParam(SubjectName,'Bodymass',max(Max_FP1_Fz,Max_FP2_Fz)) 
            
            # =============================================================================
            #             AFO Condition- Populate Subject Information from Barefoot 
            # =============================================================================
            DefaultStaticDataFileName = FilePath + 'Static_' + DefaultTestingCondition + '_' + SubjectName + '.py'
            if os.path.exists(DefaultStaticDataFileName):
                # Execute Default Static File to read stored Subject parameters values
                exec(open(DefaultStaticDataFileName).read())
                # Clear Widgets before overwriting 
                FirstName.delete(0,tk.END)
                LastName.delete(0,tk.END)
                PatientNumber.delete(0,tk.END)
                BodyMass.delete(0,tk.END)
                Height.delete(0,tk.END)
                ASISdist.delete(0,tk.END)
                LeftLegLength.delete(0,tk.END)
                RightLegLength.delete(0,tk.END)
                # Put in stored values onto display
                FirstName.insert(0,self.valueFirstName)
                LastName.insert(0,self.valueLastName)
                PatientNumber.insert(0,self.valuePatientNumber)
                Date.set(self.valueDateOfBirth_Day)
                Month.set(self.valueDateOfBirth_Month)
                Year.set(self.valueDateOfBirth_Year)
                #AnthropometricFile.insert(0,self.valueAnthropometricFile)
                DataCollectionDate.set(self.valueDataCollectionDate_Day)
                DataCollectionMonth.set(self.valueDataCollectionDate_Month)
                DataCollectionYear.set(self.valueDataCollectionDate_Year)
                BodyMass.insert(0,self.valueBodyMass)
                Height.insert(0,self.valueHeight)
                ASISdist.insert(0,self.valueASISdist)
                LeftLegLength.insert(0,self.valueLeftLegLength)
                RightLegLength.insert(0,self.valueRightLegLength)

        # =============================================================================
        #       Function to save Subject parameters in Static_BF_MRN.py file. It gets executed with Proceed button.
        # =============================================================================
        def saveSubjectData():
            if os.path.exists(StaticDataFileName):
                # Read Current File
                StaticDataFile = open(StaticDataFileName,'r')
                lines=StaticDataFile.readlines()
                StaticDataFile.close()
                
                # Open Static py File
                StaticDataFile = open(StaticDataFileName,'w+')
                # Restore the UserPreferences
                UserPreferencesBlockEnds = 0
                for line in lines:
                    words=line.split()
                    if words[0] == 'self.valueFirstName':
                        UserPreferencesBlockEnds = 1
                    if UserPreferencesBlockEnds == 0:
                        if words[0] == 'self.StaticForwardDirection':
                            StaticDataFile.write('self.StaticForwardDirection = ' + "'" + StaticForwardDirection.get() + "'\n")
                        else:
                            StaticDataFile.write(line)
                        
                # Write Subject Data into Static Anthropometric File
                StaticDataFile.write('self.valueFirstName = ' + "'" + FirstName.get() + "'" + '\n')
                StaticDataFile.write('self.valueLastName = ' + "'" + LastName.get() + "'" + '\n')
                StaticDataFile.write('self.valuePatientNumber = ' + "'" + PatientNumber.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Day = ' + "'" + Date.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Month = ' + "'" + Month.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Year = ' + "'" + Year.get() + "'" + '\n')
                StaticDataFile.write('self.valueTrialActivity = ' + "'" + TrialActivity.get() + "'" + '\n')
                StaticDataFile.write('self.valueTrialModifier = ' + "'" + TrialModifier.get() + "'" + '\n')
                StaticDataFile.write('self.valueAssistiveDevice = ' + "'" + AssistiveDevice.get() + "'" + '\n')
                StaticDataFile.write('self.valueStaticFile = ' + "'" + StaticFile.get() + "'" + '\n')
                StaticDataFile.write('self.valueAnthropometricFile = ' + "'" + 'Static_' + TestingCondition + '_' + SubjectName  + "'" + '\n')         
                StaticDataFile.write('self.valueDataCollectionDate_Day = ' + "'" + DataCollectionDate.get() + "'" + '\n')
                StaticDataFile.write('self.valueDataCollectionDate_Month = ' + "'" + DataCollectionMonth.get() + "'" + '\n')
                StaticDataFile.write('self.valueDataCollectionDate_Year = ' + "'" + DataCollectionYear.get() + "'" + '\n')
                StaticDataFile.write('self.valueBodyMass = round(float(' + "'" + BodyMass.get() + "'),2)" + '\n')
                StaticDataFile.write('self.valueHeight = int(' + "'" + Height.get() + "')" + '\n')
                StaticDataFile.write('self.valueASISdist = int(' + "'" + ASISdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftLegLength = int(' + "'" + LeftLegLength.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightLegLength = int(' + "'" + RightLegLength.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftKneeWidth = int(' + "'" + LeftKneeWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightKneeWidth = int(' + "'" + RightKneeWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftAnkleWidth = int(' + "'" + LeftAnkleWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightAnkleWidth = int(' + "'" + RightAnkleWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftASIStoGTdist = int(' + "'" + LeftASIStoGTdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightASIStoGTdist = int(' + "'" + RightASIStoGTdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftFootModelCheck = ' + "'" + str(self.LeftFootModelCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueRightFootModelCheck = ' + "'" + str(self.RightFootModelCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueLeftHindfootVarus = ' + "'" + LeftHindfootVarus.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftCalcanealPitch = ' + "'" + LeftCalcanealPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftHindfootProgression = ' + "'" + LeftHindfootProgression.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftFirstMetatarsalPitch = ' + "'" + LeftFirstMetatarsalPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightHindfootVarus = ' + "'" + RightHindfootVarus.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightCalcanealPitch = ' + "'" + RightCalcanealPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightHindfootProgression = ' + "'" + RightHindfootProgression.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightFirstMetatarsalPitch = ' + "'" + RightFirstMetatarsalPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftPlantigradeCheck = ' + "'" + str(self.LeftPlantigradeCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueRightPlantigradeCheck = ' + "'" + str(self.RightPlantigradeCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueSujectShodCheck = ' + "'" + str(self.SubjectShodCheck.get()) + "'" + '\n')
                if str(self.SubjectShodCheck.get()) == '1':
                    StaticDataFile.write('self.valueLeftSoleThickness = int(' + "'" + LeftSoleThickness.get() + "')" + '\n')
                    StaticDataFile.write('self.valueRightSoleThickness = int(' + "'" + RightSoleThickness.get() + "')" + '\n')
                else:
                    StaticDataFile.write('self.valueLeftSoleThickness = int(' + "'" + '0' + "')" + '\n')
                    StaticDataFile.write('self.valueRightSoleThickness = int(' + "'" + '0' + "')" + '\n')
                StaticDataFile.write('self.valuePelvicFixCheck = ' + "'" + str(self.PelvicFixCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueKneeAlignmentCheck = ' + "'" + str(self.KneeAlignmentCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueStaticFrameNumber = ' + "'" + str(StaticFrameNumber.get()) + "'" + '\n')
                # If File Exists, then restore the Transformation Matrices Section
                PatientInformationBlockEnds = 0
                for line in lines:
                    words=line.split()
                    if words[0] == '#' and words[1] == 'Pelfix':
                        PatientInformationBlockEnds = 1
                    else:
                        if words[0] == '#' and words[1] == 'Transformation':
                            PatientInformationBlockEnds = 1
                    if PatientInformationBlockEnds == 1:
                        StaticDataFile.write(line)
                #print('FileUpdate- PatientInfo')
                StaticDataFile.close()
            else:
                # Open Static py file
                StaticDataFile = open(StaticDataFileName,'w+')
                # Copy User Preferences 
                UserPreferencesFile = open(UserPreferencesFileName,'r')
                lines=UserPreferencesFile.readlines()
                UserPreferencesFile.close()
                for line in lines:
                    words=line.split()
                    if words[0] == 'self.StaticForwardDirection':
                        StaticDataFile.write('self.StaticForwardDirection = ' + "'" + StaticForwardDirection.get() + "'\n")
                    else:
                        StaticDataFile.write(line)        
                # Write Subject Data into Static Anthropometric File
                StaticDataFile.write('self.valueFirstName = ' + "'" + FirstName.get() + "'" + '\n')
                StaticDataFile.write('self.valueLastName = ' + "'" + LastName.get() + "'" + '\n')
                StaticDataFile.write('self.valuePatientNumber = ' + "'" + PatientNumber.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Day = ' + "'" + Date.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Month = ' + "'" + Month.get() + "'" + '\n')
                StaticDataFile.write('self.valueDateOfBirth_Year = ' + "'" + Year.get() + "'" + '\n')
                StaticDataFile.write('self.valueTrialActivity = ' + "'" + TrialActivity.get() + "'" + '\n')
                StaticDataFile.write('self.valueTrialModifier = ' + "'" + TrialModifier.get() + "'" + '\n')
                StaticDataFile.write('self.valueAssistiveDevice = ' + "'" + AssistiveDevice.get() + "'" + '\n')
                StaticDataFile.write('self.valueStaticFile = ' + "'" + StaticFile.get() + "'" + '\n')
                StaticDataFile.write('self.valueAnthropometricFile = ' + "'" + 'Static_' + TestingCondition + '_' + SubjectName  + "'" + '\n')
                StaticDataFile.write('self.valueDataCollectionDate_Day = ' + "'" + DataCollectionDate.get() + "'" + '\n')
                StaticDataFile.write('self.valueDataCollectionDate_Month = ' + "'" + DataCollectionMonth.get() + "'" + '\n')
                StaticDataFile.write('self.valueDataCollectionDate_Year = ' + "'" + DataCollectionYear.get() + "'" + '\n')
                StaticDataFile.write('self.valueBodyMass = round(float(' + "'" + BodyMass.get() + "'),2)" + '\n')
                StaticDataFile.write('self.valueHeight = int(' + "'" + Height.get() + "')" + '\n')
                StaticDataFile.write('self.valueASISdist = int(' + "'" + ASISdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftLegLength = int(' + "'" + LeftLegLength.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightLegLength = int(' + "'" + RightLegLength.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftKneeWidth = int(' + "'" + LeftKneeWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightKneeWidth = int(' + "'" + RightKneeWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftAnkleWidth = int(' + "'" + LeftAnkleWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightAnkleWidth = int(' + "'" + RightAnkleWidth.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftASIStoGTdist = int(' + "'" + LeftASIStoGTdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueRightASIStoGTdist = int(' + "'" + RightASIStoGTdist.get() + "')" + '\n')
                StaticDataFile.write('self.valueLeftFootModelCheck = ' + "'" + str(self.LeftFootModelCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueRightFootModelCheck = ' + "'" + str(self.RightFootModelCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueLeftHindfootVarus = ' + "'" + LeftHindfootVarus.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftCalcanealPitch = ' + "'" + LeftCalcanealPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftHindfootProgression = ' + "'" + LeftHindfootProgression.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftFirstMetatarsalPitch = ' + "'" + LeftFirstMetatarsalPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightHindfootVarus = ' + "'" + RightHindfootVarus.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightCalcanealPitch = ' + "'" + RightCalcanealPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightHindfootProgression = ' + "'" + RightHindfootProgression.get() + "'" + '\n')
                StaticDataFile.write('self.valueRightFirstMetatarsalPitch = ' + "'" + RightFirstMetatarsalPitch.get() + "'" + '\n')
                StaticDataFile.write('self.valueLeftPlantigradeCheck = ' + "'" + str(self.LeftPlantigradeCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueRightPlantigradeCheck = ' + "'" + str(self.RightPlantigradeCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueSujectShodCheck = ' + "'" + str(self.SubjectShodCheck.get()) + "'" + '\n')
                if str(self.SubjectShodCheck.get()) == '1':
                    StaticDataFile.write('self.valueLeftSoleThickness = int(' + "'" + LeftSoleThickness.get() + "')" + '\n')
                    StaticDataFile.write('self.valueRightSoleThickness = int(' + "'" + RightSoleThickness.get() + "')" + '\n')
                else:
                    StaticDataFile.write('self.valueLeftSoleThickness = int(' + "'" + '0' + "')" + '\n')
                    StaticDataFile.write('self.valueRightSoleThickness = int(' + "'" + '0' + "')" + '\n')
                StaticDataFile.write('self.valuePelvicFixCheck = ' + "'" + str(self.PelvicFixCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueKneeAlignmentCheck = ' + "'" + str(self.KneeAlignmentCheck.get()) + "'" + '\n')
                StaticDataFile.write('self.valueStaticFrameNumber = ' + "'" + str(StaticFrameNumber.get()) + "'" + '\n')
                #print('File Created')
                StaticDataFile.close()  
               

class QAreport_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self,parent, width=AppWidth, height=AppHeight)
        self.parent = parent
        self.grid()
    
    def build_UI(self):            
        # Crete a Canvas to draw section on forms
        SectionCanvas = tk.Canvas(self, width=AppWidth, height=AppHeight)
        SectionCanvas.pack()

        # Proceed button chnages the form to Subject Calibration Report
        ProceedButton = tk.Button(self, text="Proceed",font=Small_Font, command = lambda: [self.parent.frames[StaticSubjectCalibrationReport_Page].tkraise(),self.parent.frames[StaticSubjectCalibrationReport_Page].build_UI()])
        ProceedButton.place(x=700,y=20,width=90,height=710)
        # Back button chnages the form display to Patient Information Page
        BackButton = tk.Button(self, text="Back",font=Small_Font, command = lambda: [self.parent.frames[PatientInfo_Page].tkraise(),self.parent.frames[PatientInfo_Page].build_UI(),ErrorMessagesLabel.place_forget(),ErrorMessagesText.place_forget()])
        BackButton.place(x=700,y=740,width=90,height=90)
        #Quit button closes app
        QuitButton = tk.Button(self,text="Quit",font=Small_Font, command = lambda: quit())
        QuitButton.place(x=700,y=840,width=90,height=90)

# =============================================================================
#       Patient Information widgets are created here
# =============================================================================
        
        #Get file path and name from Nexus
        SubjectName = vicon.GetSubjectNames()[0]
        FilePath, FileName = vicon.GetTrialName()
        
        StaticFileLabel = tk.Label(self, text="Static File-", font=Small_Font)
        StaticFileLabel.place(x=50,y=50)
        SectionCanvas.create_rectangle(195, 45, 680, 75, dash=1)
        StaticFile = tk.Label(self, text=str(FileName + '.c3d'), font=Small_Font )
        StaticFile.place(x=200,y=50)
        
        ModelLabel = tk.Label(self, text="Model-", font=Small_Font)
        ModelLabel.place(x=50,y=100)
        FilePath, FileName = vicon.GetTrialName()
        SectionCanvas.create_rectangle(195, 95, 680, 125, dash=1)
        Model = tk.Label(self, text='Shriners Gait Model', font=Small_Font )
        Model.place(x=200,y=100)
        
        UserPreferenceLabel = tk.Label(self,text='User Preference', font=Small_Font)
        UserPreferenceLabel.place(x=50,y=150)
        SectionCanvas.create_rectangle(195, 145, 680, 175, dash=1)
        UserPreference = tk.Label(self, text=UserPreferencesFileName, font=Smaller_Font, anchor='w' )
        UserPreference.place(x=200,y=150,width=470)
        
        #Create Error Label but place them only if error occurs
        ErrorMessagesLabel = tk.Label(self,text='Warnings', font=Bold_Small_Font)
        ErrorMessagesText = tk.Text(self)
        ErrorMessagesLabel['fg']='red'
        ErrorMessagesText['fg']='red'
        #ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
        #ErrorMessagesText.place(x=195,y=95,width=490,height=85)
        
# =============================================================================
#       Clinical Exam - Marker Data Section widgets are created here 
# =============================================================================
        SectionCanvas.create_rectangle(20, 220, 680, 440)
        
        ClinicalExamMarkerDataTitle = tk.Label(self, text="Clinical Exam - Marker Data", font=Large_Font)
        ClinicalExamMarkerDataTitle.place(x=50,y=200)
        
        ClinicalLabel = tk.Label(self, text='Clinical', font=Small_Font)
        ClinicalLabel.place(x=285,y=230)
        MarkersLabel = tk.Label(self, text='Markers', font=Small_Font)
        MarkersLabel.place(x=385,y=230)
        DifferenceLabel = tk.Label(self, text='Difference', font=Small_Font)
        DifferenceLabel.place(x=500,y=230)
        
        
        ASISdistLabel = tk.Label(self, text='ASIS-to-ASIS Distance (mm)', font=Small_Font)
        ASISdistLabel.place(x=50,y=265)
        ASISdistClinical = tk.Label(self, text='-', font=Small_Font)
        ASISdistClinical.place(x=300,y=265)
        ASISdistMarkers = tk.Label(self, text='-', font=Small_Font)
        ASISdistMarkers.place(x=400,y=265)
        ASISdistDiff = tk.Entry(self,justify='center')
        ASISdistDiff.place(x=500,y=265,width=80,height=20)
        
        
        LeftKneeWidthLabel = tk.Label(self, text='Knee Width (mm)- Left', font=Small_Font)
        LeftKneeWidthLabel.place(x=50,y=300)
        LeftKneeWidthClinical = tk.Label(self, text='-', font=Small_Font)
        LeftKneeWidthClinical.place(x=300,y=300)
        LeftKneeWidthMarkers = tk.Label(self, text='-', font=Small_Font)
        LeftKneeWidthMarkers.place(x=400,y=300)
        LeftKneeWidthDiff = tk.Entry(self,justify='center')
        LeftKneeWidthDiff.place(x=500,y=300,width=80,height=20)
        
        RightKneeWidthLabel = tk.Label(self, text='Knee Width (mm)- Right', font=Small_Font)
        RightKneeWidthLabel.place(x=50,y=335)
        RightKneeWidthClinical = tk.Label(self, text='-', font=Small_Font)
        RightKneeWidthClinical.place(x=300,y=335)
        RightKneeWidthMarkers = tk.Label(self, text='-', font=Small_Font)
        RightKneeWidthMarkers.place(x=400,y=335)
        RightKneeWidthDiff = tk.Entry(self,justify='center')
        RightKneeWidthDiff.place(x=500,y=335,width=80,height=20)
        
        
        LeftAnkleWidthLabel = tk.Label(self, text='Ankle Width (mm)- Left', font=Small_Font)
        LeftAnkleWidthLabel.place(x=50,y=370)
        LeftAnkleWidthClinical = tk.Label(self, text='-', font=Small_Font)
        LeftAnkleWidthClinical.place(x=300,y=370)
        LeftAnkleWidthMarkers = tk.Label(self, text='-', font=Small_Font)
        LeftAnkleWidthMarkers.place(x=400,y=370)
        LeftAnkleWidthDiff = tk.Entry(self,justify='center')
        LeftAnkleWidthDiff.place(x=500,y=370,width=80,height=20)
        
        RightAnkleWidthLabel = tk.Label(self, text='Ankle Width (mm)- Right', font=Small_Font)
        RightAnkleWidthLabel.place(x=50,y=405)
        RightAnkleWidthClinical = tk.Label(self, text='-', font=Small_Font)
        RightAnkleWidthClinical.place(x=300,y=405)
        RightAnkleWidthMarkers = tk.Label(self, text='-', font=Small_Font)
        RightAnkleWidthMarkers.place(x=400,y=405)
        RightAnkleWidthDiff = tk.Entry(self,justify='center')
        RightAnkleWidthDiff.place(x=500,y=405,width=80,height=20)
        
# =============================================================================
#       KAD QA form widgets are created here
# =============================================================================
        SectionCanvas.create_rectangle(20, 485, 680, 930)
        
        ClinicalExamMarkerDataTitle = tk.Label(self, text="Knee Alignment Fixture Marker Data", font=Large_Font)
        ClinicalExamMarkerDataTitle.place(x=50,y=470)
        InterMarkersDistLabel = tk.Label(self, text='Inter Markers Distance (mm)', font=Bold_Small_Font)
        InterMarkersDistLabel.place(x=30,y=510)
        
        LeftLabel = tk.Label(self, text='Left', font=Small_Font)
        LeftLabel.place(x=300, y=540)
        LeftRangeLabel = tk.Label(self, text='Range', font=Small_Font)
        LeftRangeLabel.place(x=365, y=540)
        RightLabel = tk.Label(self, text='Right', font=Small_Font)
        RightLabel.place(x=500, y=540)
        RightRangeLabel = tk.Label(self, text='Range', font=Small_Font)
        RightRangeLabel.place(x=565, y=540)
        
        UpperLateralLabel = tk.Label(self, text='Upper & Lateral Marker', font=Small_Font)
        UpperLateralLabel.place(x=100,y=580)
        LeftUpperLateral = tk.Label(self, text='-', font=Small_Font)
        LeftUpperLateral.place(x=300,y=580)
        RightUpperLateral = tk.Label(self, text='-', font=Small_Font)
        RightUpperLateral.place(x=500,y=580)
        
        UpperLowerLabel = tk.Label(self, text='Upper & Lower Marker', font=Small_Font)
        UpperLowerLabel.place(x=100,y=620)
        LeftUpperLower = tk.Label(self, text='-', font=Small_Font)
        LeftUpperLower.place(x=300,y=620)
        RightUpperLower = tk.Label(self, text='-', font=Small_Font)
        RightUpperLower.place(x=500,y=620)
        
        LateralLowerLabel = tk.Label(self, text='Lateral & Lower Marker', font=Small_Font)
        LateralLowerLabel.place(x=100,y=660)
        LeftLateralLower = tk.Label(self, text='-', font=Small_Font)
        LeftLateralLower.place(x=300,y=660)
        RightLateralLower = tk.Label(self, text='-', font=Small_Font)
        RightLateralLower.place(x=500,y=660)
        
        LeftDistRange = tk.Entry(self, justify='center')
        LeftDistRange.place(x=370,y=620,width=40,height=20)
        RightDistRange = tk.Entry(self, justify='center')
        RightDistRange.place(x=570,y=620,width=40,height=20)

        InterMarkersAngleLabel = tk.Label(self, text='Inter Markers Angles (deg)', font=Bold_Small_Font)
        InterMarkersAngleLabel.place(x=30,y=720)
        
        UpperLateralLowerLabel = tk.Label(self, text='Upper-Lateral-Lower', font=Small_Font)
        UpperLateralLowerLabel.place(x=100,y=770)
        LeftUpperLateralLower = tk.Label(self, text='-', font=Small_Font)
        LeftUpperLateralLower.place(x=300,y=770)
        RightUpperLateralLower = tk.Label(self, text='-', font=Small_Font)
        RightUpperLateralLower.place(x=500,y=770)
        
        LateralUpperLowerLabel = tk.Label(self, text='Lateral-Upper-Lower', font=Small_Font)
        LateralUpperLowerLabel.place(x=100,y=810)
        LeftLateralUpperLower = tk.Label(self, text='-', font=Small_Font)
        LeftLateralUpperLower.place(x=300,y=810)
        RightLateralUpperLower = tk.Label(self, text='-', font=Small_Font)
        RightLateralUpperLower.place(x=500,y=810)
        
        UpperLowerLateralLabel = tk.Label(self, text='Upper-Lower-Lateral', font=Small_Font)
        UpperLowerLateralLabel.place(x=100,y=850)
        LeftUpperLowerLateral = tk.Label(self, text='-', font=Small_Font)
        LeftUpperLowerLateral.place(x=300,y=850)
        RightUpperLowerLateral = tk.Label(self, text='-', font=Small_Font)
        RightUpperLowerLateral.place(x=500,y=850)
        
        LeftAngleRange = tk.Entry(self, justify='center')
        LeftAngleRange.place(x=370,y=810,width=40,height=20)
        RightAngleRange = tk.Entry(self, justify='center')
        RightAngleRange.place(x=570,y=810,width=40,height=20)
        
# =============================================================================
#       Compute QA based on Clinical Measures and Marker Data  
# =============================================================================
        # Extract Clinical Values
        exec(open(StaticDataFileName).read())
        #Extract Nexus first frame
        StartFrame, EndFrame = vicon.GetTrialRegionOfInterest()

        
        # =============================================================================
        #         Read Marker data from Start Frame (First Frame) for Static Check
        #         Dispplay Warning if marker not found
        # =============================================================================
       
        # Function to extract markerdata and check if data exists
        def MarkerCheck(Subject, MarkerName, FirstFrame):
            # Check if marker exists at all
            if vicon.HasTrajectory(Subject,MarkerName) is True:
                MarkerData = np.array(vicon.GetTrajectoryAtFrame(Subject, MarkerName, FirstFrame )[0:3])
                # Check if marker is labeled at the first frame
                if MarkerData[0] == 0 or MarkerData[1] == 0 or MarkerData[2] == 0:
                    ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                    ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                    ErrorMessage = 'Marker ' + MarkerName + ' is not labeled at frame ' + str(FirstFrame) + '\n'
                    ErrorMessagesText.insert(tk.END,ErrorMessage)
            else:
                MarkerData = np.array([0.,0.,0.])
                # Dont show error for Trunk Markers
                ExcludedForErrorMarkerNames = [self.C7MarkerName, self.LeftClavicleMarkerName, self.RightClavicleMarkerName]
                if not MarkerName in ExcludedForErrorMarkerNames: 
                    ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                    ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                    ErrorMessage = 'Marker ' + MarkerName + ' is not Found ' + '\n'
                    ErrorMessagesText.insert(tk.END,ErrorMessage)
            return MarkerData    

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
                ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                ErrorMessage = 'Marker ' + MarkerName + ' is not Found ' + '\n'
                ErrorMessagesText.insert(tk.END,ErrorMessage)
            return MarkerDataX, MarkerDataY, MarkerDataZ, MarkerDataExists
# =============================================================================
#       If Pelvic Fix Option used then compute ASIS markers  
# =============================================================================
        if not self.valuePelvicFixCheck == '0': # Pelfix Option is Used
            if self.valuePelvicFixCheck == '1':
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
            
            if self.valuePelvicFixCheck == '2':
                LeftPSISMarkerX, LeftPSISMarkerY, LeftPSISMarkerZ, LeftPSISMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPSISMarkerName)
                RightPSISMarkerX, RightPSISMarkerY, RightPSISMarkerZ, RightPSISMarkerExists = MarkerArrayCheck(SubjectName, self.RightPSISMarkerName)
                SacralTriadMarkerX, SacralTriadMarkerY, SacralTriadMarkerZ, SacralTriadMarkerExists = MarkerArrayCheck(SubjectName, self.SacralTriadMarkerName)
                        
            
            DefaultStaticDataFileName = FilePath + 'Static_' + DefaultTestingCondition + '_' + SubjectName + '.py'
            if os.path.exists(DefaultStaticDataFileName) and vicon.HasTrajectory(SubjectName, self.PointerTipMarkerName) is False and vicon.HasTrajectory(SubjectName, self.PointerTailMarkerName) is False:
                # =============================================================================
                #       AFO Condition Check- Read Pelfix Information from Barefoot Trials 
                # =============================================================================
                f=open(DefaultStaticDataFileName,'r')
                lines=f.readlines() #read all lines
                TempPelfixFileName = 'C:\Python27\Pelfix.py'
                TempPelfixFile = open(TempPelfixFileName,'w+')
                for line in lines:
                    words=line.split()
                    if words[0] == 'self.valueLeftASISMarkerPelvis' or words[0] == 'self.valueRightASISMarkerPelvis':
                        TempPelfixFile.write(line)
                TempPelfixFile.close()
                exec(open(TempPelfixFileName).read())
                try:
                    os.remove('C:\Python27\Pelfix.py')
                    os.remove('C:\Python27\Pelfix.pyc')
                except:
                    pass
                LeftASISMarkerPelvis = self.valueLeftASISMarkerPelvis
                RightASISMarkerPelvis = self.valueRightASISMarkerPelvis
            else:
                # Compute Max and Min Pointer Disance
                PointerTipMarkerX, PointerTipMarkerY, PointerTipMarkerZ, PointerTipMarkerExists = MarkerArrayCheck(SubjectName, self.PointerTipMarkerName)
                PointerTailMarkerX, PointerTailMarkerY, PointerTailMarkerZ, PointerTailMarkerExists = MarkerArrayCheck(SubjectName, self.PointerTailMarkerName)
                
                MinPointerDist = 1000
                MaxPointerDist = -1000
                framecount = vicon.GetFrameCount()
                for FrameNumber in range(StartFrame,EndFrame):
                    PointerTipMarker = np.array([PointerTipMarkerX[FrameNumber], PointerTipMarkerY[FrameNumber], PointerTipMarkerZ[FrameNumber]])
                    PointerTailMarker = np.array([PointerTailMarkerX[FrameNumber], PointerTailMarkerY[FrameNumber], PointerTailMarkerZ[FrameNumber]])
                    if PointerTipMarkerExists[FrameNumber] is True and PointerTailMarkerExists[FrameNumber] is True:
                        PointerDist = round(np.linalg.norm(PointerTipMarker - PointerTailMarker),0)
                        if PointerDist > MaxPointerDist:
                            MaxPointerDist = PointerDist
                        if PointerDist < MinPointerDist:
                            MinPointerDist = PointerDist
    
                # Compute Threshold Distance for Pointer Press
                Threshold_Distance = round((MaxPointerDist + MinPointerDist) / 2 , 0)
                #print(Threshold_Distance)
                
                # Compute Frames when Pointer was pressed
                FrameA = 0 #First Press Frame
                FrameB = 0 #Second Press Frame
                FrameX = 0 #Frame when First Press is released
                for FrameNumber in range(StartFrame,EndFrame):
                    PointerTipMarker = np.array([PointerTipMarkerX[FrameNumber], PointerTipMarkerY[FrameNumber], PointerTipMarkerZ[FrameNumber]])
                    PointerTailMarker = np.array([PointerTailMarkerX[FrameNumber], PointerTailMarkerY[FrameNumber], PointerTailMarkerZ[FrameNumber]])
                    PointerDist = round(np.linalg.norm(PointerTipMarker - PointerTailMarker),0)
                    #print(PointerDist)
                    if PointerDist < Threshold_Distance and FrameA == 0:
                        FrameA = FrameNumber
                    if PointerDist > Threshold_Distance and FrameA != 0 and FrameX == 0:
                        FrameX = FrameNumber
                    if PointerDist < Threshold_Distance and FrameA != 0 and FrameX != 0 and FrameB == 0:
                        FrameB = FrameNumber
                #print(FrameA,FrameB)       
    
                
                for FrameNumber in (FrameA,FrameB):
                    if self.valuePelvicFixCheck == '1':#Iliac Markers Option
                        # Pelvis Technical coordinate system based on LILC, RILC, SACR
                        LeftIliacMarker = np.array([LeftIliacMarkerX[FrameNumber], LeftIliacMarkerY[FrameNumber], LeftIliacMarkerZ[FrameNumber]])
                        RightIliacMarker = np.array([RightIliacMarkerX[FrameNumber], RightIliacMarkerY[FrameNumber], RightIliacMarkerZ[FrameNumber]])
                        SacralMarker = np.array([SacralMarkerX[FrameNumber], SacralMarkerY[FrameNumber], SacralMarkerZ[FrameNumber]])
                        [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftIliacMarker, RightIliacMarker, SacralMarker)
                        
                        PointerTipMarker = np.array([PointerTipMarkerX[FrameNumber], PointerTipMarkerY[FrameNumber], PointerTipMarkerZ[FrameNumber]])
                        PointerTailMarker = np.array([PointerTailMarkerX[FrameNumber], PointerTailMarkerY[FrameNumber], PointerTailMarkerZ[FrameNumber]])
                        Pointer_UnitVector = math.ComputeUnitVecFromPts(PointerTailMarker, PointerTipMarker)
                        
                        valueASISMarkerLab = np.array([0.,0.,0.])
                        valueASISMarkerLab = PointerTipMarker + Pointer_UnitVector * float(self.PointerMarkerTipDistance)
                        
                        #Transform ASIS Marker in Pelvic Technical Coordinate System
                        valueASISMarkerPelvis =  math.TransformPointIntoMovingCoors(valueASISMarkerLab, EPelvisTech, MidASISLab)
                        
                    
                    if self.valuePelvicFixCheck == '2': # Pelvic Triad Option
                        # Pelvis Technical coordinate system based on LPSI, RPSI, SACT
                        LeftPSISMarker = np.array([LeftPSISMarkerX[FrameNumber], LeftPSISMarkerY[FrameNumber], LeftPSISMarkerZ[FrameNumber]])
                        RightPSISMarker = np.array([RightPSISMarkerX[FrameNumber], RightPSISMarkerY[FrameNumber], RightPSISMarkerZ[FrameNumber]])
                        SacralTriadMarker = np.array([SacralTriadMarkerX[FrameNumber], SacralTriadMarkerY[FrameNumber], SacralTriadMarkerZ[FrameNumber]])
                        SacralMarker = (LeftPSISMarker  + RightPSISMarker) / 2
                        [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftPSISMarker, RightPSISMarker, SacralTriadMarker)
                        
                        PointerTipMarker = np.array([PointerTipMarkerX[FrameNumber], PointerTipMarkerY[FrameNumber], PointerTipMarkerZ[FrameNumber]])
                        PointerTailMarker = np.array([PointerTailMarkerX[FrameNumber], PointerTailMarkerY[FrameNumber], PointerTailMarkerZ[FrameNumber]])
                        Pointer_UnitVector = math.ComputeUnitVecFromPts(PointerTailMarker, PointerTipMarker)
                        
                        valueASISMarkerLab = np.array([0.,0.,0.])
                        valueASISMarkerLab = PointerTipMarker + Pointer_UnitVector * float(self.PointerMarkerTipDistance)
                        
                        #Transform ASIS Marker in Pelvic Technical Coordinate System
                        valueASISMarkerPelvis =  math.TransformPointIntoMovingCoors(valueASISMarkerLab, EPelvisTech, MidASISLab)

                        
                    if FrameNumber == FrameA:
                        valueASISMarkerPelvis_FrameA = valueASISMarkerPelvis
                        SACRtoASIS_FrameA = math.ComputeUnitVecFromPts(SacralMarker, valueASISMarkerLab)
                    else:
                        valueASISMarkerPelvis_FrameB = valueASISMarkerPelvis
                        SACRtoASIS_FrameB = math.ComputeUnitVecFromPts(SacralMarker, valueASISMarkerLab)
                    
                # Determine which ASIS is being identified by Pointer and save to C3D
                CrossVector = np.cross(SACRtoASIS_FrameA, SACRtoASIS_FrameB)
                if CrossVector[2] > 0:     
                    RightASISMarkerPelvis = valueASISMarkerPelvis_FrameA
                    LeftASISMarkerPelvis = valueASISMarkerPelvis_FrameB
                else:
                    RightASISMarkerPelvis = valueASISMarkerPelvis_FrameB
                    LeftASISMarkerPelvis = valueASISMarkerPelvis_FrameA
            
            
            #Write Marker into C3D
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
                    
                LeftASISMarkerLab = math.TransformPointIntoLabCoors(LeftASISMarkerPelvis,EPelvisTech, MidASISLab)
                RightASISMarkerLab = math.TransformPointIntoLabCoors(RightASISMarkerPelvis,EPelvisTech, MidASISLab)
                arrayLASISMarkerX[FrameNumber] = LeftASISMarkerLab[0]
                arrayLASISMarkerY[FrameNumber] = LeftASISMarkerLab[1]
                arrayLASISMarkerZ[FrameNumber] = LeftASISMarkerLab[2]
                arrayRASISMarkerX[FrameNumber] = RightASISMarkerLab[0]
                arrayRASISMarkerY[FrameNumber] = RightASISMarkerLab[1]
                arrayRASISMarkerZ[FrameNumber] = RightASISMarkerLab[2]
                    
            vicon.SetTrajectory(SubjectName, self.LeftASISMarkerName, arrayLASISMarkerX, arrayLASISMarkerY, arrayLASISMarkerZ, exists )
            vicon.SetTrajectory(SubjectName, self.RightASISMarkerName, arrayRASISMarkerX, arrayRASISMarkerY, arrayRASISMarkerZ, exists )
            
 # =============================================================================           
        
 # =============================================================================
 #       If FootModel is used then write HEEL and TOE markers   
 # =============================================================================
        
        if vicon.HasTrajectory(SubjectName,self.LeftToeMarkerName) is False:
            if vicon.HasTrajectory(SubjectName,self.Left23MetatarsalHeadMarkerName) is True:
                arrayLeft23MetatarsalHeadMarkerX, arrayLeft23MetatarsalHeadMarkerY, arrayLeft23MetatarsalHeadMarkerZ, arrayLeft23MetatarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.Left23MetatarsalHeadMarkerName)
                vicon.SetTrajectory(SubjectName, self.LeftToeMarkerName, arrayLeft23MetatarsalHeadMarkerX, arrayLeft23MetatarsalHeadMarkerY, arrayLeft23MetatarsalHeadMarkerZ, arrayLeft23MetatarsalHeadMarkerExists)
            else:
                if os.path.exists(SittingFootStaticDataFileName):
                    exec(open(SittingFootStaticDataFileName).read())
                    LeftFirstMetarsalBaseMarkerX, LeftFirstMetarsalBaseMarkerY, LeftFirstMetarsalBaseMarkerZ, LeftFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalBaseMarkerName)
                    LeftFirstMetarsalHeadMarkerX, LeftFirstMetarsalHeadMarkerY, LeftFirstMetarsalHeadMarkerZ, LeftFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFirstMetarsalHeadMarkerName)
                    LeftFifthMetarsalHeadMarkerX, LeftFifthMetarsalHeadMarkerY, LeftFifthMetarsalHeadMarkerZ, LeftFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.LeftFifthMetarsalHeadMarkerName)
                    #Compute markers for each frame            
                    framecount = vicon.GetFrameCount()
                    arrayLMT23HMarkerX= [0 for m in range(framecount)] 
                    arrayLMT23HMarkerY= [0 for m in range(framecount)] 
                    arrayLMT23HMarkerZ= [0 for m in range(framecount)] 
                    exists = [True]*framecount
                    for FrameNumber in range(StartFrame-1,EndFrame):    
                        # Compute Technical Coordinate System: Left Foot Segments
                        LeftFirstMetarsalBaseMarker = np.array([LeftFirstMetarsalBaseMarkerX[FrameNumber], LeftFirstMetarsalBaseMarkerY[FrameNumber], LeftFirstMetarsalBaseMarkerZ[FrameNumber]])
                        LeftFirstMetarsalHeadMarker = np.array([LeftFirstMetarsalHeadMarkerX[FrameNumber], LeftFirstMetarsalHeadMarkerY[FrameNumber], LeftFirstMetarsalHeadMarkerZ[FrameNumber]])
                        LeftFifthMetarsalHeadMarker = np.array([LeftFifthMetarsalHeadMarkerX[FrameNumber], LeftFifthMetarsalHeadMarkerY[FrameNumber], LeftFifthMetarsalHeadMarkerZ[FrameNumber]])
                        LeftEForefootTech = gait.TechCS_Forefoot_mSHCG('Left', LeftFirstMetarsalBaseMarker, LeftFirstMetarsalHeadMarker, LeftFifthMetarsalHeadMarker)
                        LeftMT23HMarkerLab = math.TransformPointIntoLabCoors(self.valueLeft23MetatarsalHeadMarkerForefoot,LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                        arrayLMT23HMarkerX[FrameNumber] = LeftMT23HMarkerLab[0]
                        arrayLMT23HMarkerY[FrameNumber] = LeftMT23HMarkerLab[1]
                        arrayLMT23HMarkerZ[FrameNumber] = LeftMT23HMarkerLab[2]
                    vicon.SetTrajectory(SubjectName, self.LeftToeMarkerName, arrayLMT23HMarkerX, arrayLMT23HMarkerY, arrayLMT23HMarkerZ, exists)
                    
        if vicon.HasTrajectory(SubjectName,self.LeftHeelMarkerName) is False and vicon.HasTrajectory(SubjectName,self.LeftPosteriorCalcaneusMarkerName) is True:
            arrayLeftPosteriorCalcaneusMarkerX, arrayLeftPosteriorCalcaneusMarkerY, arrayLeftPosteriorCalcaneusMarkerZ, arrayLeftPosteriorCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.LeftPosteriorCalcaneusMarkerName)
            vicon.SetTrajectory(SubjectName, self.LeftHeelMarkerName, arrayLeftPosteriorCalcaneusMarkerX, arrayLeftPosteriorCalcaneusMarkerY, arrayLeftPosteriorCalcaneusMarkerZ, arrayLeftPosteriorCalcaneusMarkerExists)
        if vicon.HasTrajectory(SubjectName,self.RightToeMarkerName) is False:
            if vicon.HasTrajectory(SubjectName,self.Right23MetatarsalHeadMarkerName) is True:
                arrayRight23MetatarsalHeadMarkerX, arrayRight23MetatarsalHeadMarkerY, arrayRight23MetatarsalHeadMarkerZ, arrayRight23MetatarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.Right23MetatarsalHeadMarkerName)
                vicon.SetTrajectory(SubjectName, self.RightToeMarkerName, arrayRight23MetatarsalHeadMarkerX, arrayRight23MetatarsalHeadMarkerY, arrayRight23MetatarsalHeadMarkerZ, arrayRight23MetatarsalHeadMarkerExists)
            else:
                if os.path.exists(SittingFootStaticDataFileName):
                    exec(open(SittingFootStaticDataFileName).read())
                    RightFirstMetarsalBaseMarkerX, RightFirstMetarsalBaseMarkerY, RightFirstMetarsalBaseMarkerZ, RightFirstMetarsalBaseMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalBaseMarkerName)
                    RightFirstMetarsalHeadMarkerX, RightFirstMetarsalHeadMarkerY, RightFirstMetarsalHeadMarkerZ, RightFirstMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFirstMetarsalHeadMarkerName)
                    RightFifthMetarsalHeadMarkerX, RightFifthMetarsalHeadMarkerY, RightFifthMetarsalHeadMarkerZ, RightFifthMetarsalHeadMarkerExists = MarkerArrayCheck(SubjectName, self.RightFifthMetarsalHeadMarkerName)
                    #Compute markers for each frame            
                    framecount = vicon.GetFrameCount()
                    arrayRMT23HMarkerX= [0 for m in range(framecount)] 
                    arrayRMT23HMarkerY= [0 for m in range(framecount)] 
                    arrayRMT23HMarkerZ= [0 for m in range(framecount)] 
                    exists = [True]*framecount
                    for FrameNumber in range(StartFrame-1,EndFrame):    
                        # Compute Technical Coordinate System: Right Foot Segments
                        RightFirstMetarsalBaseMarker = np.array([RightFirstMetarsalBaseMarkerX[FrameNumber], RightFirstMetarsalBaseMarkerY[FrameNumber], RightFirstMetarsalBaseMarkerZ[FrameNumber]])
                        RightFirstMetarsalHeadMarker = np.array([RightFirstMetarsalHeadMarkerX[FrameNumber], RightFirstMetarsalHeadMarkerY[FrameNumber], RightFirstMetarsalHeadMarkerZ[FrameNumber]])
                        RightFifthMetarsalHeadMarker = np.array([RightFifthMetarsalHeadMarkerX[FrameNumber], RightFifthMetarsalHeadMarkerY[FrameNumber], RightFifthMetarsalHeadMarkerZ[FrameNumber]])
                        RightEForefootTech = gait.TechCS_Forefoot_mSHCG('Right', RightFirstMetarsalBaseMarker, RightFirstMetarsalHeadMarker, RightFifthMetarsalHeadMarker)
                        RightMT23HMarkerLab = math.TransformPointIntoLabCoors(self.valueRight23MetatarsalHeadMarkerForefoot,RightEForefootTech, RightFirstMetarsalBaseMarker)
                        arrayRMT23HMarkerX[FrameNumber] = RightMT23HMarkerLab[0]
                        arrayRMT23HMarkerY[FrameNumber] = RightMT23HMarkerLab[1]
                        arrayRMT23HMarkerZ[FrameNumber] = RightMT23HMarkerLab[2]
                    vicon.SetTrajectory(SubjectName, self.RightToeMarkerName, arrayRMT23HMarkerX, arrayRMT23HMarkerY, arrayRMT23HMarkerZ, exists)
                    
        if vicon.HasTrajectory(SubjectName,self.RightHeelMarkerName) is False and vicon.HasTrajectory(SubjectName,self.RightPosteriorCalcaneusMarkerName) is True:
            arrayRightPosteriorCalcaneusMarkerX, arrayRightPosteriorCalcaneusMarkerY, arrayRightPosteriorCalcaneusMarkerZ, arrayRightPosteriorCalcaneusMarkerExists = MarkerArrayCheck(SubjectName, self.RightPosteriorCalcaneusMarkerName)
            vicon.SetTrajectory(SubjectName, self.RightHeelMarkerName, arrayRightPosteriorCalcaneusMarkerX, arrayRightPosteriorCalcaneusMarkerY, arrayRightPosteriorCalcaneusMarkerZ, arrayRightPosteriorCalcaneusMarkerExists)
           
# ============================================================================= 
        LeftASISMarker = MarkerCheck(SubjectName,self.LeftASISMarkerName,int(self.valueStaticFrameNumber))  
        LeftLateralAnkleMarker = MarkerCheck(SubjectName,self.LeftLateralAnkleMarkerName,int(self.valueStaticFrameNumber))   
        LeftMedialAnkleMarker = MarkerCheck(SubjectName,self.LeftMedialAnkleMarkerName,int(self.valueStaticFrameNumber))   
        if self.valueKneeAlignmentCheck == '0':
            LeftLateralKADMarker = MarkerCheck(SubjectName,self.LeftLateralKADMarkerName,int(self.valueStaticFrameNumber))   
            LeftUpperKADMarker = MarkerCheck(SubjectName,self.LeftUpperKADMarkerName,int(self.valueStaticFrameNumber))  
            LeftLowerKADMarker = MarkerCheck(SubjectName,self.LeftLowerKADMarkerName,int(self.valueStaticFrameNumber)) 
        else:
            LeftLateralKneeMarker = MarkerCheck(SubjectName,self.LeftLateralKneeMarkerName,int(self.valueStaticFrameNumber))   
            LeftMedialKneeMarker = MarkerCheck(SubjectName,self.LeftMedialKneeMarkerName,int(self.valueStaticFrameNumber))   
        
        
        RightASISMarker = MarkerCheck(SubjectName,self.RightASISMarkerName,int(self.valueStaticFrameNumber))    
        RightLateralAnkleMarker = MarkerCheck(SubjectName,self.RightLateralAnkleMarkerName,int(self.valueStaticFrameNumber))   
        RightMedialAnkleMarker = MarkerCheck(SubjectName,self.RightMedialAnkleMarkerName,int(self.valueStaticFrameNumber))   
        if self.valueKneeAlignmentCheck == '0':
            RightLateralKADMarker = MarkerCheck(SubjectName,self.RightLateralKADMarkerName,int(self.valueStaticFrameNumber))   
            RightUpperKADMarker = MarkerCheck(SubjectName,self.RightUpperKADMarkerName,int(self.valueStaticFrameNumber))   
            RightLowerKADMarker = MarkerCheck(SubjectName,self.RightLowerKADMarkerName,int(self.valueStaticFrameNumber))  
        else:
            RightLateralKneeMarker = MarkerCheck(SubjectName,self.RightLateralKneeMarkerName,int(self.valueStaticFrameNumber))   
            RightMedialKneeMarker = MarkerCheck(SubjectName,self.RightMedialKneeMarkerName,int(self.valueStaticFrameNumber))   
            
        
        if self.valueKneeAlignmentCheck == '0':
            # Check of Upper/Lower KAD Marker labeling
            if LeftLowerKADMarker[2] > LeftUpperKADMarker[2]:
                ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                ErrorMessage = 'Markers on the Left KAD do not appear to be properly labeled' + '\n'
                ErrorMessagesText.insert(tk.END,ErrorMessage)
            if RightLowerKADMarker[2] > RightUpperKADMarker[2]:
                ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                ErrorMessage = 'Markers on the Right KAD do not appear to be properly labeled' + '\n'
                ErrorMessagesText.insert(tk.END,ErrorMessage)
            # =============================================================================

        
                        
        ASISdistClinical['text']=str(self.valueASISdist)
        if vicon.HasTrajectory(SubjectName,self.LeftASISMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightASISMarkerName) is True:
            valueASISdistMarkers=np.linalg.norm(LeftASISMarker-RightASISMarker)
            ASISdistMarkers['text']=int(round(valueASISdistMarkers))
            ASISdistDiff.insert(0,int(round(abs(valueASISdistMarkers-self.valueASISdist))))
        
        LeftKneeWidthClinical['text']=str(self.valueLeftKneeWidth)
        if self.valueKneeAlignmentCheck == '1':
            valueLeftKneeWidthMarkers=np.linalg.norm(LeftLateralKneeMarker-LeftMedialKneeMarker)-self.MarkerDiameter
            LeftKneeWidthMarkers['text']=int(round(valueLeftKneeWidthMarkers))
            LeftKneeWidthDiff.insert(0,int(round(abs(valueLeftKneeWidthMarkers-self.valueLeftKneeWidth))))
        
        RightKneeWidthClinical['text']=str(self.valueRightKneeWidth)
        if self.valueKneeAlignmentCheck == '1':
            valueRightKneeWidthMarkers=np.linalg.norm(RightLateralKneeMarker-RightMedialKneeMarker)-self.MarkerDiameter
            RightKneeWidthMarkers['text']=int(round(valueRightKneeWidthMarkers))
            RightKneeWidthDiff.insert(0,int(round(abs(valueRightKneeWidthMarkers-self.valueRightKneeWidth))))
        

        LeftAnkleWidthClinical['text']=str(self.valueLeftAnkleWidth)
        if vicon.HasTrajectory(SubjectName,self.LeftLateralAnkleMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftMedialAnkleMarkerName) is True:
            valueLeftAnkleWidthMarkers=np.linalg.norm(LeftLateralAnkleMarker-LeftMedialAnkleMarker)-self.MarkerDiameter
            LeftAnkleWidthMarkers['text']=int(round(valueLeftAnkleWidthMarkers))
            LeftAnkleWidthDiff.insert(0,int(round(abs(valueLeftAnkleWidthMarkers-self.valueLeftAnkleWidth))))

        RightAnkleWidthClinical['text']=str(self.valueRightAnkleWidth)
        if vicon.HasTrajectory(SubjectName,self.RightLateralAnkleMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightMedialAnkleMarkerName) is True:
            valueRightAnkleWidthMarkers=np.linalg.norm(RightLateralAnkleMarker-RightMedialAnkleMarker)-self.MarkerDiameter
            RightAnkleWidthMarkers['text']=int(round(valueRightAnkleWidthMarkers))
            RightAnkleWidthDiff.insert(0,int(round(abs(valueRightAnkleWidthMarkers-self.valueRightAnkleWidth))))
        
        if vicon.HasTrajectory(SubjectName,self.LeftLateralKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftUpperKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftLowerKADMarkerName) is True:
            # Distances
            valueLeftUpperLateral = np.linalg.norm(LeftUpperKADMarker-LeftLateralKADMarker)
            valueLeftUpperLower = np.linalg.norm(LeftUpperKADMarker-LeftLowerKADMarker)
            valueLeftLateralLower = np.linalg.norm(LeftLateralKADMarker-LeftLowerKADMarker)
            LeftUpperLateral['text'] = int(round(valueLeftUpperLateral))
            LeftUpperLower['text'] = int(round(valueLeftUpperLower))
            LeftLateralLower['text'] = int(round(valueLeftLateralLower))
            LeftDistRange.insert(0,int(round(max(valueLeftUpperLateral,valueLeftUpperLower,valueLeftLateralLower)-min(valueLeftUpperLateral,valueLeftUpperLower,valueLeftLateralLower))))
            # Angles
            valueLeftUpperLateralLower = math.Compute3DAngle(LeftUpperKADMarker,LeftLateralKADMarker,LeftLowerKADMarker) * 180 / np.pi
            valueLeftLateralUpperLower = math.Compute3DAngle(LeftLateralKADMarker,LeftUpperKADMarker,LeftLowerKADMarker) * 180 / np.pi
            valueLeftUpperLowerLateral = math.Compute3DAngle(LeftUpperKADMarker,LeftLowerKADMarker,LeftLateralKADMarker) * 180 / np.pi
            LeftUpperLateralLower['text'] = int(round(valueLeftUpperLateralLower))
            LeftLateralUpperLower['text'] = int(round(valueLeftLateralUpperLower))
            LeftUpperLowerLateral['text'] = int(round(valueLeftUpperLowerLateral))
            LeftAngleRange.insert(0,int(round(max(valueLeftUpperLateralLower,valueLeftLateralUpperLower,valueLeftUpperLowerLateral)-min(valueLeftUpperLateralLower,valueLeftLateralUpperLower,valueLeftUpperLowerLateral))))

        if vicon.HasTrajectory(SubjectName,self.RightLateralKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightUpperKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightLowerKADMarkerName) is True:
            #Distances
            valueRightUpperLateral = np.linalg.norm(RightUpperKADMarker-RightLateralKADMarker)
            valueRightUpperLower = np.linalg.norm(RightUpperKADMarker-RightLowerKADMarker)
            valueRightLateralLower = np.linalg.norm(RightLateralKADMarker-RightLowerKADMarker)
            RightUpperLateral['text'] = int(round(valueRightUpperLateral))
            RightUpperLower['text'] = int(round((valueRightUpperLower)))
            RightLateralLower['text'] = int(round((valueRightLateralLower)))
            RightDistRange.insert(0,int(round(max(valueRightUpperLateral,valueRightUpperLower,valueRightLateralLower)-min(valueRightUpperLateral,valueRightUpperLower,valueRightLateralLower))))
            #Angles
            valueRightUpperLateralLower = math.Compute3DAngle(RightUpperKADMarker,RightLateralKADMarker,RightLowerKADMarker) * 180 / np.pi
            valueRightLateralUpperLower = math.Compute3DAngle(RightLateralKADMarker,RightUpperKADMarker,RightLowerKADMarker) * 180 / np.pi
            valueRightUpperLowerLateral = math.Compute3DAngle(RightUpperKADMarker,RightLowerKADMarker,RightLateralKADMarker) * 180 / np.pi
            RightUpperLateralLower['text'] = int(round(valueRightUpperLateralLower))
            RightLateralUpperLower['text'] = int(round(valueRightLateralUpperLower))
            RightUpperLowerLateral['text'] = int(round(valueRightUpperLowerLateral))
            RightAngleRange.insert(0,int(round(max(valueRightUpperLateralLower,valueRightLateralUpperLower,valueRightUpperLowerLateral)-min(valueRightUpperLateralLower,valueRightLateralUpperLower,valueRightUpperLowerLateral))))

        # =============================================================================
        #       Function to save Transformation matrics in Static_BF_MRN.py file.
        # =============================================================================
        if not self.valuePelvicFixCheck == '0':
            # Read Current File
            StaticDataFile = open(StaticDataFileName,'r')
            lines=StaticDataFile.readlines()
            StaticDataFile.close()
            
            # Write Subject Data into Static Anthropometric File
            StaticDataFile = open(StaticDataFileName,'w+')
            # Rewrite Subject Information 
            PelfixInformationBlockStarts = 0
            TransformationMatricesBlockStarts = 0
            for line in lines:
                words=line.split()
                if words[0] == '#' and words[1] == 'Pelfix':
                    PelfixInformationBlockStarts = 1
                if words[0] == '#' and words[1] == 'Transformation':
                    TransformationMatricesBlockStarts = 1
                if PelfixInformationBlockStarts == 0 and TransformationMatricesBlockStarts == 0:
                    StaticDataFile.write(line)
            
            # Write Pelfix Information
            StaticDataFile.write('# Pelfix Information' + '\n')
            StaticDataFile.write('self.valueLeftASISMarkerPelvis = np.array([' + str(LeftASISMarkerPelvis[0]) + "," + str(LeftASISMarkerPelvis[1]) + "," + str(LeftASISMarkerPelvis[2]) + "])" +'\n')
            StaticDataFile.write('self.valueRightASISMarkerPelvis = np.array([' + str(RightASISMarkerPelvis[0]) + "," + str(RightASISMarkerPelvis[1]) + "," + str(RightASISMarkerPelvis[2]) + "])" +'\n')
                                 
            # ReWrite Transformation Block if exists
            TransformationMatricesBlockStarts = 0
            for line in lines:
                words=line.split()
                if words[0] == '#' and words[1] == 'Transformation':
                    TransformationMatricesBlockStarts = 1
                if TransformationMatricesBlockStarts == 1:
                    StaticDataFile.write(line)
            #print('FileUpdate- QA Report')    
            StaticDataFile.close()  
            
        
        
class StaticSubjectCalibrationReport_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self,parent, width=AppWidth, height=AppHeight)
        self.parent = parent
        self.grid()
        
    def build_UI(self):     
        # Crete a Canvas to draw section on forms
        SectionCanvas = tk.Canvas(self, width=AppWidth, height=AppHeight)
        SectionCanvas.pack()
        # Saves Static Results in Pdf file
        SavePdfButton = tk.Button(self, text="Save PDF",font=Small_Font, command=lambda: [saveTransformationMatrices(),saveResultsinC3D(),savePdf(),self.parent.frames[StaticSubjectCalibrationReport_Page].build_UI()]) 
        SavePdfButton.place(x=700,y=20,width=90,height=410)
        # Saves Computed Joint center and Knee markers to C3D File and Transformation Matrix to Py File
        SaveResultsButton = tk.Button(self, text="Save Results",wraplength=80,font=Small_Font, command=lambda: [saveTransformationMatrices(),saveResultsinC3D()])
        SaveResultsButton.place(x=700,y=440,width=90,height=290)
        # Back button chnages the form display to Patient Information Page
        BackButton = tk.Button(self, text="Back",font=Small_Font, command=lambda: [self.parent.frames[QAreport_Page].tkraise(),self.parent.frames[QAreport_Page].build_UI(),ErrorMessagesLabel.place_forget(),ErrorMessagesText.place_forget()])
        BackButton.place(x=700,y=740,width=90,height=90)
        #Quit button cloese app
        QuitButton = tk.Button(self,text="Quit",font=Small_Font, command=lambda: [quit()])
        QuitButton.place(x=700,y=840,width=90,height=90)
       
# =============================================================================
#       Patient Information widgets are created here
# =============================================================================
        SubjectName = vicon.GetSubjectNames()[0]
        FilePath, FileName = vicon.GetTrialName()
        
        StaticFileLabel = tk.Label(self, text="Static File-", font=Small_Font)
        StaticFileLabel.place(x=50,y=50)
        SectionCanvas.create_rectangle(195, 45, 680, 75, dash=1)
        StaticFile = tk.Label(self, text=str(FileName + '.c3d'), font=Small_Font )
        StaticFile.place(x=200,y=50)
        
        ModelLabel = tk.Label(self, text="Model-", font=Small_Font)
        ModelLabel.place(x=50,y=100)
        FilePath, FileName = vicon.GetTrialName()
        SectionCanvas.create_rectangle(195, 95, 680, 125, dash=1)
        Model = tk.Label(self, text='Shriners Gait Model', font=Small_Font )
        Model.place(x=200,y=100)
        
        UserPreferenceLabel = tk.Label(self,text='User Preference', font=Small_Font)
        UserPreferenceLabel.place(x=50,y=150)
        SectionCanvas.create_rectangle(195, 145, 680, 175, dash=1)
        UserPreference = tk.Label(self, text=UserPreferencesFileName, font=Smaller_Font, anchor='w' )
        UserPreference.place(x=200,y=150,width=470)
        
        #Create Error Label but place them only if error occurs
        ErrorMessagesLabel = tk.Label(self,text='Warnings', font=Bold_Small_Font)
        ErrorMessagesText = tk.Text(self)
        ErrorMessagesLabel['fg']='red'
        ErrorMessagesText['fg']='red'
        #ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
        #ErrorMessagesText.place(x=195,y=95,width=490,height=85)
        
        #Create File Save Error Label but place them only if error occurs
        SaveErrorMessagesLabel = tk.Label(self,text='Warning', font=Small_Font, anchor = 'w')
        SaveErrorMessagesLabel['fg']='red'
        
# =============================================================================
#       Posture Information Form  widgets are created here
# =============================================================================
        SectionCanvas.create_rectangle(20, 200, 680, 865)
        
        StandingPostureLabel = tk.Label(self, text="Standing Posture (degrees)", font=Large_Font)
        StandingPostureLabel.place(x=50,y=180)
        
        LeftLabel = tk.Label(self, text='Left', font=Bold_Small_Font)
        LeftLabel.place(x=425,y=210)
        
        RightLabel = tk.Label(self, text='Right', font=Bold_Small_Font)
        RightLabel.place(x=575,y=210)
        
        TrunkObliquityLabel = tk.Label(self, text='Trunk Obliqity', font=Small_Font, anchor='e') 
        TrunkObliquityLabel.place(x=100,y=238,width=290)
        LeftTrunkObliquity = tk.Entry(self,justify='center')
        LeftTrunkObliquity.place(x=400,y=240,height=20,width=100)
        RightTrunkObliquity = tk.Entry(self,justify='center')
        RightTrunkObliquity.place(x=550,y=240,height=20,width=100)
        
        TrunkTiltLabel = tk.Label(self, text='Trunk Tilt', font=Small_Font, anchor='e') 
        TrunkTiltLabel.place(x=100,y=263,width=290)
        LeftTrunkTilt = tk.Entry(self,justify='center')
        LeftTrunkTilt.place(x=400,y=265,height=20,width=100)
        RightTrunkTilt = tk.Entry(self,justify='center')
        RightTrunkTilt.place(x=550,y=265,height=20,width=100)
        
        TrunkRotationLabel = tk.Label(self, text='Trunk Rotation', font=Small_Font, anchor='e') 
        TrunkRotationLabel.place(x=100,y=288,width=290)
        LeftTrunkRotation = tk.Entry(self,justify='center')
        LeftTrunkRotation.place(x=400,y=290,height=20,width=100)
        RightTrunkRotation = tk.Entry(self,justify='center')
        RightTrunkRotation.place(x=550,y=290,height=20,width=100)
        
        PelvisObliquityLabel = tk.Label(self, text='Pelvic Obliquity', font=Small_Font, anchor='e') 
        PelvisObliquityLabel.place(x=100,y=313,width=290)
        LeftPelvisObliquity = tk.Entry(self,justify='center')
        LeftPelvisObliquity.place(x=400,y=315,height=20,width=100)
        RightPelvisObliquity = tk.Entry(self,justify='center')
        RightPelvisObliquity.place(x=550,y=315,height=20,width=100)
        
        PelvisTiltLabel = tk.Label(self, text='Pelvic Tilt', font=Small_Font, anchor='e') 
        PelvisTiltLabel.place(x=100,y=338,width=290)
        LeftPelvisTilt = tk.Entry(self,justify='center')
        LeftPelvisTilt.place(x=400,y=340,height=20,width=100)
        RightPelvisTilt = tk.Entry(self,justify='center')
        RightPelvisTilt.place(x=550,y=340,height=20,width=100)
        
        PelvisRotationLabel = tk.Label(self, text='Pelvic Rotation', font=Small_Font, anchor='e') 
        PelvisRotationLabel.place(x=100,y=363,width=290)
        LeftPelvisRotation = tk.Entry(self,justify='center')
        LeftPelvisRotation.place(x=400,y=365,height=20,width=100)
        RightPelvisRotation = tk.Entry(self,justify='center')
        RightPelvisRotation.place(x=550,y=365,height=20,width=100)
        
        HipAbAdductionLabel = tk.Label(self, text='Hip Ab/Adduction', font=Small_Font, anchor='e') 
        HipAbAdductionLabel.place(x=100,y=388,width=290)
        LeftHipAbAdduction = tk.Entry(self,justify='center')
        LeftHipAbAdduction.place(x=400,y=390,height=20,width=100)
        RightHipAbAdduction = tk.Entry(self,justify='center')
        RightHipAbAdduction.place(x=550,y=390,height=20,width=100)
        
        HipFlexExtensionLabel = tk.Label(self, text='Hip Flex/Extension', font=Small_Font, anchor='e') 
        HipFlexExtensionLabel.place(x=100,y=413,width=290)
        LeftHipFlexExtension = tk.Entry(self,justify='center')
        LeftHipFlexExtension.place(x=400,y=415,height=20,width=100)
        RightHipFlexExtension = tk.Entry(self,justify='center')
        RightHipFlexExtension.place(x=550,y=415,height=20,width=100)
        
        HipIntExtRotationLabel = tk.Label(self, text='Hip Int/Ext Rotation', font=Small_Font, anchor='e') 
        HipIntExtRotationLabel.place(x=100,y=438,width=290)
        LeftHipIntExtRotation = tk.Entry(self,justify='center')
        LeftHipIntExtRotation.place(x=400,y=440,height=20,width=100)
        RightHipIntExtRotation = tk.Entry(self,justify='center')
        RightHipIntExtRotation.place(x=550,y=440,height=20,width=100)
        
        KneeVarusValgusLabel = tk.Label(self, text='Knee Varus/Valgus', font=Small_Font, anchor='e') 
        KneeVarusValgusLabel.place(x=100,y=463,width=290)
        LeftKneeVarusValgus = tk.Entry(self,justify='center')
        LeftKneeVarusValgus.place(x=400,y=465,height=20,width=100)
        RightKneeVarusValgus = tk.Entry(self,justify='center')
        RightKneeVarusValgus.place(x=550,y=465,height=20,width=100)
        
        KneeFlexExtensionLabel = tk.Label(self, text='Knee Flex/Extension', font=Small_Font, anchor='e') 
        KneeFlexExtensionLabel.place(x=100,y=488,width=290)
        LeftKneeFlexExtension = tk.Entry(self,justify='center')
        LeftKneeFlexExtension.place(x=400,y=490,height=20,width=100)
        RightKneeFlexExtension = tk.Entry(self,justify='center')
        RightKneeFlexExtension.place(x=550,y=490,height=20,width=100)
        
        KneeIntExtRotationLabel = tk.Label(self, text='Knee Int/Ext Rotation', font=Small_Font, anchor='e') 
        KneeIntExtRotationLabel.place(x=100,y=513,width=290)
        LeftKneeIntExtRotation = tk.Entry(self,justify='center')
        LeftKneeIntExtRotation.place(x=400,y=515,height=20,width=100)
        RightKneeIntExtRotation = tk.Entry(self,justify='center')
        RightKneeIntExtRotation.place(x=550,y=515,height=20,width=100)
        
        KneeProgressionLabel = tk.Label(self, text='Knee Progression', font=Small_Font, anchor='e') 
        KneeProgressionLabel.place(x=100,y=538,width=290)
        LeftKneeProgression = tk.Entry(self,justify='center')
        LeftKneeProgression.place(x=400,y=540,height=20,width=100)
        RightKneeProgression = tk.Entry(self,justify='center')
        RightKneeProgression.place(x=550,y=540,height=20,width=100)
        
        AnklePlantarDorsiflexionLabel = tk.Label(self, text='Ankle Plantar/Dorsiflexion', font=Small_Font, anchor='e') 
        AnklePlantarDorsiflexionLabel.place(x=100,y=563,width=290)
        LeftAnklePlantarDorsiflexion = tk.Entry(self,justify='center')
        LeftAnklePlantarDorsiflexion.place(x=400,y=565,height=20,width=100)
        RightAnklePlantarDorsiflexion = tk.Entry(self,justify='center')
        RightAnklePlantarDorsiflexion.place(x=550,y=565,height=20,width=100)
        
        AnkleIntExtRotationLabel = tk.Label(self, text='Ankle Int/Ext Rotation', font=Small_Font, anchor='e') 
        AnkleIntExtRotationLabel.place(x=100,y=588,width=290)
        LeftAnkleIntExtRotation = tk.Entry(self,justify='center')
        LeftAnkleIntExtRotation.place(x=400,y=590,height=20,width=100)
        RightAnkleIntExtRotation = tk.Entry(self,justify='center')
        RightAnkleIntExtRotation.place(x=550,y=590,height=20,width=100)
        
        FootProgressionLabel = tk.Label(self, text='Foot Progression', font=Small_Font, anchor='e') 
        FootProgressionLabel.place(x=100,y=613,width=290)
        LeftFootProgression = tk.Entry(self,justify='center')
        LeftFootProgression.place(x=400,y=615,height=20,width=100)
        RightFootProgression = tk.Entry(self,justify='center')
        RightFootProgression.place(x=550,y=615,height=20,width=100)
        
        # Foot Posture
        SectionCanvas.create_rectangle(40, 650, 660, 860, outline = 'grey')
        FootSegmentsLabel = tk.Label(self, text='Foot Segments', font=Small_Font, anchor='w')
        FootSegmentsLabel.place(x=50,y=635)
        
        HindfootPitchLabel = tk.Label(self, text='Hindfoot Pitch', font=Small_Font, anchor='e') 
        HindfootPitchLabel.place(x=100,y=653,width=290)
        LeftHindfootPitch = tk.Entry(self,justify='center')
        LeftHindfootPitch.place(x=400,y=655,height=20,width=100)
        RightHindfootPitch = tk.Entry(self,justify='center')
        RightHindfootPitch.place(x=550,y=655,height=20,width=100)
        
        HindfootProgressionLabel = tk.Label(self, text='Hindfoot Progression', font=Small_Font, anchor='e') 
        HindfootProgressionLabel.place(x=100,y=678,width=290)
        LeftHindfootProgression = tk.Entry(self,justify='center')
        LeftHindfootProgression.place(x=400,y=680,height=20,width=100)
        RightHindfootProgression = tk.Entry(self,justify='center')
        RightHindfootProgression.place(x=550,y=680,height=20,width=100)
        
        HindfootInvEversionLabel = tk.Label(self, text='Hindfoot Varus/Valgus', font=Small_Font, anchor='e') 
        HindfootInvEversionLabel.place(x=100,y=703,width=290)
        LeftHindfootInvEversion = tk.Entry(self,justify='center')
        LeftHindfootInvEversion.place(x=400,y=705,height=20,width=100)
        RightHindfootInvEversion = tk.Entry(self,justify='center')
        RightHindfootInvEversion.place(x=550,y=705,height=20,width=100)
        
        AnkleComplexInvEversionLabel = tk.Label(self, text='Ankle Complex Varus/Valgus', font=Small_Font, anchor='e') 
        AnkleComplexInvEversionLabel.place(x=100,y=728,width=290)
        LeftAnkleComplexInvEversion = tk.Entry(self,justify='center')
        LeftAnkleComplexInvEversion.place(x=400,y=730,height=20,width=100)
        RightAnkleComplexInvEversion = tk.Entry(self,justify='center')
        RightAnkleComplexInvEversion.place(x=550,y=730,height=20,width=100)
        
#        ForefootPitchLabel = tk.Label(self, text='Forefoot Pitch', font=Small_Font, anchor='e') 
#        ForefootPitchLabel.place(x=100,y=763,width=290)
#        LeftForefootPitch = tk.Entry(self,justify='center')
#        LeftForefootPitch.place(x=400,y=765,height=20,width=100)
#        RightForefootPitch = tk.Entry(self,justify='center')
#        RightForefootPitch.place(x=550,y=765,height=20,width=100)
#        
#        ForefootProgressionLabel = tk.Label(self, text='Forefoot Progression', font=Small_Font, anchor='e') 
#        ForefootProgressionLabel.place(x=100,y=788,width=290)
#        LeftForefootProgression = tk.Entry(self,justify='center')
#        LeftForefootProgression.place(x=400,y=790,height=20,width=100)
#        RightForefootProgression = tk.Entry(self,justify='center')
#        RightForefootProgression.place(x=550,y=790,height=20,width=100)
        
#        ForefootInvEversionLabel = tk.Label(self, text='Forefoot Inv/Eversion', font=Small_Font, anchor='e') 
#        ForefootInvEversionLabel.place(x=100,y=803,width=290)
#        LeftForefootInvEversion = tk.Entry(self,justify='center')
#        LeftForefootInvEversion.place(x=400,y=805,height=20,width=100)
#        RightForefootInvEversion = tk.Entry(self,justify='center')
#        RightForefootInvEversion.place(x=550,y=805,height=20,width=100)
        
        ForefootPitchLabel = tk.Label(self, text='Forefoot Pitch', font=Small_Font, anchor='e') 
        ForefootPitchLabel.place(x=100,y=753,width=290)
        LeftForefootPitch = tk.Entry(self,justify='center')
        LeftForefootPitch.place(x=400,y=755,height=20,width=100)
        RightForefootPitch = tk.Entry(self,justify='center')
        RightForefootPitch.place(x=550,y=755,height=20,width=100)
        
        ForefootProgressionLabel = tk.Label(self, text='Forefoot Progression', font=Small_Font, anchor='e') 
        ForefootProgressionLabel.place(x=100,y=778,width=290)
        LeftForefootProgression = tk.Entry(self,justify='center')
        LeftForefootProgression.place(x=400,y=780,height=20,width=100)
        RightForefootProgression = tk.Entry(self,justify='center')
        RightForefootProgression.place(x=550,y=780,height=20,width=100)
        
        MidfootAbAdductionLabel = tk.Label(self, text='Midfoot Complex Ab/Adduction', font=Small_Font, anchor='e') 
        MidfootAbAdductionLabel.place(x=100,y=803,width=290)
        LeftMidfootAbAdduction = tk.Entry(self,justify='center')
        LeftMidfootAbAdduction.place(x=400,y=805,height=20,width=100)
        RightMidfootAbAdduction = tk.Entry(self,justify='center')
        RightMidfootAbAdduction.place(x=550,y=805,height=20,width=100)
        
        
        HalluxProgressionLabel = tk.Label(self, text='MTP1 Varus/Valgus', font=Small_Font, anchor='e') 
        HalluxProgressionLabel.place(x=100,y=828,width=290)
        LeftHalluxProgression = tk.Entry(self,justify='center')
        LeftHalluxProgression.place(x=400,y=830,height=20,width=100)
        RightHalluxProgression = tk.Entry(self,justify='center')
        RightHalluxProgression.place(x=550,y=830,height=20,width=100)
        
        SectionCanvas.create_rectangle(20, 880, 680, 925)
        TibiaTorsionLabel = tk.Label(self, text='Tibial Torsion (degrees)', font=Bold_Small_Font, anchor='e') 
        TibiaTorsionLabel.place(x=100,y=888,width=290)
        LeftTibiaTorsion = tk.Entry(self,justify='center')
        LeftTibiaTorsion.place(x=400,y=890,height=20,width=100)
        RightTibiaTorsion = tk.Entry(self,justify='center')
        RightTibiaTorsion.place(x=550,y=890,height=20,width=100)
# =============================================================================     
        
# =============================================================================
#       Posture Measures are computed from Marker data  
# =============================================================================
        #Extract Nexus first frame
        StartFrame, EndFrame = vicon.GetTrialRegionOfInterest()
        
        # Extract Clinical Values
        exec(open(StaticDataFileName).read())
        
        # For Sacral Triad Case, delete Sacral Marker Name
        # Explanation: When Sacral marker is used and exists in the UserPreferences, then 
        # Sacral Marker Name is deleted to push the code towards using PSIS markers.
        if self.valuePelvicFixCheck == '2':
            try:
                del self.SacralMarkerName
            except:
                pass
        else:
            pass
        
        # =============================================================================
        #         Read Marker data from Start Frame (First Frame) for Static Check
        #         Dispplay Warning if marker not found
        # =============================================================================
        
        # Function to extract markerdata into an array and check if data exists
        def MarkerCheck(Subject, MarkerName, FirstFrame):
            # Check if marker exists at all
            if vicon.HasTrajectory(Subject,MarkerName) is True:
                MarkerData = np.array(vicon.GetTrajectoryAtFrame(SubjectName, MarkerName, FirstFrame )[0:3])
                # Check if marker is labeled at the first frame
                if MarkerData[0] == 0 or MarkerData[1] == 0 or MarkerData[2] == 0:
                    ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                    ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                    ErrorMessage = 'Marker ' + MarkerName + ' is not labeled at frame ' + str(FirstFrame) + '\n'
                    ErrorMessagesText.insert(tk.END,ErrorMessage)
            else:
                MarkerData = np.array([0,0,0])
                # Dont show error for Trunk Markers
                ExcludedForErrorMarkerNames = [self.C7MarkerName, self.LeftClavicleMarkerName, self.RightClavicleMarkerName]
                # Add anatomical foot model markers to Excluded list if Sitting Foot Static.py exists
                if os.path.exists(SittingFootStaticDataFileName):
                    ExcludedForErrorMarkerNames = [self.C7MarkerName, self.LeftClavicleMarkerName, self.RightClavicleMarkerName,\
                                                   self.Left23MetatarsalBaseMarkerName, self.Left23MetatarsalHeadMarkerName,\
                                                   self.LeftFirstMetatarsalMedialBaseMarkerName, self.LeftFirstMetatarsalMedialHeadMarkerName,\
                                                   self.LeftCalcanealPeronealTrochleaMarkerName, self.LeftFirstMetatarsoPhalangealJointMarkerName,\
                                                   self.Right23MetatarsalBaseMarkerName, self.Right23MetatarsalHeadMarkerName,\
                                                   self.RightFirstMetatarsalMedialBaseMarkerName, self.RightFirstMetatarsalMedialHeadMarkerName,\
                                                   self.RightCalcanealPeronealTrochleaMarkerName, self.RightFirstMetatarsoPhalangealJointMarkerName]
                if not MarkerName in ExcludedForErrorMarkerNames: 
                    ErrorMessagesLabel.place(x=50,y=100, width=130,height=85)
                    ErrorMessagesText.place(x=195,y=95,width=490,height=85)
                    ErrorMessage = 'Marker ' + MarkerName + ' is not Found ' + '\n'
                    ErrorMessagesText.insert(tk.END,ErrorMessage)
            return MarkerData    
        
        C7Marker = MarkerCheck(SubjectName,self.C7MarkerName,int(self.valueStaticFrameNumber))  
        LeftClavicleMarker = MarkerCheck(SubjectName,self.LeftClavicleMarkerName,int(self.valueStaticFrameNumber))  
        RightClavicleMarker = MarkerCheck(SubjectName,self.RightClavicleMarkerName,int(self.valueStaticFrameNumber))  
        # =============================================================================
        #       Determine if Trunk Data is Available  
        # =============================================================================
        if (C7Marker[2] * LeftClavicleMarker[2] * RightClavicleMarker[2]) > 0:
            TrunkFlag = 1
        else:
            TrunkFlag = 0
        ##############################################################################
        try:
            SacralMarker = MarkerCheck(SubjectName,self.SacralMarkerName,int(self.valueStaticFrameNumber))  
        except:
            #Compute Sacral Marker as mid point of PSIS markers
            LeftPSISMarker = MarkerCheck(SubjectName,self.LeftPSISMarkerName,int(self.valueStaticFrameNumber)) 
            RightPSISMarker = MarkerCheck(SubjectName,self.RightPSISMarkerName,int(self.valueStaticFrameNumber)) 
            SacralMarker = (LeftPSISMarker + RightPSISMarker) / 2
        LeftASISMarker = MarkerCheck(SubjectName,self.LeftASISMarkerName,int(self.valueStaticFrameNumber))   
        LeftThighMarker = MarkerCheck(SubjectName,self.LeftThighMarkerName,int(self.valueStaticFrameNumber))   
        LeftTibialMarker = MarkerCheck(SubjectName,self.LeftTibialMarkerName,int(self.valueStaticFrameNumber))   
        LeftLateralAnkleMarker = MarkerCheck(SubjectName,self.LeftLateralAnkleMarkerName,int(self.valueStaticFrameNumber))   
        LeftToeMarker = MarkerCheck(SubjectName,self.LeftToeMarkerName,int(self.valueStaticFrameNumber))   
        LeftMedialAnkleMarker = MarkerCheck(SubjectName,self.LeftMedialAnkleMarkerName,int(self.valueStaticFrameNumber))   
        LeftHeelMarker = MarkerCheck(SubjectName,self.LeftHeelMarkerName,int(self.valueStaticFrameNumber))   
        if self.valueKneeAlignmentCheck == '0':
            LeftLateralKADMarker = MarkerCheck(SubjectName,self.LeftLateralKADMarkerName,int(self.valueStaticFrameNumber))   
            LeftUpperKADMarker = MarkerCheck(SubjectName,self.LeftUpperKADMarkerName,int(self.valueStaticFrameNumber))  
            LeftLowerKADMarker = MarkerCheck(SubjectName,self.LeftLowerKADMarkerName,int(self.valueStaticFrameNumber))   
        else:
            LeftLateralKneeMarker = MarkerCheck(SubjectName,self.LeftLateralKneeMarkerName,int(self.valueStaticFrameNumber)) 
            LeftMedialKneeMarker = MarkerCheck(SubjectName,self.LeftMedialKneeMarkerName,int(self.valueStaticFrameNumber))   
        
        # Read Left Foot Markers
        if self.valueLeftFootModelCheck == '1':
            LeftLateralCalcaneusMarker = MarkerCheck(SubjectName,self.LeftLateralCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            LeftMedialCalcaneusMarker = MarkerCheck(SubjectName,self.LeftMedialCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            LeftPosteriorCalcaneusMarker = MarkerCheck(SubjectName,self.LeftPosteriorCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFirstMetarsalBaseMarker = MarkerCheck(SubjectName,self.LeftFirstMetarsalBaseMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFirstMetarsalHeadMarker = MarkerCheck(SubjectName,self.LeftFirstMetarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFifthMetarsalHeadMarker = MarkerCheck(SubjectName,self.LeftFifthMetarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            LeftHalluxMarker = MarkerCheck(SubjectName,self.LeftHalluxMarkerName, int(self.valueStaticFrameNumber)) 
            Left23MetatarsalBaseMarker = MarkerCheck(SubjectName,self.Left23MetatarsalBaseMarkerName, int(self.valueStaticFrameNumber)) 
            Left23MetatarsalHeadMarker = MarkerCheck(SubjectName,self.Left23MetatarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFirstMetatarsalMedialBaseMarker = MarkerCheck(SubjectName,self.LeftFirstMetatarsalMedialBaseMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFirstMetatarsalMedialHeadMarker = MarkerCheck(SubjectName,self.LeftFirstMetatarsalMedialHeadMarkerName, int(self.valueStaticFrameNumber)) 
            LeftCalcanealPeronealTrochleaMarker = MarkerCheck(SubjectName,self.LeftCalcanealPeronealTrochleaMarkerName, int(self.valueStaticFrameNumber)) 
            LeftFirstMetatarsoPhalangealJointMarker = MarkerCheck(SubjectName,self.LeftFirstMetatarsoPhalangealJointMarkerName, int(self.valueStaticFrameNumber)) 

        
        RightASISMarker = MarkerCheck(SubjectName,self.RightASISMarkerName,int(self.valueStaticFrameNumber))   
        RightThighMarker = MarkerCheck(SubjectName,self.RightThighMarkerName,int(self.valueStaticFrameNumber))   
        RightTibialMarker = MarkerCheck(SubjectName,self.RightTibialMarkerName,int(self.valueStaticFrameNumber))   
        RightLateralAnkleMarker = MarkerCheck(SubjectName,self.RightLateralAnkleMarkerName,int(self.valueStaticFrameNumber))   
        RightToeMarker = MarkerCheck(SubjectName,self.RightToeMarkerName,int(self.valueStaticFrameNumber))   
        RightMedialAnkleMarker = MarkerCheck(SubjectName,self.RightMedialAnkleMarkerName,int(self.valueStaticFrameNumber))   
        RightHeelMarker = MarkerCheck(SubjectName,self.RightHeelMarkerName,int(self.valueStaticFrameNumber))   
        if self.valueKneeAlignmentCheck == '0':
            RightLateralKADMarker = MarkerCheck(SubjectName,self.RightLateralKADMarkerName,int(self.valueStaticFrameNumber))   
            RightUpperKADMarker = MarkerCheck(SubjectName,self.RightUpperKADMarkerName,int(self.valueStaticFrameNumber))   
            RightLowerKADMarker = MarkerCheck(SubjectName,self.RightLowerKADMarkerName,int(self.valueStaticFrameNumber))  
        else:
            RightLateralKneeMarker = MarkerCheck(SubjectName,self.RightLateralKneeMarkerName,int(self.valueStaticFrameNumber)) 
            RightMedialKneeMarker = MarkerCheck(SubjectName,self.RightMedialKneeMarkerName,int(self.valueStaticFrameNumber))  
        
        # Read Right Foot Markers
        if self.valueRightFootModelCheck == '1':
            RightLateralCalcaneusMarker = MarkerCheck(SubjectName,self.RightLateralCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            RightMedialCalcaneusMarker = MarkerCheck(SubjectName,self.RightMedialCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            RightPosteriorCalcaneusMarker = MarkerCheck(SubjectName,self.RightPosteriorCalcaneusMarkerName, int(self.valueStaticFrameNumber)) 
            RightFirstMetarsalBaseMarker = MarkerCheck(SubjectName,self.RightFirstMetarsalBaseMarkerName, int(self.valueStaticFrameNumber)) 
            RightFirstMetarsalHeadMarker = MarkerCheck(SubjectName,self.RightFirstMetarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            RightFifthMetarsalHeadMarker = MarkerCheck(SubjectName,self.RightFifthMetarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            RightHalluxMarker = MarkerCheck(SubjectName,self.RightHalluxMarkerName, int(self.valueStaticFrameNumber)) 
            Right23MetatarsalBaseMarker = MarkerCheck(SubjectName,self.Right23MetatarsalBaseMarkerName, int(self.valueStaticFrameNumber)) 
            Right23MetatarsalHeadMarker = MarkerCheck(SubjectName,self.Right23MetatarsalHeadMarkerName, int(self.valueStaticFrameNumber)) 
            RightFirstMetatarsalMedialBaseMarker = MarkerCheck(SubjectName,self.RightFirstMetatarsalMedialBaseMarkerName, int(self.valueStaticFrameNumber)) 
            RightFirstMetatarsalMedialHeadMarker = MarkerCheck(SubjectName,self.RightFirstMetatarsalMedialHeadMarkerName, int(self.valueStaticFrameNumber)) 
            RightCalcanealPeronealTrochleaMarker = MarkerCheck(SubjectName,self.RightCalcanealPeronealTrochleaMarkerName, int(self.valueStaticFrameNumber)) 
            RightFirstMetatarsoPhalangealJointMarker = MarkerCheck(SubjectName,self.RightFirstMetatarsoPhalangealJointMarkerName, int(self.valueStaticFrameNumber)) 
        # =============================================================================

        #Read orientation of the Standing patient relative to laboratory coordinate system
        #print(self.StaticForwardDirection)        
        if self.StaticForwardDirection == '+X':
            RotationMatrix = np.array([[ 1.,  0.,  0.], [ 0.,  1.,  0.],[ 0.,  0.,  1.]])
        if self.StaticForwardDirection == '-X':
            RotationMatrix = np.array([[-1.,  0.,  0.], [ 0., -1.,  0.],[ 0.,  0.,  1.]])
        if self.StaticForwardDirection == '+Y':
            RotationMatrix = np.array([[ 0.,  1.,  0.], [-1.,  0.,  0.],[ 0.,  0.,  1.]])
        if self.StaticForwardDirection == '-Y':
            RotationMatrix = np.array([[ 0., -1.,  0.], [ 1.,  0.,  0.],[ 0.,  0.,  1.]])
    
        #Transform marker data if necessary based on direction that the patient is facing
        C7Marker = RotationMatrix.dot(C7Marker)
        LeftClavicleMarker = RotationMatrix.dot(LeftClavicleMarker)
        RightClavicleMarker = RotationMatrix.dot(RightClavicleMarker)
        SacralMarker = RotationMatrix.dot(SacralMarker)
        LeftASISMarker = RotationMatrix.dot(LeftASISMarker)
        LeftThighMarker = RotationMatrix.dot(LeftThighMarker)
        LeftTibialMarker = RotationMatrix.dot(LeftTibialMarker)
        LeftLateralAnkleMarker = RotationMatrix.dot(LeftLateralAnkleMarker)
        LeftToeMarker = RotationMatrix.dot(LeftToeMarker)
        LeftMedialAnkleMarker = RotationMatrix.dot(LeftMedialAnkleMarker)
        LeftHeelMarker = RotationMatrix.dot(LeftHeelMarker)
        if self.valueKneeAlignmentCheck == '0':
            LeftLateralKADMarker = RotationMatrix.dot(LeftLateralKADMarker)
            LeftUpperKADMarker = RotationMatrix.dot(LeftUpperKADMarker)
            LeftLowerKADMarker = RotationMatrix.dot(LeftLowerKADMarker)
        else:
            LeftLateralKneeMarker = RotationMatrix.dot(LeftLateralKneeMarker)
            LeftMedialKneeMarker = RotationMatrix.dot(LeftMedialKneeMarker)
        
        if self.valueLeftFootModelCheck == '1':
            LeftLateralCalcaneusMarker = RotationMatrix.dot(LeftLateralCalcaneusMarker)
            LeftMedialCalcaneusMarker = RotationMatrix.dot(LeftMedialCalcaneusMarker)
            LeftPosteriorCalcaneusMarker = RotationMatrix.dot(LeftPosteriorCalcaneusMarker)
            LeftFirstMetarsalBaseMarker = RotationMatrix.dot(LeftFirstMetarsalBaseMarker)
            LeftFirstMetarsalHeadMarker = RotationMatrix.dot(LeftFirstMetarsalHeadMarker)
            LeftFifthMetarsalHeadMarker = RotationMatrix.dot(LeftFifthMetarsalHeadMarker)
            LeftHalluxMarker = RotationMatrix.dot(LeftHalluxMarker)
            Left23MetatarsalBaseMarker = RotationMatrix.dot(Left23MetatarsalBaseMarker)
            Left23MetatarsalHeadMarker = RotationMatrix.dot(Left23MetatarsalHeadMarker)
            LeftFirstMetatarsalMedialBaseMarker = RotationMatrix.dot(LeftFirstMetatarsalMedialBaseMarker)
            LeftFirstMetatarsalMedialHeadMarker = RotationMatrix.dot(LeftFirstMetatarsalMedialHeadMarker)
            LeftCalcanealPeronealTrochleaMarker = RotationMatrix.dot(LeftCalcanealPeronealTrochleaMarker)
            LeftFirstMetatarsoPhalangealJointMarker = RotationMatrix.dot(LeftFirstMetatarsoPhalangealJointMarker)
            
        RightASISMarker = RotationMatrix.dot(RightASISMarker)
        RightThighMarker = RotationMatrix.dot(RightThighMarker)
        RightTibialMarker = RotationMatrix.dot(RightTibialMarker)
        RightLateralAnkleMarker = RotationMatrix.dot(RightLateralAnkleMarker)
        RightToeMarker = RotationMatrix.dot(RightToeMarker)
        RightMedialAnkleMarker = RotationMatrix.dot(RightMedialAnkleMarker)
        RightHeelMarker = RotationMatrix.dot(RightHeelMarker)
        if self.valueKneeAlignmentCheck == '0':
            RightLateralKADMarker = RotationMatrix.dot(RightLateralKADMarker)
            RightUpperKADMarker = RotationMatrix.dot(RightUpperKADMarker)
            RightLowerKADMarker = RotationMatrix.dot(RightLowerKADMarker)
        else:
            RightLateralKneeMarker = RotationMatrix.dot(RightLateralKneeMarker)
            RightMedialKneeMarker = RotationMatrix.dot(RightMedialKneeMarker)
        
        if self.valueRightFootModelCheck == '1':
            RightLateralCalcaneusMarker = RotationMatrix.dot(RightLateralCalcaneusMarker)
            RightMedialCalcaneusMarker = RotationMatrix.dot(RightMedialCalcaneusMarker)
            RightPosteriorCalcaneusMarker = RotationMatrix.dot(RightPosteriorCalcaneusMarker)
            RightFirstMetarsalBaseMarker = RotationMatrix.dot(RightFirstMetarsalBaseMarker)
            RightFirstMetarsalHeadMarker = RotationMatrix.dot(RightFirstMetarsalHeadMarker)
            RightFifthMetarsalHeadMarker = RotationMatrix.dot(RightFifthMetarsalHeadMarker)
            RightHalluxMarker = RotationMatrix.dot(RightHalluxMarker)
            Right23MetatarsalBaseMarker = RotationMatrix.dot(Right23MetatarsalBaseMarker)
            Right23MetatarsalHeadMarker = RotationMatrix.dot(Right23MetatarsalHeadMarker)
            RightFirstMetatarsalMedialBaseMarker = RotationMatrix.dot(RightFirstMetatarsalMedialBaseMarker)
            RightFirstMetatarsalMedialHeadMarker = RotationMatrix.dot(RightFirstMetatarsalMedialHeadMarker)
            RightCalcanealPeronealTrochleaMarker = RotationMatrix.dot(RightCalcanealPeronealTrochleaMarker)
            RightFirstMetatarsoPhalangealJointMarker = RotationMatrix.dot(RightFirstMetatarsoPhalangealJointMarker)
        
        
        #Compute Technical Coordinate System: Trunk
        if TrunkFlag == 1:
            if C7Marker[2] != 0 and LeftClavicleMarker[2] != 0 and RightClavicleMarker[2] != 0 and LeftASISMarker[2] != 0 and RightASISMarker[2] != 0 and SacralMarker[2] !=0:
                [ETrunkTech,PelvicCenterLab,ShouldersCenterLab] = gait.TechCS_Trunk_Newington(C7Marker, LeftClavicleMarker, RightClavicleMarker, LeftASISMarker, RightASISMarker, SacralMarker)
        else:
            ETrunkTech =  np.eye(3)
        #print(ETrunkTech)
        #print(PelvicCenterLab)
        #print(ShouldersCenterLab)
        
        #Compute Technical Coordinate System: Pelvis
        [EPelvisTech, MidASISLab] = gait.TechCS_Pelvis_Newington(LeftASISMarker, RightASISMarker, SacralMarker)
        #print(EPelvisTech)
        #print(MidASISLab)
        
        #Compute Hip Center Location, relative to midASIS point and expressed relative to pelvic coor system
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
        #print(LeftHipCenterPelvis)
        #print(LeftHipCenterLab)
        #print(RightHipCenterPelvis)
        #print(RightHipCenterLab)
        
        if self.valueKneeAlignmentCheck == '0':
            #Compute Location of Virtual Knee Marker (based on cluster-type knee fixture)
            LeftVirtualKneeMarkerLab = gait.ComputeVirtualKneeMarker_Newington('Left', self.MarkerDiameter, LeftUpperKADMarker, LeftLateralKADMarker, LeftLowerKADMarker)
            RightVirtualKneeMarkerLab = gait.ComputeVirtualKneeMarker_Newington('Right', self.MarkerDiameter, RightUpperKADMarker, RightLateralKADMarker, RightLowerKADMarker)
            #print(LeftVirtualKneeMarkerLab)
            #print(RightVirtualKneeMarkerLab)
        else:
            LeftVirtualKneeMarkerLab = LeftLateralKneeMarker
            RightVirtualKneeMarkerLab = RightLateralKneeMarker
            
        #Compute Technical Coordinate System: Thigh       
        LeftEThighTech = gait.TechCS_Thigh_Newington('Left', LeftHipCenterLab, LeftThighMarker, LeftVirtualKneeMarkerLab)
        RightEThighTech = gait.TechCS_Thigh_Newington('Right', RightHipCenterLab, RightThighMarker, RightVirtualKneeMarkerLab)
        #print(LeftEThighTech)
        #print(RightEThighTech)
        
        if self.valueKneeAlignmentCheck == '0':
            #Compute Location of Knee Center (in lab space)
            LeftKneeCenterLab = gait.JointCenterModel_Knee_Newington('Left', self.MarkerDiameter, self.valueLeftKneeWidth, LeftVirtualKneeMarkerLab, LeftLateralKADMarker)
            RightKneeCenterLab = gait.JointCenterModel_Knee_Newington('Right', self.MarkerDiameter, self.valueRightKneeWidth, RightVirtualKneeMarkerLab, RightLateralKADMarker)
            #print(LeftKneeCenterLab)
            #print(RightKneeCenterLab)
        else:
            E1= math.ComputeUnitVecFromPts(LeftLateralKneeMarker,LeftMedialKneeMarker)
            LeftKneeCenterLab = LeftLateralKneeMarker + (float(self.valueLeftKneeWidth)/2 + float(self.MarkerDiameter)/2) * E1 
            E1= math.ComputeUnitVecFromPts(RightLateralKneeMarker,RightMedialKneeMarker)
            RightKneeCenterLab = RightLateralKneeMarker + (float(self.valueRightKneeWidth)/2 + float(self.MarkerDiameter)/2) * E1 
            
        
        #Compute Knee Center Location Relative to the Thigh Coordinates
        LeftKneeCenterThigh = math.TransformPointIntoMovingCoors(LeftKneeCenterLab, LeftEThighTech, LeftVirtualKneeMarkerLab)
        RightKneeCenterThigh = math.TransformPointIntoMovingCoors(RightKneeCenterLab, RightEThighTech, RightVirtualKneeMarkerLab)
        #print(LeftKneeCenterThigh)
        #print(RightKneeCenterThigh)
        
        #Compute Technical Coordinate System: Shank
        # Use Tibial triad if markers available
        if vicon.HasTrajectory(SubjectName,self.LeftTibialMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftTibialUpperMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftTibialLowerMarkerName) is True:
            LeftTibialTriadCheck = True
            LeftTibialUpperMarker = MarkerCheck(SubjectName,self.LeftTibialUpperMarkerName,int(self.valueStaticFrameNumber)) 
            LeftTibialLowerMarker = MarkerCheck(SubjectName,self.LeftTibialLowerMarkerName,int(self.valueStaticFrameNumber))  
            LeftTibialUpperMarker = RotationMatrix.dot(LeftTibialUpperMarker)
            LeftTibialLowerMarker = RotationMatrix.dot(LeftTibialLowerMarker)
            LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftTibialUpperMarker, LeftTibialLowerMarker, LeftTibialMarker)
        else:
            LeftTibialTriadCheck = False
            LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftKneeCenterLab, LeftTibialMarker, LeftLateralAnkleMarker)
        if vicon.HasTrajectory(SubjectName,self.RightTibialMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightTibialUpperMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightTibialLowerMarkerName) is True:
            RightTibialTriadCheck = True
            RightTibialUpperMarker = MarkerCheck(SubjectName,self.RightTibialUpperMarkerName,int(self.valueStaticFrameNumber))  
            RightTibialLowerMarker = MarkerCheck(SubjectName,self.RightTibialLowerMarkerName,int(self.valueStaticFrameNumber)) 
            RightTibialUpperMarker = RotationMatrix.dot(RightTibialUpperMarker)
            RightTibialLowerMarker = RotationMatrix.dot(RightTibialLowerMarker)
            RightEShankTech = gait.TechCS_Shank_Newington('Right', RightTibialUpperMarker, RightTibialLowerMarker, RightTibialMarker)
        else:
            RightTibialTriadCheck = False
            RightEShankTech = gait.TechCS_Shank_Newington('Right', RightKneeCenterLab, RightTibialMarker, RightLateralAnkleMarker)
        #print(LeftEShankTech)
        #print(RightEShankTech)
        
        #Compute Location of Ankle Center (in lab space)
        LeftAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Left', self.MarkerDiameter, self.valueLeftAnkleWidth, LeftLateralAnkleMarker, LeftMedialAnkleMarker)
        RightAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Right', self.MarkerDiameter, self.valueRightAnkleWidth, RightLateralAnkleMarker, RightMedialAnkleMarker)
        #print(LeftAnkleCenterLab)
        #print(RightAnkleCenterLab)
        
        #Compute Ankle Center Location Relative to Shank Coordinates and Lateral Ankle [Compared to Tibial Marker if Tibial Triad is used]
        if LeftTibialTriadCheck == True:
            LeftAnkleCenterShank = math.TransformPointIntoMovingCoors(LeftAnkleCenterLab, LeftEShankTech, LeftTibialMarker)
        else:
            LeftAnkleCenterShank = math.TransformPointIntoMovingCoors(LeftAnkleCenterLab, LeftEShankTech, LeftLateralAnkleMarker)
        if RightTibialTriadCheck == True:
            RightAnkleCenterShank = math.TransformPointIntoMovingCoors(RightAnkleCenterLab, RightEShankTech, RightTibialMarker)
        else:
            RightAnkleCenterShank = math.TransformPointIntoMovingCoors(RightAnkleCenterLab, RightEShankTech, RightLateralAnkleMarker)
        #print(LeftAnkleCenterShank)
        #print(RightAnkleCenterShank)
        
        #Compute Virtual Heel Marker
        LeftVirtualHeelMarkerLab = gait.ComputeVirtualHeelMarkerLab(self.valueLeftPlantigradeCheck, self.valueSujectShodCheck, self.valueLeftSoleThickness, LeftAnkleCenterLab, LeftToeMarker, LeftHeelMarker)
        RightVirtualHeelMarkerLab = gait.ComputeVirtualHeelMarkerLab(self.valueRightPlantigradeCheck, self.valueSujectShodCheck, self.valueRightSoleThickness, RightAnkleCenterLab, RightToeMarker, RightHeelMarker)
        #print(LeftVirtualHeelMarkerLab)
        #print(RightVirtualHeelMarkerLab)
        
        # Compute Technical Coordinate System: Foot
        LeftEFootTech = gait.TechCS_Foot_Newington('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftToeMarker)
        RightEFootTech = gait.TechCS_Foot_Newington('Right', RightKneeCenterLab, RightAnkleCenterLab, RightToeMarker)
        #print(LeftEFootTech)
        #print(RightEFootTech)
        
        # Compute Technical Coordinate System: Left Foot Segments
        if self.valueLeftFootModelCheck == '1':
            LeftEHindfootTech = gait.TechCS_Hindfoot_mSHCG('Left', LeftLateralCalcaneusMarker, LeftMedialCalcaneusMarker, LeftPosteriorCalcaneusMarker)
            LeftEForefootTech = gait.TechCS_Forefoot_mSHCG('Left', LeftFirstMetarsalBaseMarker, LeftFirstMetarsalHeadMarker, LeftFifthMetarsalHeadMarker)
            if os.path.exists(SittingFootStaticDataFileName):
                exec(open(SittingFootStaticDataFileName).read())
                Left23MetatarsalHeadMarker = math.TransformPointIntoLabCoors(self.valueLeft23MetatarsalHeadMarkerForefoot,LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                LeftFirstMetatarsoPhalangealJointMarker = math.TransformPointIntoLabCoors(self.valueLeftFirstMetatarsoPhalangealJointMarkerForefoot,LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                exec(open(StaticDataFileName).read())
            LeftEHalluxTech = gait.TechCS_Hallux_mSHCG('Left', LeftHalluxMarker, LeftFirstMetatarsoPhalangealJointMarker, Left23MetatarsalHeadMarker)
            
            #print(LeftEHindfootTech)
            #print(LeftEForefootTech)
            #print(LeftEHalluxTech)
        
        # Compute Technical Coordinate System: Right Foot Segments
        if self.valueRightFootModelCheck == '1':
            RightEHindfootTech = gait.TechCS_Hindfoot_mSHCG('Right', RightLateralCalcaneusMarker, RightMedialCalcaneusMarker, RightPosteriorCalcaneusMarker)
            RightEForefootTech = gait.TechCS_Forefoot_mSHCG('Right', RightFirstMetarsalBaseMarker, RightFirstMetarsalHeadMarker, RightFifthMetarsalHeadMarker)
            if os.path.exists(SittingFootStaticDataFileName):
                exec(open(SittingFootStaticDataFileName).read())
                Right23MetatarsalHeadMarker = math.TransformPointIntoLabCoors(self.valueRight23MetatarsalHeadMarkerForefoot,RightEForefootTech, RightFirstMetarsalBaseMarker)
                RightFirstMetatarsoPhalangealJointMarker = math.TransformPointIntoLabCoors(self.valueRightFirstMetatarsoPhalangealJointMarkerForefoot,RightEForefootTech, RightFirstMetarsalBaseMarker)
                exec(open(StaticDataFileName).read())
            RightEHalluxTech = gait.TechCS_Hallux_mSHCG('Right', RightHalluxMarker, RightFirstMetatarsoPhalangealJointMarker, Right23MetatarsalHeadMarker)
            #print(RightEHindfootTech)
            #print(RightEForefootTech)
            #print(RightEHalluxTech)
            
        #Compute Anatomical Coordinate System: Trunk and Pelvis
        ETrunkAnat = ETrunkTech
        EPelvisAnat = EPelvisTech
        
        #Compute Anatomical Coordinate System: Thigh
        LeftEThighAnat= gait.AnatCS_Thigh_Newington('Left', LeftHipCenterLab, LeftVirtualKneeMarkerLab, LeftKneeCenterLab)
        RightEThighAnat= gait.AnatCS_Thigh_Newington('Right', RightHipCenterLab, RightVirtualKneeMarkerLab, RightKneeCenterLab)
        #print(LeftEThighAnat)
        #print(RightEThighAnat)
        
        #Compute Anatomical Coordinate System: Proximal Shank
        LeftEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Left', LeftKneeCenterLab, LeftVirtualKneeMarkerLab, LeftAnkleCenterLab)
        RightEShankProximalAnat = gait.AnatCS_Shank_Proximal_Newington('Right', RightKneeCenterLab, RightVirtualKneeMarkerLab, RightAnkleCenterLab)
        #print(LeftEShankProximalAnat)
        #print(RightEShankProximalAnat)
        
        #Compute Anatomical Coordinate System: Distal Shank
        LeftEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftLateralAnkleMarker)
        RightEShankDistalAnat= gait.AnatCS_Shank_Distal_VCM('Right', RightKneeCenterLab, RightAnkleCenterLab, RightLateralAnkleMarker)
        #print(LeftEShankDistalAnat)
        #print(RightEShankDistalAnat)
        
        #Compute Anatomical Coordinate System (or Vector):  Foot
        LeftEFootAnat = gait.AnatCS_Foot_Newington('Left', LeftLateralAnkleMarker, LeftAnkleCenterLab, LeftToeMarker, LeftVirtualHeelMarkerLab)
        RightEFootAnat = gait.AnatCS_Foot_Newington('Right', RightLateralAnkleMarker, RightAnkleCenterLab, RightToeMarker, RightVirtualHeelMarkerLab)
        #print(LeftEFootAnat)
        #print(RightEFootAnat)
        
        # Compute Anatomical Coodttinate System: Second Foot CS for Ankle Joint Reaction force [Uses Knee Center Instead of lateral Ankle Marker]
        LeftEFootAnat2 = gait.AnatCS_Foot_ShrineGaitModel('Left', LeftKneeCenterLab, LeftAnkleCenterLab, LeftToeMarker, LeftVirtualHeelMarkerLab)
        RightEFootAnat2 = gait.AnatCS_Foot_ShrineGaitModel('Right', RightKneeCenterLab, RightAnkleCenterLab, RightToeMarker, RightVirtualHeelMarkerLab)
        
        # Compute Anatomical Coordinate System: Left Foot Segments
        if self.valueLeftFootModelCheck == '1':
            if os.path.exists(SittingFootStaticDataFileName):
                exec(open(SittingFootStaticDataFileName).read())
                LeftEHindfootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEHindfootAnatRelTech, LeftEHindfootTech)
                LeftEForefootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEForefootAnatRelTech, LeftEForefootTech)
                LeftEHalluxAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEHalluxAnatRelTech, LeftEHalluxTech)
                exec(open(StaticDataFileName).read())
            else:    
                LeftEHindfootAnat = gait.AnatCS_Hindfoot_mSHCG('Left', LeftLateralCalcaneusMarker, LeftMedialCalcaneusMarker, LeftPosteriorCalcaneusMarker, 
                                                               LeftCalcanealPeronealTrochleaMarker, self.valueLeftHindfootVarus, self.valueLeftCalcanealPitch,self.valueLeftHindfootProgression,self.HindfootValgusIsNegative)
                LeftEForefootAnat = gait.AnatCS_Forefoot_mSHCG('Left', Left23MetatarsalBaseMarker, Left23MetatarsalHeadMarker, LeftFirstMetatarsalMedialBaseMarker,
                                                               LeftFirstMetatarsalMedialHeadMarker, self.valueLeftFirstMetatarsalPitch)
                LeftEHalluxAnat = LeftEHalluxTech
            #print(LeftEHindfootAnat)
            #print(LeftEForefootAnat)
            #print(LeftEHalluxAnat)
        
        # Compute Anatomical Coordinate System: Right Foot Segments
        if self.valueRightFootModelCheck == '1':
            if os.path.exists(SittingFootStaticDataFileName):
                exec(open(SittingFootStaticDataFileName).read())
                RightEHindfootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEHindfootAnatRelTech, RightEHindfootTech)
                RightEForefootAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEForefootAnatRelTech, RightEForefootTech)
                RightEHalluxAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEHalluxAnatRelTech, RightEHalluxTech)
                exec(open(StaticDataFileName).read())
            else:
                RightEHindfootAnat = gait.AnatCS_Hindfoot_mSHCG('Right', RightLateralCalcaneusMarker, RightMedialCalcaneusMarker, RightPosteriorCalcaneusMarker, 
                                                               RightCalcanealPeronealTrochleaMarker, self.valueRightHindfootVarus, self.valueRightCalcanealPitch,self.valueRightHindfootProgression,self.HindfootValgusIsNegative)
                RightEForefootAnat = gait.AnatCS_Forefoot_mSHCG('Right', Right23MetatarsalBaseMarker, Right23MetatarsalHeadMarker, RightFirstMetatarsalMedialBaseMarker,
                                                               RightFirstMetatarsalMedialHeadMarker, self.valueRightFirstMetatarsalPitch)
                RightEHalluxAnat = RightEHalluxTech
            #print(RightEHindfootAnat)
            #print(RightEForefootAnat)
            #print(RightEHalluxAnat)
            
        #Compute Attitude of Anatomical Coordinate Systems Relative to their respective Technical Coordinate System
        ETrunkAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(ETrunkAnat, ETrunkTech)
        EPelvisAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(EPelvisAnat, EPelvisTech)
        LeftEThighAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEThighAnat, LeftEThighTech)
        LeftEShankProximalAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEShankProximalAnat, LeftEShankTech)
        LeftEShankDistalAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEShankDistalAnat, LeftEShankTech)
        LeftEFootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEFootAnat, LeftEFootTech)
        RightEThighAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEThighAnat, RightEThighTech)
        RightEShankProximalAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEShankProximalAnat, RightEShankTech)
        RightEShankDistalAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEShankDistalAnat, RightEShankTech)
        RightEFootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEFootAnat, RightEFootTech)
        # Foot CS for Ankle Joint Reaction Force
        LeftEFootAnat2RelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEFootAnat2, LeftEFootTech)
        RightEFootAnat2RelTech = math.TransformAnatCoorSysIntoTechCoors(RightEFootAnat2, RightEFootTech)
        if self.valueLeftFootModelCheck == '1':
            LeftEHindfootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEHindfootAnat, LeftEHindfootTech)
            LeftEForefootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEForefootAnat, LeftEForefootTech)
            LeftEHalluxAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(LeftEHalluxAnat, LeftEHalluxTech)
            Left23MetatarsalHeadMarkerForefoot = math.TransformPointIntoMovingCoors(Left23MetatarsalHeadMarker, LeftEForefootTech, LeftFirstMetarsalBaseMarker)
            LeftFirstMetatarsoPhalangealJointMarkerForefoot = math.TransformPointIntoMovingCoors(LeftFirstMetatarsoPhalangealJointMarker, LeftEForefootTech, LeftFirstMetarsalBaseMarker)
                    
        if self.valueRightFootModelCheck == '1':
            RightEHindfootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEHindfootAnat, RightEHindfootTech)
            RightEForefootAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEForefootAnat, RightEForefootTech)
            RightEHalluxAnatRelTech = math.TransformAnatCoorSysIntoTechCoors(RightEHalluxAnat, RightEHalluxTech)
            Right23MetatarsalHeadMarkerForefoot = math.TransformPointIntoMovingCoors(Right23MetatarsalHeadMarker, RightEForefootTech, RightFirstMetarsalBaseMarker)
            RightFirstMetatarsoPhalangealJointMarkerForefoot = math.TransformPointIntoMovingCoors(RightFirstMetatarsoPhalangealJointMarker, RightEForefootTech, RightFirstMetarsalBaseMarker)
            
        #print(ETrunkAnatRelTech)
        #print(EPelvisAnatRelTech)
        #print(LeftEThighAnatRelTech)
        #print(LeftEShankProximalAnatRelTech)
        #print(LeftEShankDistalAnatRelTech)
        #print(LeftEFootAnatRelTech)
        #print(RightEThighAnatRelTech)
        #print(RightEShankProximalAnatRelTech)
        #print(RightEShankDistalAnatRelTech)
        #print(RightEFootAnatRelTech)
        
        
        
        #initialize the global or lab coordinate system
        ELab = np.eye(3)
        
        #Compute trunk kinematics
        TrunkAnglesTORRad = math.EulerAngles_YXZ(ETrunkAnat, ELab)
        TrunkAnglesROTRad = math.EulerAngles_ZXY(ETrunkAnat, ELab)
        if self.TrunkRotationSequence == 'TOR':
            TrunkAnglesRad = TrunkAnglesTORRad
        if self.TrunkRotationSequence == 'ROT':
            TrunkAnglesRad = TrunkAnglesROTRad
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
        LeftShankAnglesRad = math.EulerAngles_YXZ(LeftEShankDistalAnat, ELab, )     
        RightShankAnglesRad = math.EulerAngles_YXZ(RightEShankDistalAnat, ELab, )     
        #Compute foot kinematics
        LeftFootAnglesRad = math.EulerAngles_YXZ(LeftEFootAnat, ELab, )
        RightFootAnglesRad = math.EulerAngles_YXZ(RightEFootAnat, ELab, )
        #Compute hip kinematics
        LeftHipAnglesRad = math.EulerAngles_YXZ(LeftEThighAnat, EPelvisAnat)
        RightHipAnglesRad = math.EulerAngles_YXZ(RightEThighAnat, EPelvisAnat)
        #Compute knee kinematics
        if self.ShankCoordinateSystem == 'Distal':
            LeftKneeAnglesRad = math.EulerAngles_YXZ(LeftEShankDistalAnat, LeftEThighAnat)    
            RightKneeAnglesRad = math.EulerAngles_YXZ(RightEShankDistalAnat, RightEThighAnat) 
        if self.ShankCoordinateSystem == 'Proximal':
            LeftKneeAnglesRad = math.EulerAngles_YXZ(LeftEShankProximalAnat, LeftEThighAnat)    
            RightKneeAnglesRad = math.EulerAngles_YXZ(RightEShankProximalAnat, RightEThighAnat) 
        #Compute ankle kinematics
        LeftAnkleAnglesRad = math.EulerAngles_YXZ(LeftEFootAnat, LeftEShankDistalAnat)
        RightAnkleAnglesRad = math.EulerAngles_YXZ(RightEFootAnat, RightEShankDistalAnat)
        #Compute Left Foot kinematics
        if self.valueLeftFootModelCheck == '1':
            LeftHindfootAnglesRad = math.EulerAngles_ZYX(LeftEHindfootAnat,ELab)
            LeftForefootAnglesRad = math.EulerAngles_ZYX(LeftEForefootAnat,ELab)            
            #LeftHindfootAnglesRad = math.EulerAngles_YXZ(LeftEHindfootAnat,ELab)
            #LeftForefootAnglesRad = math.EulerAngles_YXZ(LeftEForefootAnat,ELab)
            LeftHalluxAnglesRad   = math.EulerAngles_YXZ(LeftEHalluxAnat,ELab)
            LeftAnkleComplexAnglesRad = math.EulerAngles_YXZ(LeftEHindfootAnat,LeftEShankDistalAnat)
            LeftMidfootAnglesRad = math.EulerAngles_YXZ(LeftEForefootAnat,LeftEHindfootAnat)
            LeftToesAnglesRad = math.EulerAngles_YXZ(LeftEHalluxAnat,LeftEForefootAnat)
            #print LeftHindfootAnglesRad
            #print LeftForefootAnglesRad
            #print LeftHalluxAnglesRad
            #print LeftAnkleComplexAnglesRad
            #print LeftMidfootAnglesRad
            #print LeftToesAnglesRad
        #Compute Right Foot kinematics
        if self.valueRightFootModelCheck == '1':
            RightHindfootAnglesRad = math.EulerAngles_ZYX(RightEHindfootAnat,ELab)
            RightForefootAnglesRad = math.EulerAngles_ZYX(RightEForefootAnat,ELab)
            #RightHindfootAnglesRad = math.EulerAngles_YXZ(RightEHindfootAnat,ELab)
            #RightForefootAnglesRad = math.EulerAngles_YXZ(RightEForefootAnat,ELab)
            RightHalluxAnglesRad   = math.EulerAngles_YXZ(RightEHalluxAnat,ELab)
            RightAnkleComplexAnglesRad = math.EulerAngles_YXZ(RightEHindfootAnat,RightEShankDistalAnat)
            RightMidfootAnglesRad = math.EulerAngles_YXZ(RightEForefootAnat,RightEHindfootAnat)
            RightToesAnglesRad = math.EulerAngles_YXZ(RightEHalluxAnat,RightEForefootAnat)
            #print RightHindfootAnglesRad
            #print RightForefootAnglesRad
            #print RightHalluxAnglesRad
            #print RightAnkleComplexAnglesRad
            #print RightMidfootAnglesRad
            #print RightToesAnglesRad   
#        print(TrunkAnglesRad)
#        print(PelvisAnglesRad)
#        print(LeftThighAnglesRad)
#        print(LeftShankAnglesRad)
#        print(LeftFootAnglesRad)
#        print(LeftHipAnglesRad)
#        print(LeftKneeAnglesRad)
#        print(LeftAnkleAnglesRad)
#        print(RightThighAnglesRad)
#        print(RightShankAnglesRad)
#        print(RightFootAnglesRad)
#        print(RightHipAnglesRad)
#        print(RightKneeAnglesRad)
#        print(RightAnkleAnglesRad)
        
        #Convert units of angles from radians to degrees & set sign based on side and plotting convention
        Sign = -1 # For Left Side
        
        T1, T1[0,0], T1[1,1], T1[2,2] = np.eye(3), -Sign, +1, Sign
        T2, T2[0,0], T2[1,1], T2[2,2] = np.eye(3),  Sign, -1, Sign
        T3, T3[0,0], T3[1,1], T3[2,2] = np.eye(3),  Sign, +1, Sign
        
        LeftTrunkAnglesDeg = T1.dot(TrunkAnglesRad) * 180 / np.pi 
        LeftPelvisAnglesDeg = T1.dot(PelvisAnglesRad) * 180 / np.pi
        LeftThighAnglesDeg = T1.dot(LeftThighAnglesRad) * 180 / np.pi
        LeftShankAnglesDeg = T1.dot(LeftShankAnglesRad) * 180 / np.pi
        LeftFootAnglesDeg = T1.dot(LeftFootAnglesRad) * 180 / np.pi
        LeftHipAnglesDeg = T2.dot(LeftHipAnglesRad) * 180 / np.pi
        LeftKneeAnglesDeg = T3.dot(LeftKneeAnglesRad) * 180 / np.pi
        LeftAnkleAnglesDeg = T2.dot(LeftAnkleAnglesRad) * 180 / np.pi
        if self.valueLeftFootModelCheck == '1':
            LeftHindfootAnglesDeg = T1.dot(LeftHindfootAnglesRad) * 180 / np.pi 
            LeftForefootAnglesDeg = T1.dot(LeftForefootAnglesRad) * 180 / np.pi 
            LeftHalluxAnglesDeg   = T1.dot(LeftHalluxAnglesRad) * 180 / np.pi 
            LeftAnkleComplexAnglesDeg = T2.dot(LeftAnkleComplexAnglesRad) * 180 / np.pi 
            LeftMidfootAnglesDeg = T2.dot(LeftMidfootAnglesRad) * 180 / np.pi 
            LeftToesAnglesDeg = T2.dot(LeftToesAnglesRad) * 180 / np.pi 
        #print(LeftTrunkAnglesDeg)
        #print(LeftPelvisAnglesDeg)
        #print(LeftThighAnglesDeg)
        #print(LeftShankAnglesDeg)
        #print(LeftFootAnglesDeg)
        #print(LeftHipAnglesDeg)
        #print(LeftKneeAnglesDeg)
        #print(LeftAnkleAnglesDeg)
        
        Sign = 1 #For Right Side
        
        T1, T1[0,0], T1[1,1], T1[2,2] = np.eye(3), -Sign, +1, Sign
        T2, T2[0,0], T2[1,1], T2[2,2] = np.eye(3),  Sign, -1, Sign
        T3, T3[0,0], T3[1,1], T3[2,2] = np.eye(3),  Sign, +1, Sign
        
        RightTrunkAnglesDeg = T1.dot(TrunkAnglesRad) * 180 / np.pi 
        RightPelvisAnglesDeg = T1.dot(PelvisAnglesRad) * 180 / np.pi
        RightThighAnglesDeg = T1.dot(RightThighAnglesRad) * 180 / np.pi
        RightShankAnglesDeg = T1.dot(RightShankAnglesRad) * 180 / np.pi
        RightFootAnglesDeg = T1.dot(RightFootAnglesRad) * 180 / np.pi
        RightHipAnglesDeg = T2.dot(RightHipAnglesRad) * 180 / np.pi
        RightKneeAnglesDeg = T3.dot(RightKneeAnglesRad) * 180 / np.pi
        RightAnkleAnglesDeg = T2.dot(RightAnkleAnglesRad) * 180 / np.pi
        if self.valueRightFootModelCheck == '1':
            RightHindfootAnglesDeg = T1.dot(RightHindfootAnglesRad) * 180 / np.pi 
            RightForefootAnglesDeg = T1.dot(RightForefootAnglesRad) * 180 / np.pi 
            RightHalluxAnglesDeg   = T1.dot(RightHalluxAnglesRad) * 180 / np.pi 
            RightAnkleComplexAnglesDeg = T2.dot(RightAnkleComplexAnglesRad) * 180 / np.pi 
            RightMidfootAnglesDeg = T2.dot(RightMidfootAnglesRad) * 180 / np.pi 
            RightToesAnglesDeg = T2.dot(RightToesAnglesRad) * 180 / np.pi 
        #print(RightTrunkAnglesDeg)
        #print(RightPelvisAnglesDeg)
        #print(RightThighAnglesDeg)
        #print(RightShankAnglesDeg)
        #print(RightFootAnglesDeg)
        #print(RightHipAnglesDeg)
        #print(RightKneeAnglesDeg)
        #print(RightAnkleAnglesDeg)
        
        
        #Compute Ankle Plantar/Dorsiflexion based on the ankle-to-knee center axis and long axis of foot
        LeftAnkleKneeVector = math.ComputeUnitVecFromPts(LeftAnkleCenterLab, LeftKneeCenterLab)
        LeftEFootAnatX = np.array((LeftEFootAnat[0][0],LeftEFootAnat[1][0],LeftEFootAnat[2][0])) 
        LeftAnkleAnglesDeg[1] = 90 - np.arccos(np.dot(LeftAnkleKneeVector,LeftEFootAnatX)) * 180 / np.pi
        RightAnkleKneeVector = math.ComputeUnitVecFromPts(RightAnkleCenterLab, RightKneeCenterLab)
        RightEFootAnatX = np.array((RightEFootAnat[0][0],RightEFootAnat[1][0],RightEFootAnat[2][0])) 
        RightAnkleAnglesDeg[1] = 90 - np.arccos(np.dot(RightAnkleKneeVector,RightEFootAnatX)) * 180 / np.pi
        #print(LeftAnkleAnglesDeg[1])
        #print(RightAnkleAnglesDeg[1])
        
        #Compute Foot Progression as the sin of the angle between long axis of foot and the y-axis of lab
        LeftFootAnglesDeg[2] = -1 * np.arcsin(LeftEFootAnat[1][0]) * 180 / np.pi
        RightFootAnglesDeg[2] =  1 * np.arcsin(RightEFootAnat[1][0]) * 180 / np.pi
        #print(LeftFootAnglesDeg[2])
        #print(RightFootAnglesDeg[2])
        
        #Compute Tibial Torsion based on the Ankle Flexion-Extension Axis
        LeftTibialTorsion = gait.Compute_TibialTorsion('Left', LeftEShankProximalAnat, LeftLateralAnkleMarker, LeftMedialAnkleMarker)
        RightTibialTorsion = gait.Compute_TibialTorsion('Right', RightEShankProximalAnat, RightLateralAnkleMarker, RightMedialAnkleMarker)
        #print(LeftTibialTorsion)
        #print(RightTibialTorsion)
        
        
# =============================================================================
#       Fille in Posture Display Measurements
# =============================================================================
        # Left
        if TrunkFlag == 1:
            if round(LeftTrunkAnglesDeg[0], 0) > 0:
                LeftTrunkObliquity.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[0], 0)))) +  " Up")
            if round(LeftTrunkAnglesDeg[0], 0) < 0:
                LeftTrunkObliquity.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[0], 0)))) +  " Down")
            if round(LeftTrunkAnglesDeg[0], 0) == 0:
                LeftTrunkObliquity.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[0], 0)))) +  "")
            if round(LeftTrunkAnglesDeg[1], 0) > 0:
                LeftTrunkTilt.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[1], 0)))) +  " Forw")
            if round(LeftTrunkAnglesDeg[1], 0) < 0:
                LeftTrunkTilt.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[1], 0)))) +  " Back")
            if round(LeftTrunkAnglesDeg[1], 0) == 0:
                LeftTrunkTilt.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[1], 0)))) +  "")
            if round(LeftTrunkAnglesDeg[2], 0) > 0:
                LeftTrunkRotation.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[2], 0)))) +  " Int")
            if round(LeftTrunkAnglesDeg[2], 0) < 0:
                LeftTrunkRotation.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[2], 0)))) +  " Ext")
            if round(LeftTrunkAnglesDeg[2], 0) == 0:
                LeftTrunkRotation.insert(0, str(int(abs(round(LeftTrunkAnglesDeg[2], 0)))) +  "")
            
        if round(LeftPelvisAnglesDeg[0], 0) > 0:
            LeftPelvisObliquity.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[0], 0)))) +  " Up")
        if round(LeftPelvisAnglesDeg[0], 0) < 0:
            LeftPelvisObliquity.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[0], 0)))) +  " Down")
        if round(LeftPelvisAnglesDeg[0], 0) == 0:
            LeftPelvisObliquity.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[0], 0)))) +  "")
        if round(LeftPelvisAnglesDeg[1], 0) > 0:
            LeftPelvisTilt.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[1], 0)))) +  " Ant")
        if round(LeftPelvisAnglesDeg[1], 0) < 0:
            LeftPelvisTilt.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[1], 0)))) +  " Post")
        if round(LeftPelvisAnglesDeg[1], 0) == 0:
            LeftPelvisTilt.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[1], 0)))) +  "")
        if round(LeftPelvisAnglesDeg[2], 0) > 0:
            LeftPelvisRotation.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[2], 0)))) +  " Int")
        if round(LeftPelvisAnglesDeg[2], 0) < 0:
            LeftPelvisRotation.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftPelvisAnglesDeg[2], 0) == 0:
            LeftPelvisRotation.insert(0, str(int(abs(round(LeftPelvisAnglesDeg[2], 0)))) +  "")
        
        if round(LeftHipAnglesDeg[0], 0) > 0:
            LeftHipAbAdduction.insert(0, str(int(abs(round(LeftHipAnglesDeg[0], 0)))) +  " Add")
        if round(LeftHipAnglesDeg[0], 0) < 0:
            LeftHipAbAdduction.insert(0, str(int(abs(round(LeftHipAnglesDeg[0], 0)))) +  " Abd")
        if round(LeftHipAnglesDeg[0], 0) == 0:
            LeftHipAbAdduction.insert(0, str(int(abs(round(LeftHipAnglesDeg[0], 0)))) +  "")
        if round(LeftHipAnglesDeg[1], 0) > 0:
            LeftHipFlexExtension.insert(0, str(int(abs(round(LeftHipAnglesDeg[1], 0)))) +  " Flex")
        if round(LeftHipAnglesDeg[1], 0) < 0:
            LeftHipFlexExtension.insert(0, str(int(abs(round(LeftHipAnglesDeg[1], 0)))) +  " Ext")
        if round(LeftHipAnglesDeg[1], 0) == 0:
            LeftHipFlexExtension.insert(0, str(int(abs(round(LeftHipAnglesDeg[1], 0)))) +  "")
        if round(LeftHipAnglesDeg[2], 0) > 0:
            LeftHipIntExtRotation.insert(0, str(int(abs(round(LeftHipAnglesDeg[2], 0)))) +  " Int")
        if round(LeftHipAnglesDeg[2], 0) < 0:
            LeftHipIntExtRotation.insert(0, str(int(abs(round(LeftHipAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftHipAnglesDeg[2], 0) == 0:
            LeftHipIntExtRotation.insert(0, str(int(abs(round(LeftHipAnglesDeg[2], 0)))) +  "")

        if round(LeftKneeAnglesDeg[0], 0) > 0:
            LeftKneeVarusValgus.insert(0, str(int(abs(round(LeftKneeAnglesDeg[0], 0)))) +  " Var")
        if round(LeftKneeAnglesDeg[0], 0) < 0:
            LeftKneeVarusValgus.insert(0, str(int(abs(round(LeftKneeAnglesDeg[0], 0)))) +  " Val")
        if round(LeftKneeAnglesDeg[0], 0) == 0:
            LeftKneeVarusValgus.insert(0, str(int(abs(round(LeftKneeAnglesDeg[0], 0)))) +  "")
        if round(LeftKneeAnglesDeg[1], 0) > 0:
            LeftKneeFlexExtension.insert(0, str(int(abs(round(LeftKneeAnglesDeg[1], 0)))) +  " Flex")
        if round(LeftKneeAnglesDeg[1], 0) < 0:
            LeftKneeFlexExtension.insert(0, str(int(abs(round(LeftKneeAnglesDeg[1], 0)))) +  " Ext")
        if round(LeftKneeAnglesDeg[1], 0) == 0:
            LeftKneeFlexExtension.insert(0, str(int(abs(round(LeftKneeAnglesDeg[1], 0)))) +  "")
        if round(LeftKneeAnglesDeg[2], 0) > 0:
            LeftKneeIntExtRotation.insert(0, str(int(abs(round(LeftKneeAnglesDeg[2], 0)))) +  " Int")
        if round(LeftKneeAnglesDeg[2], 0) < 0:
            LeftKneeIntExtRotation.insert(0, str(int(abs(round(LeftKneeAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftKneeAnglesDeg[2], 0) == 0:
            LeftKneeIntExtRotation.insert(0, str(int(abs(round(LeftKneeAnglesDeg[2], 0)))) +  "")
        
        if round(LeftThighAnglesDeg[2], 0) > 0:
            LeftKneeProgression.insert(0, str(int(abs(round(LeftThighAnglesDeg[2], 0)))) +  " Int")
        if round(LeftThighAnglesDeg[2], 0) < 0:
            LeftKneeProgression.insert(0, str(int(abs(round(LeftThighAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftThighAnglesDeg[2], 0) == 0:
            LeftKneeProgression.insert(0, str(int(abs(round(LeftThighAnglesDeg[2], 0)))) +  "")
        
        if round(LeftAnkleAnglesDeg[1], 0) > 0:
            LeftAnklePlantarDorsiflexion.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[1], 0)))) +  " Dorsi")
        if round(LeftAnkleAnglesDeg[1], 0) < 0:
            LeftAnklePlantarDorsiflexion.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[1], 0)))) +  " Plant")
        if round(LeftAnkleAnglesDeg[1], 0) == 0:
            LeftAnklePlantarDorsiflexion.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[1], 0)))) +  "")
        if round(LeftAnkleAnglesDeg[2], 0) > 0:
            LeftAnkleIntExtRotation.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[2], 0)))) +  " Int")
        if round(LeftAnkleAnglesDeg[2], 0) < 0:
            LeftAnkleIntExtRotation.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftAnkleAnglesDeg[2], 0) == 0:
            LeftAnkleIntExtRotation.insert(0, str(int(abs(round(LeftAnkleAnglesDeg[2], 0)))) +  "")

        if round(LeftFootAnglesDeg[2], 0) > 0:
            LeftFootProgression.insert(0, str(int(abs(round(LeftFootAnglesDeg[2], 0)))) +  " Int")
        if round(LeftFootAnglesDeg[2], 0) < 0:
            LeftFootProgression.insert(0, str(int(abs(round(LeftFootAnglesDeg[2], 0)))) +  " Ext")
        if round(LeftFootAnglesDeg[2], 0) == 0:
            LeftFootProgression.insert(0, str(int(abs(round(LeftFootAnglesDeg[2], 0)))) +  "")
            
        if round(LeftTibialTorsion, 0) > 0:
            LeftTibiaTorsion.insert(0, str(int(abs(round(LeftTibialTorsion, 0)))) +  " Ext")
        if round(LeftTibialTorsion, 0) < 0:
            LeftTibiaTorsion.insert(0, str(int(abs(round(LeftTibialTorsion, 0)))) +  " Int")
        if round(LeftTibialTorsion, 0) == 0:
            LeftTibiaTorsion.insert(0, str(int(abs(round(LeftTibialTorsion, 0)))) +  "")
        
        if self.valueLeftFootModelCheck == '1':
            if round(LeftHindfootAnglesDeg[0], 0) > 0:
                LeftHindfootInvEversion.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[0], 0)))) +  " Val")
            if round(LeftHindfootAnglesDeg[0], 0) < 0:
                LeftHindfootInvEversion.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[0], 0)))) +  " Var")
            if round(LeftHindfootAnglesDeg[0], 0) == 0:
                LeftHindfootInvEversion.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[0], 0)))) +  "")
            if round(LeftHindfootAnglesDeg[1], 0) > 0:
                LeftHindfootPitch.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[1], 0)))) +  " Down")
            if round(LeftHindfootAnglesDeg[1], 0) < 0:
                LeftHindfootPitch.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[1], 0)))) +  " Up")
            if round(LeftHindfootAnglesDeg[1], 0) == 0:
                LeftHindfootPitch.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[1], 0)))) +  "")
            if round(LeftHindfootAnglesDeg[2], 0) > 0:
                LeftHindfootProgression.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[2], 0)))) +  " Int")
            if round(LeftHindfootAnglesDeg[2], 0) < 0:
                LeftHindfootProgression.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[2], 0)))) +  " Ext")
            if round(LeftHindfootAnglesDeg[2], 0) == 0:
                LeftHindfootProgression.insert(0, str(int(abs(round(LeftHindfootAnglesDeg[2], 0)))) +  "")
                
            if round(LeftAnkleComplexAnglesDeg[0], 0) > 0:
                LeftAnkleComplexInvEversion.insert(0, str(int(abs(round(LeftAnkleComplexAnglesDeg[0], 0)))) +  " Var")
            if round(LeftAnkleComplexAnglesDeg[0], 0) < 0:
                LeftAnkleComplexInvEversion.insert(0, str(int(abs(round(LeftAnkleComplexAnglesDeg[0], 0)))) +  " Val")
            if round(LeftAnkleComplexAnglesDeg[0], 0) == 0:
                LeftAnkleComplexInvEversion.insert(0, str(int(abs(round(LeftAnkleComplexAnglesDeg[0], 0)))) +  "")
            
#            if round(LeftForefootAnglesDeg[0], 0) > 0:
#                LeftForefootInvEversion.insert(0, str(int(abs(round(LeftForefootAnglesDeg[0], 0)))) +  " Inv")
#            if round(LeftForefootAnglesDeg[0], 0) < 0:
#                LeftForefootInvEversion.insert(0, str(int(abs(round(LeftForefootAnglesDeg[0], 0)))) +  " Ev")
#            if round(LeftForefootAnglesDeg[0], 0) == 0:
#                LeftForefootInvEversion.insert(0, str(int(abs(round(LeftForefootAnglesDeg[0], 0)))) +  "")
            if round(LeftForefootAnglesDeg[1], 0) > 0:
                LeftForefootPitch.insert(0, str(int(abs(round(LeftForefootAnglesDeg[1], 0)))) +  " Down")
            if round(LeftForefootAnglesDeg[1], 0) < 0:
                LeftForefootPitch.insert(0, str(int(abs(round(LeftForefootAnglesDeg[1], 0)))) +  " Up")
            if round(LeftForefootAnglesDeg[1], 0) == 0:
                LeftForefootPitch.insert(0, str(int(abs(round(LeftForefootAnglesDeg[1], 0)))) +  "")
            if round(LeftForefootAnglesDeg[2], 0) > 0:
                LeftForefootProgression.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2], 0)))) +  " Int")
            if round(LeftForefootAnglesDeg[2], 0) < 0:
                LeftForefootProgression.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2], 0)))) +  " Ext")
            if round(LeftForefootAnglesDeg[2], 0) == 0:
                LeftForefootProgression.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2], 0)))) +  "")
 
    
            if round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0) > 0:
                LeftMidfootAbAdduction.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0)))) +  " Add")
            if round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0) < 0:
                LeftMidfootAbAdduction.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0)))) +  " Abd")
            if round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0) == 0:
                LeftMidfootAbAdduction.insert(0, str(int(abs(round(LeftForefootAnglesDeg[2] - LeftHindfootAnglesDeg[2], 0)))) +  "")
                
            if round(LeftHalluxAnglesDeg[2], 0) > 0:
                LeftHalluxProgression.insert(0, str(int(abs(round(LeftToesAnglesDeg[2], 0)))) +  " Var")
            if round(LeftHalluxAnglesDeg[2], 0) < 0:
                LeftHalluxProgression.insert(0, str(int(abs(round(LeftToesAnglesDeg[2], 0)))) +  " Val")
            if round(LeftHalluxAnglesDeg[2], 0) == 0:
                LeftHalluxProgression.insert(0, str(int(abs(round(LeftToesAnglesDeg[2], 0)))) +  "")
            
        #Right
        if TrunkFlag == 1:
            if round(RightTrunkAnglesDeg[0], 0) > 0:
                RightTrunkObliquity.insert(0, str(int(abs(round(RightTrunkAnglesDeg[0], 0)))) +  " Up")
            if round(RightTrunkAnglesDeg[0], 0) < 0:
                RightTrunkObliquity.insert(0, str(int(abs(round(RightTrunkAnglesDeg[0], 0)))) +  " Down")
            if round(RightTrunkAnglesDeg[0], 0) == 0:
                RightTrunkObliquity.insert(0, str(int(abs(round(RightTrunkAnglesDeg[0], 0)))) +  "")
            if round(RightTrunkAnglesDeg[1], 0) > 0:
                RightTrunkTilt.insert(0, str(int(abs(round(RightTrunkAnglesDeg[1], 0)))) +  " Forw")
            if round(RightTrunkAnglesDeg[1], 0) < 0:
                RightTrunkTilt.insert(0, str(int(abs(round(RightTrunkAnglesDeg[1], 0)))) +  " Back")
            if round(RightTrunkAnglesDeg[1], 0) == 0:
                RightTrunkTilt.insert(0, str(int(abs(round(RightTrunkAnglesDeg[1], 0)))) +  "")
            if round(RightTrunkAnglesDeg[2], 0) > 0:
                RightTrunkRotation.insert(0, str(int(abs(round(RightTrunkAnglesDeg[2], 0)))) +  " Int")
            if round(RightTrunkAnglesDeg[2], 0) < 0:
                RightTrunkRotation.insert(0, str(int(abs(round(RightTrunkAnglesDeg[2], 0)))) +  " Ext")
            if round(RightTrunkAnglesDeg[2], 0) == 0:
                RightTrunkRotation.insert(0, str(int(abs(round(RightTrunkAnglesDeg[2], 0)))) +  "")
            
        if round(RightPelvisAnglesDeg[0], 0) > 0:
            RightPelvisObliquity.insert(0, str(int(abs(round(RightPelvisAnglesDeg[0], 0)))) +  " Up")
        if round(RightPelvisAnglesDeg[0], 0) < 0:
            RightPelvisObliquity.insert(0, str(int(abs(round(RightPelvisAnglesDeg[0], 0)))) +  " Down")
        if round(RightPelvisAnglesDeg[0], 0) == 0:
            RightPelvisObliquity.insert(0, str(int(abs(round(RightPelvisAnglesDeg[0], 0)))) +  "")
        if round(RightPelvisAnglesDeg[1], 0) > 0:
            RightPelvisTilt.insert(0, str(int(abs(round(RightPelvisAnglesDeg[1], 0)))) +  " Ant")
        if round(RightPelvisAnglesDeg[1], 0) < 0:
            RightPelvisTilt.insert(0, str(int(abs(round(RightPelvisAnglesDeg[1], 0)))) +  " Post")
        if round(RightPelvisAnglesDeg[1], 0) == 0:
            RightPelvisTilt.insert(0, str(int(abs(round(RightPelvisAnglesDeg[1], 0)))) +  "")
        if round(RightPelvisAnglesDeg[2], 0) > 0:
            RightPelvisRotation.insert(0, str(int(abs(round(RightPelvisAnglesDeg[2], 0)))) +  " Int")
        if round(RightPelvisAnglesDeg[2], 0) < 0:
            RightPelvisRotation.insert(0, str(int(abs(round(RightPelvisAnglesDeg[2], 0)))) +  " Ext")
        if round(RightPelvisAnglesDeg[2], 0) == 0:
            RightPelvisRotation.insert(0, str(int(abs(round(RightPelvisAnglesDeg[2], 0)))) +  "")
        
        if round(RightHipAnglesDeg[0], 0) > 0:
            RightHipAbAdduction.insert(0, str(int(abs(round(RightHipAnglesDeg[0], 0)))) +  " Add")
        if round(RightHipAnglesDeg[0], 0) < 0:
            RightHipAbAdduction.insert(0, str(int(abs(round(RightHipAnglesDeg[0], 0)))) +  " Abd")
        if round(RightHipAnglesDeg[0], 0) == 0:
            RightHipAbAdduction.insert(0, str(int(abs(round(RightHipAnglesDeg[0], 0)))) +  "")
        if round(RightHipAnglesDeg[1], 0) > 0:
            RightHipFlexExtension.insert(0, str(int(abs(round(RightHipAnglesDeg[1], 0)))) +  " Flex")
        if round(RightHipAnglesDeg[1], 0) < 0:
            RightHipFlexExtension.insert(0, str(int(abs(round(RightHipAnglesDeg[1], 0)))) +  " Ext")
        if round(RightHipAnglesDeg[1], 0) == 0:
            RightHipFlexExtension.insert(0, str(int(abs(round(RightHipAnglesDeg[1], 0)))) +  "")
        if round(RightHipAnglesDeg[2], 0) > 0:
            RightHipIntExtRotation.insert(0, str(int(abs(round(RightHipAnglesDeg[2], 0)))) +  " Int")
        if round(RightHipAnglesDeg[2], 0) < 0:
            RightHipIntExtRotation.insert(0, str(int(abs(round(RightHipAnglesDeg[2], 0)))) +  " Ext")
        if round(RightHipAnglesDeg[2], 0) == 0:
            RightHipIntExtRotation.insert(0, str(int(abs(round(RightHipAnglesDeg[2], 0)))) +  "")

        if round(RightKneeAnglesDeg[0], 0) > 0:
            RightKneeVarusValgus.insert(0, str(int(abs(round(RightKneeAnglesDeg[0], 0)))) +  " Var")
        if round(RightKneeAnglesDeg[0], 0) < 0:
            RightKneeVarusValgus.insert(0, str(int(abs(round(RightKneeAnglesDeg[0], 0)))) +  " Val")
        if round(RightKneeAnglesDeg[0], 0) == 0:
            RightKneeVarusValgus.insert(0, str(int(abs(round(RightKneeAnglesDeg[0], 0)))) +  "")
        if round(RightKneeAnglesDeg[1], 0) > 0:
            RightKneeFlexExtension.insert(0, str(int(abs(round(RightKneeAnglesDeg[1], 0)))) +  " Flex")
        if round(RightKneeAnglesDeg[1], 0) < 0:
            RightKneeFlexExtension.insert(0, str(int(abs(round(RightKneeAnglesDeg[1], 0)))) +  " Ext")
        if round(RightKneeAnglesDeg[1], 0) == 0:
            RightKneeFlexExtension.insert(0, str(int(abs(round(RightKneeAnglesDeg[1], 0)))) +  "")
        if round(RightKneeAnglesDeg[2], 0) > 0:
            RightKneeIntExtRotation.insert(0, str(int(abs(round(RightKneeAnglesDeg[2], 0)))) +  " Int")
        if round(RightKneeAnglesDeg[2], 0) < 0:
            RightKneeIntExtRotation.insert(0, str(int(abs(round(RightKneeAnglesDeg[2], 0)))) +  " Ext")
        if round(RightKneeAnglesDeg[2], 0) == 0:
            RightKneeIntExtRotation.insert(0, str(int(abs(round(RightKneeAnglesDeg[2], 0)))) +  "")

        if round(RightThighAnglesDeg[2], 0) > 0:
            RightKneeProgression.insert(0, str(int(abs(round(RightThighAnglesDeg[2], 0)))) +  " Int")
        if round(RightThighAnglesDeg[2], 0) < 0:
            RightKneeProgression.insert(0, str(int(abs(round(RightThighAnglesDeg[2], 0)))) +  " Ext")
        if round(RightThighAnglesDeg[2], 0) == 0:
            RightKneeProgression.insert(0, str(int(abs(round(RightThighAnglesDeg[2], 0)))) +  "")
            
        if round(RightAnkleAnglesDeg[1], 0) > 0:
            RightAnklePlantarDorsiflexion.insert(0, str(int(abs(round(RightAnkleAnglesDeg[1], 0)))) +  " Dorsi")
        if round(RightAnkleAnglesDeg[1], 0) < 0:
            RightAnklePlantarDorsiflexion.insert(0, str(int(abs(round(RightAnkleAnglesDeg[1], 0)))) +  " Plant")
        if round(RightAnkleAnglesDeg[1], 0) == 0:
            RightAnklePlantarDorsiflexion.insert(0, str(int(abs(round(RightAnkleAnglesDeg[1], 0)))) +  "")
        if round(RightAnkleAnglesDeg[2], 0) > 0:
            RightAnkleIntExtRotation.insert(0, str(int(abs(round(RightAnkleAnglesDeg[2], 0)))) +  " Int")
        if round(RightAnkleAnglesDeg[2], 0) < 0:
            RightAnkleIntExtRotation.insert(0, str(int(abs(round(RightAnkleAnglesDeg[2], 0)))) +  " Ext")
        if round(RightAnkleAnglesDeg[2], 0) == 0:
            RightAnkleIntExtRotation.insert(0, str(int(abs(round(RightAnkleAnglesDeg[2], 0)))) +  "")

        if round(RightFootAnglesDeg[2], 0) > 0:
            RightFootProgression.insert(0, str(int(abs(round(RightFootAnglesDeg[2], 0)))) +  " Int")
        if round(RightFootAnglesDeg[2], 0) < 0:
            RightFootProgression.insert(0, str(int(abs(round(RightFootAnglesDeg[2], 0)))) +  " Ext")
        if round(RightFootAnglesDeg[2], 0) == 0:
            RightFootProgression.insert(0, str(int(abs(round(RightFootAnglesDeg[2], 0)))) +  "")
            
        if round(RightTibialTorsion, 0) > 0:
            RightTibiaTorsion.insert(0, str(int(abs(round(RightTibialTorsion, 0)))) +  " Ext")
        if round(RightTibialTorsion, 0) < 0:
            RightTibiaTorsion.insert(0, str(int(abs(round(RightTibialTorsion, 0)))) +  " Int")
        if round(RightTibialTorsion, 0) == 0:
            RightTibiaTorsion.insert(0, str(int(abs(round(RightTibialTorsion, 0)))) +  "")

        if self.valueRightFootModelCheck == '1':
            if round(RightHindfootAnglesDeg[0], 0) > 0:
                RightHindfootInvEversion.insert(0, str(int(abs(round(RightHindfootAnglesDeg[0], 0)))) +  " Val")
            if round(RightHindfootAnglesDeg[0], 0) < 0:
                RightHindfootInvEversion.insert(0, str(int(abs(round(RightHindfootAnglesDeg[0], 0)))) +  " Var")
            if round(RightHindfootAnglesDeg[0], 0) == 0:
                RightHindfootInvEversion.insert(0, str(int(abs(round(RightHindfootAnglesDeg[0], 0)))) +  "")
            if round(RightHindfootAnglesDeg[1], 0) > 0:
                RightHindfootPitch.insert(0, str(int(abs(round(RightHindfootAnglesDeg[1], 0)))) +  " Down")
            if round(RightHindfootAnglesDeg[1], 0) < 0:
                RightHindfootPitch.insert(0, str(int(abs(round(RightHindfootAnglesDeg[1], 0)))) +  " Up")
            if round(RightHindfootAnglesDeg[1], 0) == 0:
                RightHindfootPitch.insert(0, str(int(abs(round(RightHindfootAnglesDeg[1], 0)))) +  "")
            if round(RightHindfootAnglesDeg[2], 0) > 0:
                RightHindfootProgression.insert(0, str(int(abs(round(RightHindfootAnglesDeg[2], 0)))) +  " Int")
            if round(RightHindfootAnglesDeg[2], 0) < 0:
                RightHindfootProgression.insert(0, str(int(abs(round(RightHindfootAnglesDeg[2], 0)))) +  " Ext")
            if round(RightHindfootAnglesDeg[2], 0) == 0:
                RightHindfootProgression.insert(0, str(int(abs(round(RightHindfootAnglesDeg[2], 0)))) +  "")
                
            if round(RightAnkleComplexAnglesDeg[0], 0) > 0:
                RightAnkleComplexInvEversion.insert(0, str(int(abs(round(RightAnkleComplexAnglesDeg[0], 0)))) +  " Var")
            if round(RightAnkleComplexAnglesDeg[0], 0) < 0:
                RightAnkleComplexInvEversion.insert(0, str(int(abs(round(RightAnkleComplexAnglesDeg[0], 0)))) +  " Val")
            if round(RightAnkleComplexAnglesDeg[0], 0) == 0:
                RightAnkleComplexInvEversion.insert(0, str(int(abs(round(RightAnkleComplexAnglesDeg[0], 0)))) +  "")
            
#            if round(RightForefootAnglesDeg[0], 0) > 0:
#                RightForefootInvEversion.insert(0, str(int(abs(round(RightForefootAnglesDeg[0], 0)))) +  " Inv")
#            if round(RightForefootAnglesDeg[0], 0) < 0:
#                RightForefootInvEversion.insert(0, str(int(abs(round(RightForefootAnglesDeg[0], 0)))) +  " Ev")
#            if round(RightForefootAnglesDeg[0], 0) == 0:
#                RightForefootInvEversion.insert(0, str(int(abs(round(RightForefootAnglesDeg[0], 0)))) +  "")
            if round(RightForefootAnglesDeg[1], 0) > 0:
                RightForefootPitch.insert(0, str(int(abs(round(RightForefootAnglesDeg[1], 0)))) +  " Down")
            if round(RightForefootAnglesDeg[1], 0) < 0:
                RightForefootPitch.insert(0, str(int(abs(round(RightForefootAnglesDeg[1], 0)))) +  " Up")
            if round(RightForefootAnglesDeg[1], 0) == 0:
                RightForefootPitch.insert(0, str(int(abs(round(RightForefootAnglesDeg[1], 0)))) +  "")
            if round(RightForefootAnglesDeg[2], 0) > 0:
                RightForefootProgression.insert(0, str(int(abs(round(RightForefootAnglesDeg[2], 0)))) +  " Int")
            if round(RightForefootAnglesDeg[2], 0) < 0:
                RightForefootProgression.insert(0, str(int(abs(round(RightForefootAnglesDeg[2], 0)))) +  " Ext")
            if round(RightForefootAnglesDeg[2], 0) == 0:
                RightForefootProgression.insert(0, str(int(abs(round(RightForefootAnglesDeg[2], 0)))) +  "")
                
            if round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0) > 0:
                RightMidfootAbAdduction.insert(0, str(int(abs(round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0)))) +  " Add")
            if round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0) < 0:
                RightMidfootAbAdduction.insert(0, str(int(abs(round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0)))) +  " Abd")
            if round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0) == 0:
                RightMidfootAbAdduction.insert(0, str(int(abs(round(RightForefootAnglesDeg[2] - RightHindfootAnglesDeg[2], 0)))) +  "")
 
            if round(RightHalluxAnglesDeg[2], 0) > 0:
                RightHalluxProgression.insert(0, str(int(abs(round(RightToesAnglesDeg[2], 0)))) +  " Var")
            if round(RightHalluxAnglesDeg[2], 0) < 0:
                RightHalluxProgression.insert(0, str(int(abs(round(RightToesAnglesDeg[2], 0)))) +  " Val")
            if round(RightHalluxAnglesDeg[2], 0) == 0:
                RightHalluxProgression.insert(0, str(int(abs(round(RightToesAnglesDeg[2], 0)))) +  "")
                
# =============================================================================
#       Function to save Transformation matrics in Static_BF_MRN.py file. It gets executed with 'Save Pdf' and 'Save Results' Button.
# =============================================================================
        def saveTransformationMatrices():
            # Read Current File
            StaticDataFile = open(StaticDataFileName,'r')
            lines=StaticDataFile.readlines()
            StaticDataFile.close()
            
            # Write Subject Data into Static Anthropometric File
            StaticDataFile = open(StaticDataFileName,'w+')
            # Rewrite Subject Information 
            TransformationMatricesBlockStarts = 0
            for line in lines:
                words=line.split()
                if words[0] == '#' and words[1] == 'Transformation':
                    TransformationMatricesBlockStarts = 1
                if TransformationMatricesBlockStarts == 0:
                    StaticDataFile.write(line)
            # Write Tranformation Matrices
            StaticDataFile.write('# Transformation Matrices' + '\n')
            
            StaticDataFile.write('self.valueLeftHipCenterPelvis = np.array([' + str(LeftHipCenterPelvis[0]) + "," + str(LeftHipCenterPelvis[1]) + ","  + str(LeftHipCenterPelvis[2])  + "])" + '\n')
            StaticDataFile.write('self.valueLeftKneeCenterThigh = np.array([' + str(LeftKneeCenterThigh[0]) + "," + str(LeftKneeCenterThigh[1]) + ","  + str(LeftKneeCenterThigh[2])  + "])" + '\n')
            StaticDataFile.write('self.valueLeftAnkleCenterShank = np.array([' + str(LeftAnkleCenterShank[0]) + "," + str(LeftAnkleCenterShank[1]) + ","  + str(LeftAnkleCenterShank[2])  + "])" + '\n')
            
            StaticDataFile.write('self.valueRightHipCenterPelvis = np.array([' + str(RightHipCenterPelvis[0]) + "," + str(RightHipCenterPelvis[1]) + ","  + str(RightHipCenterPelvis[2])  + "])" + '\n')
            StaticDataFile.write('self.valueRightKneeCenterThigh = np.array([' + str(RightKneeCenterThigh[0]) + "," + str(RightKneeCenterThigh[1]) + ","  + str(RightKneeCenterThigh[2])  + "])" + '\n')
            StaticDataFile.write('self.valueRightAnkleCenterShank = np.array([' + str(RightAnkleCenterShank[0]) + "," + str(RightAnkleCenterShank[1]) + ","  + str(RightAnkleCenterShank[2])  + "])" + '\n')
            
            # Write Tibial Torsion
            if round(LeftTibialTorsion, 0) > 0:
                StaticDataFile.write('self.valueLeftTibialTorsion =  ' + "'" + str(abs(round(LeftTibialTorsion, 2))) +  " Ext" + "'" + '\n')
            if round(LeftTibialTorsion, 0) < 0:
                StaticDataFile.write('self.valueLeftTibialTorsion =  ' +  "'" + str(abs(round(LeftTibialTorsion, 2))) +  " Int"+ "'" + '\n')
            if round(LeftTibialTorsion, 0) == 0:
                StaticDataFile.write('self.valueLeftTibialTorsion =  ' + "'" + str(abs(round(LeftTibialTorsion, 2))) +  ""+ "'" + '\n')
            
            if round(RightTibialTorsion, 0) > 0:
                StaticDataFile.write('self.valueRightTibialTorsion =  ' + "'" + str(abs(round(RightTibialTorsion, 2))) +  " Ext"+ "'" + '\n')
            if round(RightTibialTorsion, 0) < 0:
                StaticDataFile.write('self.valueRightTibialTorsion =  ' + "'" + str(abs(round(RightTibialTorsion, 2))) +  " Int"+ "'" + '\n')
            if round(RightTibialTorsion, 0) == 0:
                StaticDataFile.write('self.valueRightTibialTorsion =  ' + "'" + str(abs(round(RightTibialTorsion, 2))) +  ""+ "'" + '\n')
 
                                 
            StaticDataFile.write('self.valueETrunkAnatRelTech = np.array([[' + str(ETrunkAnatRelTech[0,0]) + "," + str(ETrunkAnatRelTech[0,1]) + ","  + str(ETrunkAnatRelTech[0,2])  + "],[" +
                                                                          str(ETrunkAnatRelTech[1,0]) + "," + str(ETrunkAnatRelTech[1,1]) + ","  + str(ETrunkAnatRelTech[1,2]) + "],[" +
                                                                          str(ETrunkAnatRelTech[2,0]) + "," + str(ETrunkAnatRelTech[2,1]) + ","  + str(ETrunkAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueEPelvisAnatRelTech = np.array([[' + str(EPelvisAnatRelTech[0,0]) + "," + str(EPelvisAnatRelTech[0,1]) + ","  + str(EPelvisAnatRelTech[0,2])  + "],[" +
                                                                          str(EPelvisAnatRelTech[1,0]) + "," + str(EPelvisAnatRelTech[1,1]) + ","  + str(EPelvisAnatRelTech[1,2]) + "],[" +
                                                                          str(EPelvisAnatRelTech[2,0]) + "," + str(EPelvisAnatRelTech[2,1]) + ","  + str(EPelvisAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueLeftEThighAnatRelTech = np.array([[' + str(LeftEThighAnatRelTech[0,0]) + "," + str(LeftEThighAnatRelTech[0,1]) + ","  + str(LeftEThighAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEThighAnatRelTech[1,0]) + "," + str(LeftEThighAnatRelTech[1,1]) + ","  + str(LeftEThighAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEThighAnatRelTech[2,0]) + "," + str(LeftEThighAnatRelTech[2,1]) + ","  + str(LeftEThighAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueLeftEShankProximalAnatRelTech = np.array([[' + str(LeftEShankProximalAnatRelTech[0,0]) + "," + str(LeftEShankProximalAnatRelTech[0,1]) + ","  + str(LeftEShankProximalAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEShankProximalAnatRelTech[1,0]) + "," + str(LeftEShankProximalAnatRelTech[1,1]) + ","  + str(LeftEShankProximalAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEShankProximalAnatRelTech[2,0]) + "," + str(LeftEShankProximalAnatRelTech[2,1]) + ","  + str(LeftEShankProximalAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueLeftEShankDistalAnatRelTech = np.array([[' + str(LeftEShankDistalAnatRelTech[0,0]) + "," + str(LeftEShankDistalAnatRelTech[0,1]) + ","  + str(LeftEShankDistalAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEShankDistalAnatRelTech[1,0]) + "," + str(LeftEShankDistalAnatRelTech[1,1]) + ","  + str(LeftEShankDistalAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEShankDistalAnatRelTech[2,0]) + "," + str(LeftEShankDistalAnatRelTech[2,1]) + ","  + str(LeftEShankDistalAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueLeftEFootAnatRelTech = np.array([[' + str(LeftEFootAnatRelTech[0,0]) + "," + str(LeftEFootAnatRelTech[0,1]) + ","  + str(LeftEFootAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEFootAnatRelTech[1,0]) + "," + str(LeftEFootAnatRelTech[1,1]) + ","  + str(LeftEFootAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEFootAnatRelTech[2,0]) + "," + str(LeftEFootAnatRelTech[2,1]) + ","  + str(LeftEFootAnatRelTech[2,2]) + "]])" + '\n')
            StaticDataFile.write('self.valueLeftEFootAnat2RelTech = np.array([[' + str(LeftEFootAnat2RelTech[0,0]) + "," + str(LeftEFootAnat2RelTech[0,1]) + ","  + str(LeftEFootAnat2RelTech[0,2])  + "],[" +
                                                                          str(LeftEFootAnat2RelTech[1,0]) + "," + str(LeftEFootAnat2RelTech[1,1]) + ","  + str(LeftEFootAnat2RelTech[1,2]) + "],[" +
                                                                          str(LeftEFootAnat2RelTech[2,0]) + "," + str(LeftEFootAnat2RelTech[2,1]) + ","  + str(LeftEFootAnat2RelTech[2,2]) + "]])" + '\n')
            
            if self.valueLeftFootModelCheck == '1':
                StaticDataFile.write('self.valueLeftEHindfootAnatRelTech = np.array([[' + str(LeftEHindfootAnatRelTech[0,0]) + "," + str(LeftEHindfootAnatRelTech[0,1]) + ","  + str(LeftEHindfootAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEHindfootAnatRelTech[1,0]) + "," + str(LeftEHindfootAnatRelTech[1,1]) + ","  + str(LeftEHindfootAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEHindfootAnatRelTech[2,0]) + "," + str(LeftEHindfootAnatRelTech[2,1]) + ","  + str(LeftEHindfootAnatRelTech[2,2]) + "]])" + '\n')
    
                StaticDataFile.write('self.valueLeftEForefootAnatRelTech = np.array([[' + str(LeftEForefootAnatRelTech[0,0]) + "," + str(LeftEForefootAnatRelTech[0,1]) + ","  + str(LeftEForefootAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEForefootAnatRelTech[1,0]) + "," + str(LeftEForefootAnatRelTech[1,1]) + ","  + str(LeftEForefootAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEForefootAnatRelTech[2,0]) + "," + str(LeftEForefootAnatRelTech[2,1]) + ","  + str(LeftEForefootAnatRelTech[2,2]) + "]])" + '\n')
    
                StaticDataFile.write('self.valueLeftEHalluxAnatRelTech = np.array([[' + str(LeftEHalluxAnatRelTech[0,0]) + "," + str(LeftEHalluxAnatRelTech[0,1]) + ","  + str(LeftEHalluxAnatRelTech[0,2])  + "],[" +
                                                                          str(LeftEHalluxAnatRelTech[1,0]) + "," + str(LeftEHalluxAnatRelTech[1,1]) + ","  + str(LeftEHalluxAnatRelTech[1,2]) + "],[" +
                                                                          str(LeftEHalluxAnatRelTech[2,0]) + "," + str(LeftEHalluxAnatRelTech[2,1]) + ","  + str(LeftEHalluxAnatRelTech[2,2]) + "]])" + '\n')
                
                StaticDataFile.write('self.valueLeft23MetatarsalHeadMarkerForefoot = np.array([' + str(Left23MetatarsalHeadMarkerForefoot[0]) + "," + str(Left23MetatarsalHeadMarkerForefoot[1]) + "," + str(Left23MetatarsalHeadMarkerForefoot[2]) + "])" +'\n')
                StaticDataFile.write('self.valueLeftFirstMetatarsoPhalangealJointMarkerForefoot = np.array([' + str(LeftFirstMetatarsoPhalangealJointMarkerForefoot[0]) + "," + str(LeftFirstMetatarsoPhalangealJointMarkerForefoot[1]) + "," + str(LeftFirstMetatarsoPhalangealJointMarkerForefoot[2]) + "])" +'\n')

    
            StaticDataFile.write('self.valueRightEThighAnatRelTech = np.array([[' + str(RightEThighAnatRelTech[0,0]) + "," + str(RightEThighAnatRelTech[0,1]) + ","  + str(RightEThighAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEThighAnatRelTech[1,0]) + "," + str(RightEThighAnatRelTech[1,1]) + ","  + str(RightEThighAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEThighAnatRelTech[2,0]) + "," + str(RightEThighAnatRelTech[2,1]) + ","  + str(RightEThighAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueRightEShankProximalAnatRelTech = np.array([[' + str(RightEShankProximalAnatRelTech[0,0]) + "," + str(RightEShankProximalAnatRelTech[0,1]) + ","  + str(RightEShankProximalAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEShankProximalAnatRelTech[1,0]) + "," + str(RightEShankProximalAnatRelTech[1,1]) + ","  + str(RightEShankProximalAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEShankProximalAnatRelTech[2,0]) + "," + str(RightEShankProximalAnatRelTech[2,1]) + ","  + str(RightEShankProximalAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueRightEShankDistalAnatRelTech = np.array([[' + str(RightEShankDistalAnatRelTech[0,0]) + "," + str(RightEShankDistalAnatRelTech[0,1]) + ","  + str(RightEShankDistalAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEShankDistalAnatRelTech[1,0]) + "," + str(RightEShankDistalAnatRelTech[1,1]) + ","  + str(RightEShankDistalAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEShankDistalAnatRelTech[2,0]) + "," + str(RightEShankDistalAnatRelTech[2,1]) + ","  + str(RightEShankDistalAnatRelTech[2,2]) + "]])" + '\n')
            
            StaticDataFile.write('self.valueRightEFootAnatRelTech = np.array([[' + str(RightEFootAnatRelTech[0,0]) + "," + str(RightEFootAnatRelTech[0,1]) + ","  + str(RightEFootAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEFootAnatRelTech[1,0]) + "," + str(RightEFootAnatRelTech[1,1]) + ","  + str(RightEFootAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEFootAnatRelTech[2,0]) + "," + str(RightEFootAnatRelTech[2,1]) + ","  + str(RightEFootAnatRelTech[2,2]) + "]])" + '\n')
            StaticDataFile.write('self.valueRightEFootAnat2RelTech = np.array([[' + str(RightEFootAnat2RelTech[0,0]) + "," + str(RightEFootAnat2RelTech[0,1]) + ","  + str(RightEFootAnat2RelTech[0,2])  + "],[" +
                                                                          str(RightEFootAnat2RelTech[1,0]) + "," + str(RightEFootAnat2RelTech[1,1]) + ","  + str(RightEFootAnat2RelTech[1,2]) + "],[" +
                                                                          str(RightEFootAnat2RelTech[2,0]) + "," + str(RightEFootAnat2RelTech[2,1]) + ","  + str(RightEFootAnat2RelTech[2,2]) + "]])" + '\n')
            if self.valueRightFootModelCheck == '1':
                StaticDataFile.write('self.valueRightEHindfootAnatRelTech = np.array([[' + str(RightEHindfootAnatRelTech[0,0]) + "," + str(RightEHindfootAnatRelTech[0,1]) + ","  + str(RightEHindfootAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEHindfootAnatRelTech[1,0]) + "," + str(RightEHindfootAnatRelTech[1,1]) + ","  + str(RightEHindfootAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEHindfootAnatRelTech[2,0]) + "," + str(RightEHindfootAnatRelTech[2,1]) + ","  + str(RightEHindfootAnatRelTech[2,2]) + "]])" + '\n')
    
                StaticDataFile.write('self.valueRightEForefootAnatRelTech = np.array([[' + str(RightEForefootAnatRelTech[0,0]) + "," + str(RightEForefootAnatRelTech[0,1]) + ","  + str(RightEForefootAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEForefootAnatRelTech[1,0]) + "," + str(RightEForefootAnatRelTech[1,1]) + ","  + str(RightEForefootAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEForefootAnatRelTech[2,0]) + "," + str(RightEForefootAnatRelTech[2,1]) + ","  + str(RightEForefootAnatRelTech[2,2]) + "]])" + '\n')
    
                StaticDataFile.write('self.valueRightEHalluxAnatRelTech = np.array([[' + str(RightEHalluxAnatRelTech[0,0]) + "," + str(RightEHalluxAnatRelTech[0,1]) + ","  + str(RightEHalluxAnatRelTech[0,2])  + "],[" +
                                                                          str(RightEHalluxAnatRelTech[1,0]) + "," + str(RightEHalluxAnatRelTech[1,1]) + ","  + str(RightEHalluxAnatRelTech[1,2]) + "],[" +
                                                                          str(RightEHalluxAnatRelTech[2,0]) + "," + str(RightEHalluxAnatRelTech[2,1]) + ","  + str(RightEHalluxAnatRelTech[2,2]) + "]])" + '\n')
    
                StaticDataFile.write('self.valueRight23MetatarsalHeadMarkerForefoot = np.array([' + str(Right23MetatarsalHeadMarkerForefoot[0]) + "," + str(Right23MetatarsalHeadMarkerForefoot[1]) + "," + str(Right23MetatarsalHeadMarkerForefoot[2]) + "])" +'\n')
                StaticDataFile.write('self.valueRightFirstMetatarsoPhalangealJointMarkerForefoot = np.array([' + str(RightFirstMetatarsoPhalangealJointMarkerForefoot[0]) + "," + str(RightFirstMetatarsoPhalangealJointMarkerForefoot[1]) + "," + str(RightFirstMetatarsoPhalangealJointMarkerForefoot[2]) + "])" +'\n')

            #print('FileUpdate- Tmatrix')
            StaticDataFile.close()
            
        def saveResultsinC3D():
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
            
            # Initialize arrays to write to C3D File
            framecount = vicon.GetFrameCount()
            exists = [True]*framecount
            
            arrayLeftHipCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightHipCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftKneeCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightKneeCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftAnkleCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightAnkleCenter = [[0. for m in range(framecount)] for n in range(3)]
            arrayLeftVirtualKneeMarker = [[0. for m in range(framecount)] for n in range(3)]
            arrayRightVirtualKneeMarker = [[0. for m in range(framecount)] for n in range(3)]
            
            arrayLeftLateralKneeMarkerX= [0 for m in range(framecount)] 
            arrayLeftLateralKneeMarkerY= [0 for m in range(framecount)] 
            arrayLeftLateralKneeMarkerZ= [0 for m in range(framecount)] 
            arrayRightLateralKneeMarkerX= [0 for m in range(framecount)] 
            arrayRightLateralKneeMarkerY= [0 for m in range(framecount)] 
            arrayRightLateralKneeMarkerZ= [0 for m in range(framecount)] 
            
            
            # For Sacral Triad Case, delete Sacral Marker Name
            # Explanation: When Sacral marker is used and exists in the UserPreferences, then 
            # Sacral Marker Name is deleted to push the code towards using PSIS markers.
            if self.valuePelvicFixCheck == '2':
                try:
                    del self.SacralMarkerName
                except:
                    pass
            else:
                pass
            
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
            #LeftLateralKneeMarkerX, LeftLateralKneeMarkerY, LeftLateralKneeMarkerZ, LeftLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralKneeMarkerName)
            LeftTibialMarkerX, LeftTibialMarkerY, LeftTibialMarkerZ, LeftTibialMarkerExists = MarkerArrayCheck(SubjectName, self.LeftTibialMarkerName)
            LeftLateralAnkleMarkerX, LeftLateralAnkleMarkerY, LeftLateralAnkleMarkerZ, LeftLateralAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralAnkleMarkerName)
            LeftToeMarkerX, LeftToeMarkerY, LeftToeMarkerZ, LeftToeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftToeMarkerName)
            LeftMedialAnkleMarkerX, LeftMedialAnkleMarkerY, LeftMedialAnkleMarkerZ, LeftMedialAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.LeftMedialAnkleMarkerName)
            LeftHeelMarkerX, LeftHeelMarkerY, LeftHeelMarkerZ, LeftHeelMarkerExists = MarkerArrayCheck(SubjectName, self.LeftHeelMarkerName)
            RightASISMarkerX, RightASISMarkerY, RightASISMarkerZ, RightASISMarkerExists = MarkerArrayCheck(SubjectName, self.RightASISMarkerName)
            RightThighMarkerX, RightThighMarkerY, RightThighMarkerZ, RightThighMarkerExists = MarkerArrayCheck(SubjectName, self.RightThighMarkerName)
            #RightLateralKneeMarkerX, RightLateralKneeMarkerY, RightLateralKneeMarkerZ, RightLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralKneeMarkerName)
            RightTibialMarkerX, RightTibialMarkerY, RightTibialMarkerZ, RightTibialMarkerExists = MarkerArrayCheck(SubjectName, self.RightTibialMarkerName)
            RightLateralAnkleMarkerX, RightLateralAnkleMarkerY, RightLateralAnkleMarkerZ, RightLateralAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralAnkleMarkerName)
            RightToeMarkerX, RightToeMarkerY, RightToeMarkerZ, RightToeMarkerExists = MarkerArrayCheck(SubjectName, self.RightToeMarkerName)
            RightMedialAnkleMarkerX, RightMedialAnkleMarkerY, RightMedialAnkleMarkerZ, RightMedialAnkleMarkerExists = MarkerArrayCheck(SubjectName, self.RightMedialAnkleMarkerName)
            RightHeelMarkerX, RightHeelMarkerY, RightHeelMarkerZ, RightHeelMarkerExists = MarkerArrayCheck(SubjectName, self.RightHeelMarkerName)
            
            if self.valueKneeAlignmentCheck == '0':
                LeftLateralKADMarkerX, LeftLateralKADMarkerY, LeftLateralKADMarkerZ, LeftLateralKADMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralKADMarkerName)
                LeftUpperKADMarkerX, LeftUpperKADMarkerY, LeftUpperKADMarkerZ, LeftUpperKADMarkerExists = MarkerArrayCheck(SubjectName, self.LeftUpperKADMarkerName)
                LeftLowerKADMarkerX, LeftLowerKADMarkerY, LeftLowerKADMarkerZ, LeftLowerKADMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLowerKADMarkerName)
                
                RightLateralKADMarkerX, RightLateralKADMarkerY, RightLateralKADMarkerZ, RightLateralKADMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralKADMarkerName)
                RightUpperKADMarkerX, RightUpperKADMarkerY, RightUpperKADMarkerZ, RightUpperKADMarkerExists = MarkerArrayCheck(SubjectName, self.RightUpperKADMarkerName)
                RightLowerKADMarkerX, RightLowerKADMarkerY, RightLowerKADMarkerZ, RightLowerKADMarkerExists = MarkerArrayCheck(SubjectName, self.RightLowerKADMarkerName)
            else:
                LeftLateralKneeMarkerX, LeftLateralKneeMarkerY, LeftLateralKneeMarkerZ, LeftLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftLateralKneeMarkerName)
                LeftMedialKneeMarkerX, LeftMedialKneeMarkerY, LeftMedialKneeMarkerZ, LeftMedialKneeMarkerExists = MarkerArrayCheck(SubjectName, self.LeftMedialKneeMarkerName)
                
                RightLateralKneeMarkerX, RightLateralKneeMarkerY, RightLateralKneeMarkerZ, RightLateralKneeMarkerExists = MarkerArrayCheck(SubjectName, self.RightLateralKneeMarkerName)
                RightMedialKneeMarkerX, RightMedialKneeMarkerY, RightMedialKneeMarkerZ, RightMedialKneeMarkerExists = MarkerArrayCheck(SubjectName, self.RightMedialKneeMarkerName)
                
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
            
            
            for FrameNumber in range(StartFrame-1,EndFrame):
                
                #Transform marker data if necessary based on direction that the patient is walking
                C7Marker  = np.array([C7MarkerX[FrameNumber], C7MarkerY[FrameNumber], C7MarkerZ[FrameNumber]])
                LeftClavicleMarker  = np.array([LeftClavicleMarkerX[FrameNumber], LeftClavicleMarkerY[FrameNumber], LeftClavicleMarkerZ[FrameNumber]])
                RightClavicleMarker  = np.array([RightClavicleMarkerX[FrameNumber], RightClavicleMarkerY[FrameNumber], RightClavicleMarkerZ[FrameNumber]])
                SacralMarker  = np.array([SacralMarkerX[FrameNumber], SacralMarkerY[FrameNumber], SacralMarkerZ[FrameNumber]])
                LeftASISMarker  = np.array([LeftASISMarkerX[FrameNumber], LeftASISMarkerY[FrameNumber], LeftASISMarkerZ[FrameNumber]])
                LeftThighMarker  = np.array([LeftThighMarkerX[FrameNumber], LeftThighMarkerY[FrameNumber], LeftThighMarkerZ[FrameNumber]])
                LeftTibialMarker  = np.array([LeftTibialMarkerX[FrameNumber], LeftTibialMarkerY[FrameNumber], LeftTibialMarkerZ[FrameNumber]])
                if LeftTibialTriadCheck is True:
                    LeftTibialUpperMarker  = np.array([LeftTibialUpperMarkerX[FrameNumber], LeftTibialUpperMarkerY[FrameNumber], LeftTibialUpperMarkerZ[FrameNumber]])
                    LeftTibialLowerMarker  = np.array([LeftTibialLowerMarkerX[FrameNumber], LeftTibialLowerMarkerY[FrameNumber], LeftTibialLowerMarkerZ[FrameNumber]])
                LeftLateralAnkleMarker  = np.array([LeftLateralAnkleMarkerX[FrameNumber], LeftLateralAnkleMarkerY[FrameNumber], LeftLateralAnkleMarkerZ[FrameNumber]])
                LeftToeMarker  = np.array([LeftToeMarkerX[FrameNumber], LeftToeMarkerY[FrameNumber], LeftToeMarkerZ[FrameNumber]])
                LeftMedialAnkleMarker  = np.array([LeftMedialAnkleMarkerX[FrameNumber], LeftMedialAnkleMarkerY[FrameNumber], LeftMedialAnkleMarkerZ[FrameNumber]])
                LeftHeelMarker  = np.array([LeftHeelMarkerX[FrameNumber], LeftHeelMarkerY[FrameNumber], LeftHeelMarkerZ[FrameNumber]])
                RightASISMarker  = np.array([RightASISMarkerX[FrameNumber], RightASISMarkerY[FrameNumber], RightASISMarkerZ[FrameNumber]])
                RightThighMarker  = np.array([RightThighMarkerX[FrameNumber], RightThighMarkerY[FrameNumber], RightThighMarkerZ[FrameNumber]])
                RightTibialMarker  = np.array([RightTibialMarkerX[FrameNumber], RightTibialMarkerY[FrameNumber], RightTibialMarkerZ[FrameNumber]])
                if RightTibialTriadCheck is True:
                    RightTibialUpperMarker  = np.array([RightTibialUpperMarkerX[FrameNumber], RightTibialUpperMarkerY[FrameNumber], RightTibialUpperMarkerZ[FrameNumber]])
                    RightTibialLowerMarker  = np.array([RightTibialLowerMarkerX[FrameNumber], RightTibialLowerMarkerY[FrameNumber], RightTibialLowerMarkerZ[FrameNumber]])
                RightLateralAnkleMarker  = np.array([RightLateralAnkleMarkerX[FrameNumber], RightLateralAnkleMarkerY[FrameNumber], RightLateralAnkleMarkerZ[FrameNumber]])
                RightToeMarker  = np.array([RightToeMarkerX[FrameNumber], RightToeMarkerY[FrameNumber], RightToeMarkerZ[FrameNumber]])
                RightMedialAnkleMarker  = np.array([RightMedialAnkleMarkerX[FrameNumber], RightMedialAnkleMarkerY[FrameNumber], RightMedialAnkleMarkerZ[FrameNumber]])
                RightHeelMarker  = np.array([RightHeelMarkerX[FrameNumber], RightHeelMarkerY[FrameNumber], RightHeelMarkerZ[FrameNumber]])
                
                if self.valueKneeAlignmentCheck == '0':
                    LeftLateralKADMarker  = np.array([LeftLateralKADMarkerX[FrameNumber], LeftLateralKADMarkerY[FrameNumber], LeftLateralKADMarkerZ[FrameNumber]])
                    LeftUpperKADMarker  = np.array([LeftUpperKADMarkerX[FrameNumber], LeftUpperKADMarkerY[FrameNumber], LeftUpperKADMarkerZ[FrameNumber]])
                    LeftLowerKADMarker  = np.array([LeftLowerKADMarkerX[FrameNumber], LeftLowerKADMarkerY[FrameNumber], LeftLowerKADMarkerZ[FrameNumber]])
                    
                    RightLateralKADMarker  = np.array([RightLateralKADMarkerX[FrameNumber], RightLateralKADMarkerY[FrameNumber], RightLateralKADMarkerZ[FrameNumber]])
                    RightUpperKADMarker  = np.array([RightUpperKADMarkerX[FrameNumber], RightUpperKADMarkerY[FrameNumber], RightUpperKADMarkerZ[FrameNumber]])
                    RightLowerKADMarker  = np.array([RightLowerKADMarkerX[FrameNumber], RightLowerKADMarkerY[FrameNumber], RightLowerKADMarkerZ[FrameNumber]])
                else:
                    LeftLateralKneeMarker  = np.array([LeftLateralKneeMarkerX[FrameNumber], LeftLateralKneeMarkerY[FrameNumber], LeftLateralKneeMarkerZ[FrameNumber]])
                    LeftMedialKneeMarker  = np.array([LeftMedialKneeMarkerX[FrameNumber], LeftMedialKneeMarkerY[FrameNumber], LeftMedialKneeMarkerZ[FrameNumber]])
                    
                    RightLateralKneeMarker  = np.array([RightLateralKneeMarkerX[FrameNumber], RightLateralKneeMarkerY[FrameNumber], RightLateralKneeMarkerZ[FrameNumber]])
                    RightMedialKneeMarker  = np.array([RightMedialKneeMarkerX[FrameNumber], RightMedialKneeMarkerY[FrameNumber], RightMedialKneeMarkerZ[FrameNumber]])
                    
                    

            
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
                
                if self.valueKneeAlignmentCheck == '0':
                    #Compute Location of Virtual Knee Marker (based on cluster-type knee fixture)
                    LeftVirtualKneeMarkerLab = gait.ComputeVirtualKneeMarker_Newington('Left', self.MarkerDiameter, LeftUpperKADMarker, LeftLateralKADMarker, LeftLowerKADMarker)
                    RightVirtualKneeMarkerLab = gait.ComputeVirtualKneeMarker_Newington('Right', self.MarkerDiameter, RightUpperKADMarker, RightLateralKADMarker, RightLowerKADMarker)
                    #print(LeftVirtualKneeMarkerLab)
                    #print(RightVirtualKneeMarkerLab)
                    
                    LeftLateralKneeMarker = LeftVirtualKneeMarkerLab
                    RightLateralKneeMarker = RightVirtualKneeMarkerLab
                else:
                    LeftVirtualKneeMarkerLab = LeftLateralKneeMarker
                    RightVirtualKneeMarkerLab = RightLateralKneeMarker
                
                # Compute Technical Coordinate System: Thigh   
                LeftEThighTech = gait.TechCS_Thigh_Newington('Left', LeftHipCenterLab, LeftThighMarker, LeftLateralKneeMarker)
                RightEThighTech = gait.TechCS_Thigh_Newington('Right', RightHipCenterLab, RightThighMarker, RightLateralKneeMarker)
                # Compute Anatomical Coordinate System: Thigh
                LeftEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueLeftEThighAnatRelTech,LeftEThighTech)
                RightEThighAnat = math.TransformAnatCoorSysFromTechCoors(self.valueRightEThighAnatRelTech,RightEThighTech)

                
                # Compute Location of Knee Center (in lab space, based on thigh anatomical frame)
                LeftKneeCenterLab = math.TransformPointIntoLabCoors(self.valueLeftKneeCenterThigh, LeftEThighTech, LeftLateralKneeMarker)
                RightKneeCenterLab = math.TransformPointIntoLabCoors(self.valueRightKneeCenterThigh, RightEThighTech, RightLateralKneeMarker)
                
                
                # Compute Technical Coordinate System: Shank
                if LeftTibialTriadCheck is True:
                    LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftTibialUpperMarker, LeftTibialLowerMarker, LeftTibialMarker)
                else:
                    LeftEShankTech = gait.TechCS_Shank_Newington('Left', LeftKneeCenterLab, LeftTibialMarker, LeftLateralAnkleMarker)
                if RightTibialTriadCheck is True:
                    RightEShankTech = gait.TechCS_Shank_Newington('Right', RightTibialUpperMarker, RightTibialLowerMarker, RightTibialMarker)
                else:
                    RightEShankTech = gait.TechCS_Shank_Newington('Right', RightKneeCenterLab, RightTibialMarker, RightLateralAnkleMarker)

                # Compute anklejoint centers
                if LeftTibialTriadCheck is True:
                    LeftAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueLeftAnkleCenterShank, LeftEShankTech, LeftTibialMarker)
                else:
                    LeftAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueLeftAnkleCenterShank, LeftEShankTech, LeftLateralAnkleMarker)
                if RightTibialTriadCheck is True:
                    RightAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueRightAnkleCenterShank, RightEShankTech, RightTibialMarker)
                else:
                    RightAnkleCenterLab = math.TransformPointIntoLabCoors(self.valueRightAnkleCenterShank, RightEShankTech, RightLateralAnkleMarker)
                #print FrameNumber, LeftAnkleCenterLab
                
                
                # If Medial ankle is available,then recompute ankle joint center
                if LeftMedialAnkleMarkerDropOff == 0:
                    LeftAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Left', self.MarkerDiameter, self.valueLeftAnkleWidth, LeftLateralAnkleMarker, LeftMedialAnkleMarker)
                if RightMedialAnkleMarkerDropOff == 0:
                    RightAnkleCenterLab = gait.JointCenterModel_Ankle_Newington('Right', self.MarkerDiameter, self.valueRightAnkleWidth, RightLateralAnkleMarker, RightMedialAnkleMarker)
                #print FrameNumber, LeftAnkleCenterLab
                
                # Fill Arrays to write Joint Centers to C3D File
                arrayLeftHipCenter[0][FrameNumber] = LeftHipCenterLab[0]
                arrayLeftHipCenter[1][FrameNumber] = LeftHipCenterLab[1]
                arrayLeftHipCenter[2][FrameNumber] = LeftHipCenterLab[2]
                
                arrayRightHipCenter[0][FrameNumber] = RightHipCenterLab[0]
                arrayRightHipCenter[1][FrameNumber] = RightHipCenterLab[1]
                arrayRightHipCenter[2][FrameNumber] = RightHipCenterLab[2]
                
                arrayLeftKneeCenter[0][FrameNumber] = LeftKneeCenterLab[0]
                arrayLeftKneeCenter[1][FrameNumber] = LeftKneeCenterLab[1]
                arrayLeftKneeCenter[2][FrameNumber] = LeftKneeCenterLab[2]
                
                arrayRightKneeCenter[0][FrameNumber] = RightKneeCenterLab[0]
                arrayRightKneeCenter[1][FrameNumber] = RightKneeCenterLab[1]
                arrayRightKneeCenter[2][FrameNumber] = RightKneeCenterLab[2]
                
                arrayLeftVirtualKneeMarker[0][FrameNumber] = LeftVirtualKneeMarkerLab[0]
                arrayLeftVirtualKneeMarker[1][FrameNumber] = LeftVirtualKneeMarkerLab[1]
                arrayLeftVirtualKneeMarker[2][FrameNumber] = LeftVirtualKneeMarkerLab[2]
                
                arrayLeftLateralKneeMarkerX[FrameNumber] = arrayLeftVirtualKneeMarker[0][FrameNumber]
                arrayLeftLateralKneeMarkerY[FrameNumber] = arrayLeftVirtualKneeMarker[1][FrameNumber]
                arrayLeftLateralKneeMarkerZ[FrameNumber] = arrayLeftVirtualKneeMarker[2][FrameNumber]
                
                arrayRightVirtualKneeMarker[0][FrameNumber] = RightVirtualKneeMarkerLab[0]
                arrayRightVirtualKneeMarker[1][FrameNumber] = RightVirtualKneeMarkerLab[1]
                arrayRightVirtualKneeMarker[2][FrameNumber] = RightVirtualKneeMarkerLab[2]
                
                arrayRightLateralKneeMarkerX[FrameNumber] = arrayRightVirtualKneeMarker[0][FrameNumber]
                arrayRightLateralKneeMarkerY[FrameNumber] = arrayRightVirtualKneeMarker[1][FrameNumber]
                arrayRightLateralKneeMarkerZ[FrameNumber] = arrayRightVirtualKneeMarker[2][FrameNumber]
                
                arrayLeftAnkleCenter[0][FrameNumber] = LeftAnkleCenterLab[0]
                arrayLeftAnkleCenter[1][FrameNumber] = LeftAnkleCenterLab[1]
                arrayLeftAnkleCenter[2][FrameNumber] = LeftAnkleCenterLab[2]
                
                arrayRightAnkleCenter[0][FrameNumber] = RightAnkleCenterLab[0]
                arrayRightAnkleCenter[1][FrameNumber] = RightAnkleCenterLab[1]
                arrayRightAnkleCenter[2][FrameNumber] = RightAnkleCenterLab[2]
            
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
            if not 'LKNE' in ModelOutputs:
                vicon.CreateModeledMarker( SubjectName, 'LKNE' )
            if not 'RKNE' in ModelOutputs:
                vicon.CreateModeledMarker( SubjectName, 'RKNE' )
#            if not 'LKneeVirtual' in ModelOutputs:
#                vicon.CreateModeledMarker( SubjectName, 'LKneeVirtual' )
#            if not 'RKneeVirtual' in ModelOutputs:
#                vicon.CreateModeledMarker( SubjectName, 'RKneeVirtual' )
                
            # Write Arrays to C3D Files
            # Joint Centers
            vicon.SetModelOutput(SubjectName, 'LHJC', arrayLeftHipCenter,   exists )
            vicon.SetModelOutput(SubjectName, 'RHJC', arrayRightHipCenter,  exists )
            vicon.SetModelOutput(SubjectName, 'LKJC', arrayLeftKneeCenter,  exists )
            vicon.SetModelOutput(SubjectName, 'RKJC', arrayRightKneeCenter, exists )
            vicon.SetModelOutput(SubjectName, 'LAJC', arrayLeftAnkleCenter, exists )
            vicon.SetModelOutput(SubjectName, 'RAJC', arrayRightAnkleCenter,exists )
            vicon.SetModelOutput(SubjectName, 'LKNE', arrayLeftVirtualKneeMarker,  exists )
            vicon.SetModelOutput(SubjectName, 'RKNE', arrayRightVirtualKneeMarker, exists )
            #vicon.SetModelOutput(SubjectName, 'LKneeVirtual', arrayLeftVirtualKneeMarker,  exists )
            #vicon.SetModelOutput(SubjectName, 'RKneeVirtual', arrayRightVirtualKneeMarker, exists )
        
            #vicon.SetTrajectory(SubjectName, self.LeftLateralKneeMarkerName, arrayLeftLateralKneeMarkerX, arrayLeftLateralKneeMarkerY, arrayLeftLateralKneeMarkerZ, exists )
            #vicon.SetTrajectory(SubjectName, self.RightLateralKneeMarkerName, arrayRightLateralKneeMarkerX, arrayRightLateralKneeMarkerY, arrayRightLateralKneeMarkerZ, exists )
        
        def savePdf():
            FilePath, FileName = vicon.GetTrialName()
            InitialPath = FilePath
            
            InitialFileName = 'Static ' + TestingCondition + ' ' + self.valuePatientNumber[:7] + ' ' + self.valueDataCollectionDate_Year + self.valueDataCollectionDate_Month + self.valueDataCollectionDate_Day + '.pdf'
            StaticResultsFilename = filedialog.asksaveasfilename(initialdir = InitialPath,initialfile = InitialFileName, title = "Select Static Results File Location",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
            
            #Prepare Results Page pdf
            StaticResultsPage = canvas.Canvas(StaticResultsFilename, pagesize=letter)            
            PageWidth, PageHeight = letter 
            # Origin at Bottom Left
            # PageWidth = 612, PageHeight = 792
            HeightMargin = 56
            WidthMargin = 81 
            DrawRegionHeight = PageHeight - 2 * HeightMargin
            DrawRegionWidth = PageWidth - 2 * WidthMargin
            
            # Page Title
            StaticResultsPage.setFillColor(reportlabColors.lightgrey)
            StaticResultsPage.rect(WidthMargin,HeightMargin + DrawRegionHeight,DrawRegionWidth,-30,stroke = 0, fill = 1)
            StaticResultsPage.setFont("Times-Bold", 12)
            StaticResultsPage.setFillGray(0.0)
            StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 12,"Shriners Hospital for Children")
            StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 25,"Motion Analysis Center")
            StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 50,"-Static Report-")
            
            # Static Settings
            StaticResultsPage.setFont("Times-Roman", 11)
            VerticalOffsetFromTitle = 70
            LineSpacing = 15
            ColumnSpacing = 120
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin - VerticalOffsetFromTitle ,"Static File:")
            StaticResultsPage.drawString(WidthMargin + ColumnSpacing, PageHeight - HeightMargin - VerticalOffsetFromTitle , FileName + '.c3d')
                        
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,"Data Collection Date:")
            StaticResultsPage.drawString(WidthMargin + ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , self.valueDataCollectionDate_Day + '-' + self.valueDataCollectionDate_Month + '-' + self.valueDataCollectionDate_Year)
            
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,"User Preferences File:")
            StaticResultsPage.drawString(WidthMargin + ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing , UserPreferencesFileName)
            
            if self.valueLeftPlantigradeCheck == '1':
                PlantigradeText = 'L    '
            if self.valueRightPlantigradeCheck == '1':
                PlantigradeText = 'R    '
            if self.valueLeftPlantigradeCheck == '1' and self.valueRightPlantigradeCheck == '1':
                PlantigradeText = 'B    '
            if self.valueLeftPlantigradeCheck == '0' and self.valueRightPlantigradeCheck == '0':
                PlantigradeText = 'None    '
                
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,"Gait Model:")
            StaticResultsPage.drawString(WidthMargin + ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,'Shriners')
            StaticResultsPage.drawString(WidthMargin + 2 * ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,'DataFrameUsed: ' + str(self.valueStaticFrameNumber))
            StaticResultsPage.drawString(WidthMargin + 3 * ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,'Plantigrade: ' + PlantigradeText)
            
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,"TestingCondition:") 
            StaticResultsPage.drawString(WidthMargin + ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , self.valueTrialModifier)
            StaticResultsPage.drawString(WidthMargin + 2 * ColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , "AssistiveDevice: " + self.valueAssistiveDevice)
            
            # Static Posture- Labels
            StaticResultsPage.setFont("Times-Bold", 12)
            StaticResultsPage.setStrokeGray(0.75)
            VerticalOffsetFromTitle = 160
            LabelColumnSpacing = 150
            LeftColumnSpacing = 200
            RightColumnSpacing = 300
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Standing Posture (degrees)")
            StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Left")
            StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Right")
            StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(17*LineSpacing + 5),stroke = 1, fill = 0)
            
            StaticResultsPage.setFont("Times-Roman", 11)
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,"Trunk Obliquity")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,"Trunk Tilt")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,"Trunk Rotation")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,"Pelvic Obliquity")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,"Pelvic Tilt")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,"Pelvic Rotation")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,"Hip Ab/Adduction")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,"Hip Flex/Extension")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 9 * LineSpacing ,"Hip Int/External Rotation")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -10 * LineSpacing ,"Knee Varus/Valgus")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -11 * LineSpacing ,"Knee Flex/Extension")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -12 * LineSpacing ,"Knee Int/External Rotation")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -13 * LineSpacing ,"Knee Progression")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -14 * LineSpacing ,"Ankle Plantar/Dorsiflexion")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -15 * LineSpacing ,"Foot Int/External Rotation")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -16 * LineSpacing ,"Foot Progression")

            # Static Posture- Left Values
            if len(str.split(LeftTrunkObliquity.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,str.split(LeftTrunkObliquity.get())[0])
            if len(str.split(LeftTrunkTilt.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str.split(LeftTrunkTilt.get())[0])
            if len(str.split(LeftTrunkRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str.split(LeftTrunkRotation.get())[0])
            if len(str.split(LeftPelvisObliquity.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str.split(LeftPelvisObliquity.get())[0])
            if len(str.split(LeftPelvisTilt.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str.split(LeftPelvisTilt.get())[0])
            if len(str.split(LeftPelvisRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str.split(LeftPelvisRotation.get())[0])
            if len(str.split(LeftHipAbAdduction.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,str.split(LeftHipAbAdduction.get())[0])
            if len(str.split(LeftHipFlexExtension.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,str.split(LeftHipFlexExtension.get())[0])
            if len(str.split(LeftHipIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 9 * LineSpacing ,str.split(LeftHipIntExtRotation.get())[0])
            if len(str.split(LeftKneeVarusValgus.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -10 * LineSpacing ,str.split(LeftKneeVarusValgus.get())[0])
            if len(str.split(LeftKneeFlexExtension.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -11 * LineSpacing ,str.split(LeftKneeFlexExtension.get())[0])
            if len(str.split(LeftKneeIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -12 * LineSpacing ,str.split(LeftKneeIntExtRotation.get())[0])
            if len(str.split(LeftKneeProgression.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -13 * LineSpacing ,str.split(LeftKneeProgression.get())[0])
            if len(str.split(LeftAnklePlantarDorsiflexion.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -14 * LineSpacing ,str.split(LeftAnklePlantarDorsiflexion.get())[0])
            if len(str.split(LeftAnkleIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -15 * LineSpacing ,str.split(LeftAnkleIntExtRotation.get())[0])
            if len(str.split(LeftFootProgression.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -16 * LineSpacing ,str.split(LeftFootProgression.get())[0])
            # Static Posture- Left Direction
            if len(str.split(LeftTrunkObliquity.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , '  ' + str.split(LeftTrunkObliquity.get())[1])
            if len(str.split(LeftTrunkTilt.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing , '  ' + str.split(LeftTrunkTilt.get())[1])
            if len(str.split(LeftTrunkRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing , '  ' + str.split(LeftTrunkRotation.get())[1])
            if len(str.split(LeftPelvisObliquity.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , '  ' + str.split(LeftPelvisObliquity.get())[1])
            if len(str.split(LeftPelvisTilt.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing , '  ' + str.split(LeftPelvisTilt.get())[1])
            if len(str.split(LeftPelvisRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing , '  ' + str.split(LeftPelvisRotation.get())[1])
            if len(str.split(LeftHipAbAdduction.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing , '  ' + str.split(LeftHipAbAdduction.get())[1])
            if len(str.split(LeftHipFlexExtension.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing , '  ' + str.split(LeftHipFlexExtension.get())[1])
            if len(str.split(LeftHipIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 9 * LineSpacing , '  ' + str.split(LeftHipIntExtRotation.get())[1])
            if len(str.split(LeftKneeVarusValgus.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -10 * LineSpacing , '  ' + str.split(LeftKneeVarusValgus.get())[1])
            if len(str.split(LeftKneeFlexExtension.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -11 * LineSpacing , '  ' + str.split(LeftKneeFlexExtension.get())[1])
            if len(str.split(LeftKneeIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -12 * LineSpacing , '  ' + str.split(LeftKneeIntExtRotation.get())[1])
            if len(str.split(LeftKneeProgression.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -13 * LineSpacing , '  ' + str.split(LeftKneeProgression.get())[1])
            if len(str.split(LeftAnklePlantarDorsiflexion.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -14 * LineSpacing , '  ' + str.split(LeftAnklePlantarDorsiflexion.get())[1])
            if len(str.split(LeftAnkleIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -15 * LineSpacing , '  ' + str.split(LeftAnkleIntExtRotation.get())[1])
            if len(str.split(LeftFootProgression.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -16 * LineSpacing , '  ' + str.split(LeftFootProgression.get())[1])
            
            
            # Static Posture- Right Values
            if len(str.split(RightTrunkObliquity.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,str.split(RightTrunkObliquity.get())[0])
            if len(str.split(RightTrunkTilt.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str.split(RightTrunkTilt.get())[0])
            if len(str.split(RightTrunkRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str.split(RightTrunkRotation.get())[0])
            if len(str.split(RightPelvisObliquity.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str.split(RightPelvisObliquity.get())[0])
            if len(str.split(RightPelvisTilt.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str.split(RightPelvisTilt.get())[0])
            if len(str.split(RightPelvisRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str.split(RightPelvisRotation.get())[0])
            if len(str.split(RightHipAbAdduction.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,str.split(RightHipAbAdduction.get())[0])
            if len(str.split(RightHipFlexExtension.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,str.split(RightHipFlexExtension.get())[0])
            if len(str.split(RightHipIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 9 * LineSpacing ,str.split(RightHipIntExtRotation.get())[0])
            if len(str.split(RightKneeVarusValgus.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -10 * LineSpacing ,str.split(RightKneeVarusValgus.get())[0])
            if len(str.split(RightKneeFlexExtension.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -11 * LineSpacing ,str.split(RightKneeFlexExtension.get())[0])
            if len(str.split(RightKneeIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -12 * LineSpacing ,str.split(RightKneeIntExtRotation.get())[0])
            if len(str.split(RightKneeProgression.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -13 * LineSpacing ,str.split(RightKneeProgression.get())[0])
            if len(str.split(RightAnklePlantarDorsiflexion.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -14 * LineSpacing ,str.split(RightAnklePlantarDorsiflexion.get())[0])
            if len(str.split(RightAnkleIntExtRotation.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -15 * LineSpacing ,str.split(RightAnkleIntExtRotation.get())[0])
            if len(str.split(RightFootProgression.get())) > 0:
                StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -16 * LineSpacing ,str.split(RightFootProgression.get())[0])
            
            # Static Posture- Right Direction
            if len(str.split(RightTrunkObliquity.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , '  ' + str.split(RightTrunkObliquity.get())[1])
            if len(str.split(RightTrunkTilt.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing , '  ' + str.split(RightTrunkTilt.get())[1])
            if len(str.split(RightTrunkRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing , '  ' + str.split(RightTrunkRotation.get())[1])
            if len(str.split(RightPelvisObliquity.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , '  ' + str.split(RightPelvisObliquity.get())[1])
            if len(str.split(RightPelvisTilt.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing , '  ' + str.split(RightPelvisTilt.get())[1])
            if len(str.split(RightPelvisRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing , '  ' + str.split(RightPelvisRotation.get())[1])
            if len(str.split(RightHipAbAdduction.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing , '  ' + str.split(RightHipAbAdduction.get())[1])
            if len(str.split(RightHipFlexExtension.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing , '  ' + str.split(RightHipFlexExtension.get())[1])
            if len(str.split(RightHipIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 9 * LineSpacing , '  ' + str.split(RightHipIntExtRotation.get())[1])
            if len(str.split(RightKneeVarusValgus.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -10 * LineSpacing , '  ' + str.split(RightKneeVarusValgus.get())[1])
            if len(str.split(RightKneeFlexExtension.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -11 * LineSpacing , '  ' + str.split(RightKneeFlexExtension.get())[1])
            if len(str.split(RightKneeIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -12 * LineSpacing , '  ' + str.split(RightKneeIntExtRotation.get())[1])
            if len(str.split(RightKneeProgression.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -13 * LineSpacing , '  ' + str.split(RightKneeProgression.get())[1])
            if len(str.split(RightAnklePlantarDorsiflexion.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -14 * LineSpacing , '  ' + str.split(RightAnklePlantarDorsiflexion.get())[1])
            if len(str.split(RightAnkleIntExtRotation.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -15 * LineSpacing , '  ' + str.split(RightAnkleIntExtRotation.get())[1])
            if len(str.split(RightFootProgression.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle -16 * LineSpacing , '  ' + str.split(RightFootProgression.get())[1])
            
            # Tibial Torsion
            StaticResultsPage.setFont("Times-Bold", 12)
            VerticalOffsetFromTitle = 430
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Tibial Torsion (degrees)")
            StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(1*LineSpacing + 5),stroke = 1, fill = 0)
            
            StaticResultsPage.setFont("Times-Roman", 11)
            # Left
            StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 0 * LineSpacing ,str.split(LeftTibiaTorsion.get())[0])
            if len(str.split(LeftTibiaTorsion.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 0 * LineSpacing , '  ' + str.split(LeftTibiaTorsion.get())[1])
            # Right
            StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 0 * LineSpacing ,str.split(RightTibiaTorsion.get())[0])
            if len(str.split(RightTibiaTorsion.get())) > 1:
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 0 * LineSpacing , '  ' + str.split(RightTibiaTorsion.get())[1])
            
# =============================================================================
#           QA Report Number are recomputed here 
#           These are not available here due to being computed in QA Report class                
# =============================================================================
            if vicon.HasTrajectory(SubjectName,self.LeftASISMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightASISMarkerName) is True:
                valueASISdistMarkers=np.linalg.norm(LeftASISMarker-RightASISMarker)
                
            if vicon.HasTrajectory(SubjectName,self.LeftLateralKneeMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftMedialKneeMarkerName) is True:
                valueLeftKneeWidthMarkers=np.linalg.norm(LeftLateralKneeMarker-LeftMedialKneeMarker)-self.MarkerDiameter

            if vicon.HasTrajectory(SubjectName,self.RightLateralKneeMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightMedialKneeMarkerName) is True:
                valueRightKneeWidthMarkers=np.linalg.norm(RightLateralKneeMarker-RightMedialKneeMarker)-self.MarkerDiameter
            
            if vicon.HasTrajectory(SubjectName,self.LeftLateralAnkleMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftMedialAnkleMarkerName) is True:
                valueLeftAnkleWidthMarkers=np.linalg.norm(LeftLateralAnkleMarker-LeftMedialAnkleMarker)-self.MarkerDiameter

            if vicon.HasTrajectory(SubjectName,self.RightLateralAnkleMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightMedialAnkleMarkerName) is True:
                valueRightAnkleWidthMarkers=np.linalg.norm(RightLateralAnkleMarker-RightMedialAnkleMarker)-self.MarkerDiameter
            
            if vicon.HasTrajectory(SubjectName,self.LeftLateralKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftUpperKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.LeftLowerKADMarkerName) is True:
                # Distances
                valueLeftUpperLateral = np.linalg.norm(LeftUpperKADMarker-LeftLateralKADMarker)
                valueLeftUpperLower = np.linalg.norm(LeftUpperKADMarker-LeftLowerKADMarker)
                valueLeftLateralLower = np.linalg.norm(LeftLateralKADMarker-LeftLowerKADMarker)
                valueLeftDistRange = int(round(max(valueLeftUpperLateral,valueLeftUpperLower,valueLeftLateralLower)-min(valueLeftUpperLateral,valueLeftUpperLower,valueLeftLateralLower)))
                # Angles
                valueLeftUpperLateralLower = math.Compute3DAngle(LeftUpperKADMarker,LeftLateralKADMarker,LeftLowerKADMarker) * 180 / np.pi
                valueLeftLateralUpperLower = math.Compute3DAngle(LeftLateralKADMarker,LeftUpperKADMarker,LeftLowerKADMarker) * 180 / np.pi
                valueLeftUpperLowerLateral = math.Compute3DAngle(LeftUpperKADMarker,LeftLowerKADMarker,LeftLateralKADMarker) * 180 / np.pi
                valueLeftAngleRange = int(round(max(valueLeftUpperLateralLower,valueLeftLateralUpperLower,valueLeftUpperLowerLateral)-min(valueLeftUpperLateralLower,valueLeftLateralUpperLower,valueLeftUpperLowerLateral)))
            
            if vicon.HasTrajectory(SubjectName,self.RightLateralKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightUpperKADMarkerName) is True and vicon.HasTrajectory(SubjectName,self.RightLowerKADMarkerName) is True:
                #Distances
                valueRightUpperLateral = np.linalg.norm(RightUpperKADMarker-RightLateralKADMarker)
                valueRightUpperLower = np.linalg.norm(RightUpperKADMarker-RightLowerKADMarker)
                valueRightLateralLower = np.linalg.norm(RightLateralKADMarker-RightLowerKADMarker)
                valueRightDistRange = int(round(max(valueRightUpperLateral,valueRightUpperLower,valueRightLateralLower)-min(valueRightUpperLateral,valueRightUpperLower,valueRightLateralLower)))
                #Angles
                valueRightUpperLateralLower = math.Compute3DAngle(RightUpperKADMarker,RightLateralKADMarker,RightLowerKADMarker) * 180 / np.pi
                valueRightLateralUpperLower = math.Compute3DAngle(RightLateralKADMarker,RightUpperKADMarker,RightLowerKADMarker) * 180 / np.pi
                valueRightUpperLowerLateral = math.Compute3DAngle(RightUpperKADMarker,RightLowerKADMarker,RightLateralKADMarker) * 180 / np.pi
                valueRightAngleRange = int(round(max(valueRightUpperLateralLower,valueRightLateralUpperLower,valueRightUpperLowerLateral)-min(valueRightUpperLateralLower,valueRightLateralUpperLower,valueRightUpperLowerLateral)))
# =============================================================================

            # QA Report- Clinical vs. Marker
            StaticResultsPage.setFont("Times-Bold", 12)
            VerticalOffsetFromTitle = 460
            LabelColumnSpacing = 150
            LeftColumnSpacing = 200
            RightColumnSpacing = 300
            DifferenceColumnSpacing = 400
            StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Comparison of Clinical Exam - Marker Data")
            if self.valueKneeAlignmentCheck == '0':
                StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(5*LineSpacing + 5),stroke = 1, fill = 0)
            if self.valueKneeAlignmentCheck == '1':
                StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(7*LineSpacing + 5),stroke = 1, fill = 0)
            
            StaticResultsPage.setFont("Times-Roman", 11)
            StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing, "Clinical Exam")
            StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle- 1 * LineSpacing, "Markers")
            StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle- 1 * LineSpacing, "Diffrence")
            StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,"ASIS-to-ASIS Distance (mm)")
            if self.valueKneeAlignmentCheck == '0':
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,"Ankle Width (mm)- Left")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,"Ankle Width (mm)- Right")
            if self.valueKneeAlignmentCheck == '1':
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,"Knee Width (mm)- Left")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,"Knee Width (mm)- Right")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,"Ankle Width (mm)- Left")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,"Ankle Width (mm)- Right")
            
            #Values
            StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str(self.valueASISdist))
            StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str(int(round(valueASISdistMarkers))))
            StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str(int(round(abs(valueASISdistMarkers-self.valueASISdist)))))
            
            if self.valueKneeAlignmentCheck == '0':
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(self.valueLeftAnkleWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(int(round(valueLeftAnkleWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(int(round(abs(valueLeftAnkleWidthMarkers-self.valueLeftAnkleWidth)))))
                
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(self.valueRightAnkleWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(int(round(valueRightAnkleWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(int(round(abs(valueRightAnkleWidthMarkers-self.valueRightAnkleWidth)))))
            if self.valueKneeAlignmentCheck == '1':
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(self.valueLeftKneeWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(int(round(valueLeftKneeWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str(int(round(abs(valueLeftKneeWidthMarkers-self.valueLeftKneeWidth)))))
                
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(self.valueRightKneeWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(int(round(valueRightKneeWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str(int(round(abs(valueRightKneeWidthMarkers-self.valueRightKneeWidth)))))
                
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str(self.valueLeftAnkleWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str(int(round(valueLeftAnkleWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str(int(round(abs(valueLeftAnkleWidthMarkers-self.valueLeftAnkleWidth)))))
                
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str(self.valueRightAnkleWidth))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str(int(round(valueRightAnkleWidthMarkers))))
                StaticResultsPage.drawCentredString(WidthMargin + DifferenceColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str(int(round(abs(valueRightAnkleWidthMarkers-self.valueRightAnkleWidth)))))
                
            if self.valueKneeAlignmentCheck == '0':
                # QA Report- KAD Marker Data
                StaticResultsPage.setFont("Times-Bold", 12)
                VerticalOffsetFromTitle = 550
                LabelColumnSpacing = 150
                LeftColumnSpacing = 200
                LeftRangeColumnSpacing = 275
                RightColumnSpacing = 350
                RightRangeColumnSpacing = 425
                
                #Labels
                StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Knee Alignment Fixture Marker Data")
                StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing - 5, "Inter Marker Distance (mm)")
                StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing - 2 * 5, "Inter Marker Angles (degrees)")
                StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(9*LineSpacing + 5 + 2 * 5)  ,stroke = 1, fill = 0)
                
                StaticResultsPage.setFont("Times-Roman", 11)
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , "Left")
                StaticResultsPage.drawCentredString(WidthMargin + LeftRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , "Range")
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , "Right")
                StaticResultsPage.drawCentredString(WidthMargin + RightRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , "Range")
                
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing - 5 ,"Upper & Lateral Marker")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing - 5 ,"Upper & Lower Marker")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing - 5 ,"Lower & Lateral Marker")
                
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing - 2 * 5,"Upper-Lateral-Lower")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing - 2 * 5,"Lateral-Upper-Lower")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing - 2 * 5,"Upper-Lower-Lateral")
                
                # Values- Left
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing - 5 ,str(int(round(valueLeftUpperLateral))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing - 5 ,str(int(round(valueLeftUpperLower))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing - 5 ,str(int(round(valueLeftLateralLower))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing - 5 ,str(valueLeftDistRange))
                
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing - 2*5 ,str(int(round(valueLeftUpperLateralLower))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing - 2*5 ,str(int(round(valueLeftLateralUpperLower))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing - 2*5 ,str(int(round(valueLeftUpperLowerLateral))))
                StaticResultsPage.drawCentredString(WidthMargin + LeftRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing - 2*5 ,str(valueLeftAngleRange))
                
                # Values- Right
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing - 5 ,str(int(round(valueRightUpperLateral))))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing - 5 ,str(int(round(valueRightUpperLower))))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing - 5 ,str(int(round(valueRightLateralLower))))
                StaticResultsPage.drawCentredString(WidthMargin + RightRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing - 5 ,str(valueRightDistRange))
                
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing - 2*5 ,str(int(round(valueRightUpperLateralLower))))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing - 2*5 ,str(int(round(valueRightLateralUpperLower))))
                StaticResultsPage.drawCentredString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing - 2*5 ,str(int(round(valueRightUpperLowerLateral))))
                StaticResultsPage.drawCentredString(WidthMargin + RightRangeColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing - 2*5 ,str(valueRightAngleRange))
            
            
            StaticResultsPage.showPage() # Finishes the Current Page
            
            if self.valueLeftFootModelCheck == '1' or self.valueRightFootModelCheck == '1':
                # Add Foot Static Posture if Foot Model was used
                # Page Title
                StaticResultsPage.setFillColor(reportlabColors.lightgrey)
                StaticResultsPage.rect(WidthMargin,HeightMargin + DrawRegionHeight,DrawRegionWidth,-30,stroke = 0, fill = 1)
                StaticResultsPage.setFont("Times-Bold", 12)
                StaticResultsPage.setFillGray(0.0)
                StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 12,"Shriners Hospital for Children- Greenville, SC")
                StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 25,"Motion Analysis Center")
                StaticResultsPage.drawCentredString(PageWidth/2,PageHeight - HeightMargin - 50,"-Static Report-")
                
                # Static Posture- Labels
                StaticResultsPage.setFont("Times-Bold", 12)
                StaticResultsPage.setStrokeGray(0.75)
                VerticalOffsetFromTitle = 80
                LabelColumnSpacing = 150
                LeftColumnSpacing = 200
                RightColumnSpacing = 300
                StaticResultsPage.drawString(WidthMargin, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Foot Posture (degrees)")
                StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Left")
                StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle, "Right")
                StaticResultsPage.rect(WidthMargin -5 , PageHeight - HeightMargin -VerticalOffsetFromTitle + 15, DrawRegionWidth + 5, -(9*LineSpacing + 5),stroke = 1, fill = 0)
                
                StaticResultsPage.setFont("Times-Roman", 11)
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,"Hindfoot Pitch")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,"Hindfoot Progression")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,"Hindfoot Varus/Valgus")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,"Ankle Complex Varus/Valgus")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,"Forefoot Pitch")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,"Forefoot Progression")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,"Midfoot Complex Ab/Adduction")
                StaticResultsPage.drawRightString(WidthMargin + LabelColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,"MTP1 Varus/Valgus")
    
            
                # Static Posture- Left Values
                if len(str.split(LeftHindfootPitch.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,str.split(LeftHindfootPitch.get())[0])
                if len(str.split(LeftHindfootProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str.split(LeftHindfootProgression.get())[0])
                if len(str.split(LeftHindfootInvEversion.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str.split(LeftHindfootInvEversion.get())[0])
                if len(str.split(LeftAnkleComplexInvEversion.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str.split(LeftAnkleComplexInvEversion.get())[0])
                if len(str.split(LeftForefootPitch.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str.split(LeftForefootPitch.get())[0])
                if len(str.split(LeftForefootProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str.split(LeftForefootProgression.get())[0])
                if len(str.split(LeftMidfootAbAdduction.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,str.split(LeftMidfootAbAdduction.get())[0])
                if len(str.split(LeftHalluxProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,str.split(LeftHalluxProgression.get())[0])
    
    
                # Static Posture- Left Direction
                if len(str.split(LeftHindfootPitch.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , '  ' + str.split(LeftHindfootPitch.get())[1])
                if len(str.split(LeftHindfootProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing , '  ' + str.split(LeftHindfootProgression.get())[1])
                if len(str.split(LeftHindfootInvEversion.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing , '  ' + str.split(LeftHindfootInvEversion.get())[1])
                if len(str.split(LeftAnkleComplexInvEversion.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , '  ' + str.split(LeftAnkleComplexInvEversion.get())[1])
                if len(str.split(LeftForefootPitch.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing , '  ' + str.split(LeftForefootPitch.get())[1])
                if len(str.split(LeftForefootProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing , '  ' + str.split(LeftForefootProgression.get())[1])
                if len(str.split(LeftMidfootAbAdduction.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing , '  ' + str.split(LeftMidfootAbAdduction.get())[1])
                if len(str.split(LeftHalluxProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + LeftColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing , '  ' + str.split(LeftHalluxProgression.get())[1])
                
                
                # Static Posture- Right Values
                if len(str.split(RightHindfootPitch.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing ,str.split(RightHindfootPitch.get())[0])
                if len(str.split(RightHindfootProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing ,str.split(RightHindfootProgression.get())[0])
                if len(str.split(RightHindfootInvEversion.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing ,str.split(RightHindfootInvEversion.get())[0])
                if len(str.split(RightAnkleComplexInvEversion.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing ,str.split(RightAnkleComplexInvEversion.get())[0])
                if len(str.split(RightForefootPitch.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing ,str.split(RightForefootPitch.get())[0])
                if len(str.split(RightForefootProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing ,str.split(RightForefootProgression.get())[0])
                if len(str.split(RightMidfootAbAdduction.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing ,str.split(RightMidfootAbAdduction.get())[0])
                if len(str.split(RightHalluxProgression.get())) > 0:
                    StaticResultsPage.drawRightString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing ,str.split(RightHalluxProgression.get())[0])
    
    
                # Static Posture- Right Direction
                if len(str.split(RightHindfootPitch.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 1 * LineSpacing , '  ' + str.split(RightHindfootPitch.get())[1])
                if len(str.split(RightHindfootProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 2 * LineSpacing , '  ' + str.split(RightHindfootProgression.get())[1])
                if len(str.split(RightHindfootInvEversion.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 3 * LineSpacing , '  ' + str.split(RightHindfootInvEversion.get())[1])
                if len(str.split(RightAnkleComplexInvEversion.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 4 * LineSpacing , '  ' + str.split(RightAnkleComplexInvEversion.get())[1])
                if len(str.split(RightForefootPitch.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 5 * LineSpacing , '  ' + str.split(RightForefootPitch.get())[1])
                if len(str.split(RightForefootProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 6 * LineSpacing , '  ' + str.split(RightForefootProgression.get())[1])
                if len(str.split(RightMidfootAbAdduction.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 7 * LineSpacing , '  ' + str.split(RightMidfootAbAdduction.get())[1])
                if len(str.split(RightHalluxProgression.get())) > 1:
                    StaticResultsPage.drawString(WidthMargin + RightColumnSpacing, PageHeight - HeightMargin -VerticalOffsetFromTitle - 8 * LineSpacing , '  ' + str.split(RightHalluxProgression.get())[1])
    
                
                StaticResultsPage.showPage() # Finishes the Current Page
            
            try:
                StaticResultsPage.save()
                SaveErrorMessagesLabel.place(x=50,y=930, width=650,height=15)
                SaveErrorMessagesLabel['text'] = 'Static Results file saved'
                SaveErrorMessagesLabel['fg']='seagreen'
            except:
                SaveErrorMessagesLabel.place(x=50,y=930, width=650,height=15)
                SaveErrorMessagesLabel['text'] = 'Warning: Results file could not be saved. Close the Pdf file and try again.'
      
                    
#Calls the main Function
app = Static_Main()
#Centers the App on Monitor
ScreenWidth = app.winfo_screenwidth()
ScreenHeight = app.winfo_screenheight()
x=(ScreenWidth/2) - (AppWidth/2)
y=0 #Put the App at Top of Monitor
app.geometry('%dx%d+%d+%d' % (AppWidth, AppHeight, x, y))
app.resizable(0,0)

app.mainloop()
