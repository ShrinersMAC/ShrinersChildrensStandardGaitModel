# Shriners Children's Standard Gait Model (SCGM)
Additional detail can be found within our recent publication in [Gait & Posture](10.1016/j.gaitpost.2024.03.006).

## User Guides
### Licensing
The SCGM is licensed under the [GNU General Public License v3.0](LICENSE)
  
### Set-up and Installation
This model is built in Python 3.11. Refer to the [Python installation and set-up instructions here](User%20Guides/1.Python%20and%20Nexus%20Version%20Requirements%20and%20Installation.pdf).

### Usage
This model operates through a series of Vicon Nexus pipelines. Refer to the [Vicon Nexus set-up instructions here](User%20Guides/2.Shriners%20Gait%20Model%20Setup.pdf).

## Model Overview
### Anthropometric Measures

|                  | Measurement                                                               | Usage                                            |
|-----------------:|---------------------------------------------------------------------------|--------------------------------------------------|
|      Height (mm) | Weight bearing; plantar surface of foot to top of head                    | Not used in modeling                             |
|        Mass (kg) | On forceplate or on scale                                                 | Estimate segmental masses and moments of inertia |
|   Hip width (mm) | In supine; Between the left and right anterior superior iliac spine (ASIS)| Estimate hip joint center                        |
|  Leg length (mm) | In supine; Distance between ASIS to medial knee to medial malleolus       | Estimate hip joint center                        |
|  Knee width (mm) | Between lateral and medial femoral condyles                               | Estimate knee joint center                       |
| Ankle width (mm) | Between lateral and medial malleoli                                       | Estimate ankle joint center                      |

### Marker Set
The SCGM consists of 23 markers in total

#### *Trunk:*
|                     | Landmark              | Location                                                           |
|--------------------:|-----------------------|--------------------------------------------------------------------|
|                  C7 | 7th cervical vertebra | Prominence of C7 vertebra                                          |
| Left/Right_Clavicle | Sterno-clavicular     | Thumb width below clavicle, equidistant from centerline of sternum |

![torso_markers](User%20Guides/Media/markers_torso.png)

#### *Pelvis*
|                 | Landmark                       | Location                                                                    |
|----------------:|--------------------------------|-----------------------------------------------------------------------------|
| Left/Right_ASIS | Anterior superior iliac spine  | Superior to inferior edge of ASIS                                           |
| Left/Right_PSIS | Posterior superior iliac spine | Directly on left/right posterior superior iliac spine. Look for the dimples |

![pelvis_markers](User%20Guides/Media/markers_pelvis.png)

#### *Thigh/Shank*
|                              | Landmark                | Location                                                                                           |
|------------------------------|-------------------------|----------------------------------------------------------------------------------------------------|
|           Left/Right_Patella | Patella                 | Center of patella                                                                                  |
|      Left/Right_Lateral_Knee | Lateral femoral condyle | Posterior lateral condyles at center of a visualized circle                                        |
| *Left/Right_Medial_Knee.Cal** | Medial femoral condyle  | Posterior medial condyles at the center of a visualized circle, which could be fit to this anatomy |
| Left/Right_Lower_Tibia       | Anterior tibia          | On the anterior crest of lower third of tibia                                                      |

> [!NOTE]  
> *The `Medial_Knee` markers are **calibration** markers only, and are removed after the static calibration trial

![leg_markers](User%20Guides/Media/markers_leg.png)

#### *Foot*
|                                   | Landmark                                     | Location                                                                                        |
|-----------------------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------|
|      Left/Right_Lateral_Malleolus | Fibula lateral malleolus                     | Lateral malleoli so that marker center lies on ankle flexion/extension axis.                    |
| *Left/Right_Medial_Malleolus.Cal** | Tibia medial malleolus                       | Medial malleoli so marker center lies on ankle flexion/extension axis.                          |
| Left/Right_Heel                   | Heel                                         | Medial/lateral center of posterior calcaneus                                                    |
| Left/Right_2nd3rd_MT_Head         | Gap between the 2nd and 3rd metatarsal heads | Dorsal aspect of foot between 2nd and 3rd metatarsal heads (above metatarsal-phalangeal joints) |

> [!NOTE]  
> *The `Medial_Malleolus` markers are **calibration** markers only, and are removed after the static calibration trial

![feet_markers](User%20Guides/Media/markers_feet.png)

### Segments
+ The SCGM defines 8 distinct segments

+ The SCGM defines 10 distinct joints

### Kinematic and Kinetic Outputs
