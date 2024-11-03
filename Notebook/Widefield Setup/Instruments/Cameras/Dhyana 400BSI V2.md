---
relatives:
  - "[[Thorlabs CS165 MU]]"
software:
  - "[[MicroManager]]"
---

Lenses
- [[Nikon AF-S Nikkor 50mm]]
- [[Nikon AF-S Nikkor 105mm]]


![[Dhyana 400BSI V2 dimensions.png]]
## [Specifications]([BSI-sCMOS-Camera-Dhyana-400BSIV2-Tucsen.pdf](file:///C:/Users/SIPE_LAB/Desktop/desktop/BSI-sCMOS-Camera-Dhyana-400BSIV2-Tucsen.pdf))
## [Drivers and Software plugins](https://www.tucsen.com/Home/Product/download/dataid/19/id/27.html) ^65d0c1
## [Trigger Instructions](https://www.tucsen.com/uploads/Camera-External-Trigger-Instructions.pdf) ^fe9623
- 3.4.1 Capture Mode:
	- Camera capture modes are divided into the following 2 categories:
		1. Sequence mode (stream mode): it is used to capture continuous image data.
		2. Trigger mode: The camera captures the images by the external signals. We call this option "trigger mode", and you can call TUCAM_Cap_SetTrigger () to configure this option. We also call the external signal "external trigger".
- ![[Dhyana Output Trigger Parameters.png]]
	- High: Output high level signal all the time.
	- Low: Output low level signal all the time.
	- Exposure Start: The signal output by the Exposure Start will be the level signal from the first line starts to exposure and the width could be customized. Exposure Start is the default mode of Port 3.
	- Readout End: The signal output by the Readout End will be the level signal from the last line starts to readout and the width could be customized. Readout End is the default mode of Port 1.
	- Global: The signal output by the Global Exposure will be the level signal from the last line starts to be exposure to the end of the first line starts to readout (The exposure time need to greater than the frame time). Global Exposure is the default mode of Port 3


![[Churchland Widefield Schematic.bmp]]

## [Quick Start Manual](https://www.tucsen.com/Public/upload/download/pdf/Dhyana%20Camera%20Quick%20Start%20-%20EN.pdf) ^5c9057

- ![[Dhyana Interface.png]]
- (4) "When USB3.0 and cameralink interfaces are connected at the same time, the default is USB3.0 interface."
- Page 15: ![[Dhyana CameraLink Driver Installation.png]]

