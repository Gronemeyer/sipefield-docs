[[Current Setup]]
[[Arduino]]
[[MicroManager#^cf4e08|Micromanager Arduino Device Setup]]

[[Hardware-triggering with Micro-Manager a case study]]
[[LLM finetuning]]
[[Dhyana 400BSI V2#^fe9623|Dhyana Trigger Instructions]]

Forum response:
[[pymmcore-plus#^1785be]]



> [!LIST] Tasks
> ```tasks
> 
> ```


## [[PyLab]] Python Project File Layout and Description
- `__init__.py`: Make Python treat directories as packages. Can be empty or include imports from your modules.
- `__main__.py`: Entry point when package is run as a script. Call your main function here.
- `cli.py`: Parse command line arguments, call main function to start pipeline.
- `communication.py`: Functions for communicating with other computers, serial ports.
- `arduino.py`, `camera.py`: Classes or functions to interact with Arduino, camera.
- `matlab.py`: Functions to run Matlab scripts.
- `data.py`: Functions for data manipulation, visualization.
- `main.py`: Main function to orchestrate the pipeline.
# [[Current Setup.canvas|Current Setup]]

[SEMANTIC VERSIONING GUIDELINES](https://semver.org/)
