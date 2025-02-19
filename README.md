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
|-----------------------------:|-------------------------|----------------------------------------------------------------------------------------------------|
|           Left/Right_Patella | Patella                 | Center of patella                                                                                  |
|      Left/Right_Lateral_Knee | Lateral femoral condyle | Posterior lateral condyles at center of a visualized circle                                        |
| *Left/Right_Medial_Knee.Cal** | Medial femoral condyle  | Posterior medial condyles at the center of a visualized circle, which could be fit to this anatomy |
| Left/Right_Lower_Tibia       | Anterior tibia          | On the anterior crest of lower third of tibia                                                      |

> [!NOTE]  
> *The `Medial_Knee` markers are **calibration** markers only, and are removed after the static calibration trial

![leg_markers](User%20Guides/Media/markers_leg.png)

#### *Foot*
|                                   | Landmark                                     | Location                                                                                        |
|----------------------------------:|----------------------------------------------|-------------------------------------------------------------------------------------------------|
|      Left/Right_Lateral_Malleolus | Fibula lateral malleolus                     | Lateral malleoli so that marker center lies on ankle flexion/extension axis.                    |
| *Left/Right_Medial_Malleolus.Cal** | Tibia medial malleolus                       | Medial malleoli so marker center lies on ankle flexion/extension axis.                          |
| Left/Right_Heel                   | Heel                                         | Medial/lateral center of posterior calcaneus                                                    |
| Left/Right_2nd3rd_MT_Head         | Gap between the 2nd and 3rd metatarsal heads | Dorsal aspect of foot between 2nd and 3rd metatarsal heads (above metatarsal-phalangeal joints) |

> [!NOTE]  
> *The `Medial_Malleolus` markers are **calibration** markers only, and are removed after the static calibration trial

![feet_markers](User%20Guides/Media/markers_feet.png)

### Segments
The SCGM defines 8 distinct segments:
  1. Trunk
  2. Pelvis
  3. Left/Right femur
  4. Left/Right tibia
  5. Left/Right ankle

The SCGM defines 10 distinct joints:
| Joint                     | Distal Segment   | Proximal Segment | Cardan Order     | Angles                                              |
|--------------------------:|------------------|------------------|------------------|-----------------------------------------------------|
| *Trunk*                   | Trunk            | Global           | [ZXY]            | X: Obliquity<br>Y: Tilt<br>Z: Rotation              |
| *Pelvis*                  | Pelvis           | Global           | [ZXY]            | X: Obliquity<br>Y: Tilt<br>Z: Rotation              |
| *Left/Right Hip*          | Femur            | Pelvis           | [YXZ]            | X: Ab/Adduction<br>Y: Flex/Extension<br>Z: Rotation |
| *Left/Right Knee*         | Proximal Tibia   | Femur            | [YXZ]            | X: Varus/Valgus<br>Y: Flex/Extension<br>Z: Rotation |
| *Left/Right Ankle*        | Foot             | Distal Tibia     | [YXZ]            | Y: Dorsi/Plantarflexion<br>Z: Rotation              |
| *Left/Right Foot*         | Foot             | Global           | [YXZ]            | Z: Foot progression                                 |

> [!NOTE]
> The anatomic tibia is defined proximally for knee angle calculations and distally for ankle angle calculations in the SCGM. This ensures that tibial torsion does no pollute transverse knee and ankle rotation angles during gait.

> [!NOTE]
> Three-dimensional ankle calculations are made as specified. However, ab/adduction of the foot is not an anatomically correct angle, due to the structure of the ankle joint. Therefore, ankle ab/adduction is not typically reported.


### Biomechanical Outputs
#### *Spatiotemporal*
Example spatiotemporal outputs for the right side based on 3 walking trials:
![spatiotemporal](User%20Guides/Media/spatiotemporal.png)

#### *Kinematics*
Calculated angles (15, bilaterally) for the joints described above:
<br><br>
![kinematics](User%20Guides/Media/kinematics.png)

#### *Kinetics*

| Joint   | Distal Segment | Proximal Segment | Moments                                                                                  |
|--------:|----------------|------------------|------------------------------------------------------------------------------------------|
| *Left/Right Hip*         | Femur          | Pelvis           | X: Ab (+)/Adduction (-)<br> Y: Extension (+)/Flexion(-)<br> Z: Ext (+)/Int (-) Rotation  |
| *Left/Right Knee*        | Proximal Tibia | Femur            | X: Valgus (+)/Varus (-)<br> Y: Extension (+)/Flexion (-)<br> Z: Ext (+)/Int (-) Rotation |
| *Left/Right Ankle*       | Foot           | Distal Tibia     | Y: Plantar (+)/Dorsiflexion (-)<br> Z: Ext (+)/Int (-) Rotation                          |

> [!NOTE]
> Joint reaction forces and moments are defined internally in the Shriners Standard Gait Model – that is, a joint reaction force or moment component represents the sum total contributions from the joint structures that provide stability in the given plane.

> [!NOTE]
> Reported kinetics are typically for the sagittal and coronal planes only:
<br>

Sagittal kinetics: <br><br>
![kinetics](User%20Guides/Media/kinetics_sagittal.png)

Coronal/Frontal kinetics: <br><br>
![kinetics](User%20Guides/Media/kinetics_coronal.png)

#### *Muscle Lengths*
Muscle lengths are estimated using [???]
![kinetics](User%20Guides/Media/muscle_lengths.png)


