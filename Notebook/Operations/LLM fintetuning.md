
You are a python expert and mentor with experience in scientific image acquisition.

Here are the details of my project I would like help with. In subsequent messages I will send you reference material to learn from for better context before I ask exactly what I need for help.

I am setting up a control system for a widefield macroscope. The setup has three windows 10 PCs. The control hardware include a Dhyana 400BSI V2 camera, NIDAQ 6001 USB, a Teensy microcontroller that controls LEDs. This camera control system uses three Nidaq 6001, a teensy board, and the camera. I am using python and the nidaqmx plugin. The teensy board controls LEDs based on input from the Master NIDAQ (Dev1) which outputs signals on port1/line0,1,2 which correspond to violet, blue. and strobe. The teensy board also listens for output signals from the camera (exposure/frame intervals) for the strobe setting; the LEDs then strobe at the camera's exposure framerate when the teensy board is receiving the digital signal from Dev1/port1/line2. The same teensy output that drives the LEDs splits and provides analogue input to the Dev1 NIDAQ at AI 1 and AI 2 in order to log the changes. Lastly, Digital I/O on Dev1 at port0/line0,1 connect to NIDAQ Dev2 and Dev 3 at the same ports. Dev1 should listen to these ports in order to switch the LEDs on and off (or just log the input). Dev2, for example, will send a HIGH signal when a visual stimulus is presented on a screen, which should trigger the LEDs.

Here is a table summarizing the setup:

|**Component**|**Device**|**Port/Line**|**Function**|
|---|---|---|---|
|Master NIDAQ|Dev1|port1/line0|Output signal to Teensy for Violet LED|
|Master NIDAQ|Dev1|port1/line1|Output signal to Teensy for Blue LED|
|Master NIDAQ|Dev1|port1/line2|Output signal to Teensy for Strobe|
|Master NIDAQ|Dev1|AI1|Analog input from Teensy (LED status)|
|Master NIDAQ|Dev1|AI2|Analog input from Teensy (LED status)|
|Master NIDAQ|Dev1|port0/line0|Digital I/O for communication with Dev2|
|Master NIDAQ|Dev1|port0/line1|Digital I/O for communication with Dev3|
|Slave NIDAQ|Dev2|port0/line0|Digital I/O for communication with Dev1|
|Slave NIDAQ|Dev2|port0/line1|Digital I/O for communication with Dev1|
|Slave NIDAQ|Dev3|port0/line0|Digital I/O for communication with Dev1|
|Slave NIDAQ|Dev3|port0/line1|Digital I/O for communication with Dev1|
|Teensy Board|-|-|Controls LEDs based on input from Dev1|
|Camera|-|-|Provides exposure/frame intervals to Teensy|

| **Windows Computer** | **Devices**                           | **Software**                               |
| -------------------- | ------------------------------------- | ------------------------------------------ |
| Manager              | Dhyana Camera, NIDAQ-6001, Teensy 4.0 | Napari, MicroManager, Arduino IDE (Teensy) |
| Pupil                | Thorlabs Zelux Camera, NIDAQ-6001     | Napari, MicroManager                       |
| VisStim              | NIDAQ-6001, Arduino                   | PsychoPy, Arduino IDE                      |

## NIDAQ Prompt

Make sure your code uses the same practices as this example code from the nidaqmx-python github examples: 
```
"""Example of analog and digital data acquisition at the same time. This example demonstrates how to continuously acquire analog and digital data at the same time, synchronized with one another on the same device. """ import nidaqmx from nidaqmx.constants import AcquisitionType, LineGrouping, ProductCategory def get_terminal_name_with_dev_prefix(task: nidaqmx.Task, terminal_name: str) -> str: """Gets the terminal name with the device prefix. Args: task: Specifies the task to get the device name from. terminal_name: Specifies the terminal name to get. Returns: Indicates the terminal name with the device prefix. """ for device in task.devices: if device.product_category not in [ ProductCategory.C_SERIES_MODULE, ProductCategory.SCXI_MODULE, ]: return f"/{device.name}/{terminal_name}" raise RuntimeError("Suitable device not found in task.") def main(): """Continuously acquire analog and digital data at the same time.""" total_ai_read = 0 total_di_read = 0 with nidaqmx.Task() as ai_task, nidaqmx.Task() as di_task: def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data): """Callback function for reading signals.""" nonlocal total_ai_read nonlocal total_di_read ai_read = ai_task.read(number_of_samples_per_channel=number_of_samples) di_read = di_task.read(number_of_samples_per_channel=number_of_samples) total_ai_read += len(ai_read) total_di_read += len(di_read) print(f"\t{len(ai_read)}\t{len(di_read)}\t\t{total_ai_read}\t{total_di_read}", end="\r") return 0 ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai0") ai_task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.CONTINUOUS) ai_task.register_every_n_samples_acquired_into_buffer_event(1000, callback) terminal_name = get_terminal_name_with_dev_prefix(ai_task, "ai/SampleClock") di_task.di_channels.add_di_chan("Dev1/port0", line_grouping=LineGrouping.CHAN_FOR_ALL_LINES) di_task.timing.cfg_samp_clk_timing( 1000.0, terminal_name, sample_mode=AcquisitionType.CONTINUOUS ) di_task.start() ai_task.start() print("Acquiring samples continuously. Press Enter to stop.\n") print("Read:\tAI\tDI\tTotal:\tAI\tDI") input() ai_task.stop() di_task.stop() print(f"\nAcquired {total_ai_read} total AI samples and {total_di_read} total DI samples.") if __name__ == "__main__": main()
```