---
website: https://micro-manager.org/
---
![Micro-Manage Block Diagram](https://micro-manager.org/media/Block_diagram.gif "Micro-Manage Block Diagram")


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

[[NI USB-6001]] : https://micro-manager.org/NIDAQ
[[Teensy]]

