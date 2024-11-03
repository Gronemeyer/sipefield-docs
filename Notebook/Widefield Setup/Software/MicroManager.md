---
website: https://micro-manager.org/
relatives:
  - "[[Widefield Setup/Software/Napari|Napari]]"
  - "[[pymmcore-plus]]"
controls:
  - "[[Dhyana 400BSI V2]]"
  - "[[Arduino]]"
  - "[[Thorlabs CS165 MU]]"
---
[Micro-Manage Block Diagram](https://micro-manager.org/media/Block_diagram.gif "Micro-Manage Block Diagram")

[User Guide](https://micro-manager.org/Version_2.0_Users_Guide#sequence-acquisitions)
[Hardware Based Synchronization](https://micro-manager.org/Hardware-based_Synchronization_in_Micro-Manager)
[Download](https://micro-manager.org/Download_Micro-Manager_Latest_Release) ^963752

[Integration](https://micro-manager.org/Using_the_Micro-Manager_python_library) with [[PycroManager]] and [[pymmcore-plus]] and [[Widefield Setup/Software/Napari|Napari]]

# How to Create a Configuration file
1. Turn on the camera and devices connected to the computer
2. Launch MicroManager
4. Go to Devices > Hardware Configuration Wizard

> [!NOTE]
> Java program, avoid arbitrary clicks--be patient--be kind

3. Select radial button for "*Create New configuration*" (alternatively, you can modify and existing config)
4. From the available device menu, look for "TUCam" (assuming you have already installed [[Dhyana 400BSI V2#^65d0c1]] for micromanager) 
	- Expand, select "TUCam: TUCSEN Camera" with double click or "Add..." button
	- Press "OK" for initialization properties
5. Press next buttons (keeping all defaults) 
8. Result: ![[MicroManager Config Setup.png]]

## Device Management

[MMDevice-NI USB-6001](https://micro-manager.org/NIDAQ)
[[Teensy]]
[MMDevice-Arduino](https://micro-manager.org/Arduino)


# Multi-Camera Driver
*[Utility driver](https://micro-manager.org/Utilities) that synchronizes two camera drivers as one logical camera*

- Requires both cameras have the same ROI, which is not trivial when camera sensors have different geometry.
- By trial and error, I matched the [[Thorlabs CS165 MU]] ROI with the [[Dhyana 400BSI V2]] ROI 
	1. Set Dhyana ROI binning to 512x512
	2. set ThorCam ROI with:
```beanshell
mmc.setCameraDevice("ThorCam")
mmc.setROI(440,305,509,509);
```
```python
    mmcore2.setROI("ThorCam", 440, 305, 509, 509)
```

> [!QUOTE]
> "In the Inspector window, switch to “Composite” mode to see a 2 color overlap of the two channels. To get the two channels side by side, there are multiple steps to take. First, use the gear icon in the bottom right of the viewer window to open a “New Window for this data”. Make sure that both window are displayed in Grayscale (you do this in the Inspector window). Then press the lock icon just above the gear icon until it is red (press it twice). Move the channel slider of one of the two viewers to the right, the other to the left, so that they display different channels. Pressing Snap or Live will now show the two channels side by side." https://forum.microlist.org/t/micro-manager-multicamera-display-camera-images-side-by-side/2434/2 

