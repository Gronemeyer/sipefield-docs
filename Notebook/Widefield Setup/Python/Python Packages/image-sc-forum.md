# 240920 Forum Response

Hey @talley,

I appreciate you taking the time to test this out. Attached is the configuration file I am using. I currently have a work around also swallows the 107 exception and uploads the pattern. The Arduino does not hardware sequence naturally during an MDA on the new MMCore engine; the Arduino, itself, does sequence naturally independent of the engine once the sequence is uploaded. Therefore, at the sacrifice of channel metadata, I start the Arduino-Switch sequence, *then* the camera sequence:
```python

def load_arduino_led(mmc):
    """ Load Arduino-Switch device with a sequence pattern and start the sequence """
    mmc.getPropertyObject('Arduino-Switch', 'State').loadSequence(['4', '4', '2', '2'])
    mmc.getPropertyObject('Arduino-Switch', 'State').setValue(4) # seems essential to initiate serial communication
    mmc.getPropertyObject('Arduino-Switch', 'State').startSequence()

mmc.run_mda(MDASequence(time_plan={"interval":0, "loops": self.config.num_frames}), output=self._create_save_directory())
```

The above code overcomes the error you were able to isolate to the arduino-input. Here is my output from your script confirming your idea: 

```python
# ```python
# core.loadDevice("Arduino-Input", "Arduino", "Arduino-Input") commented out:
In [1]: runfile('C:/sipefield-workbench/talley-image-forum-arduino-mmc-test.py')
	try 1 loaded
	done

In [2]: core.reset()

# Uncommenting the troublesome line of code as suggested:
In [3]: runfile('C:/sipefield-workbench/talley-image-forum-arduino-mmc-test.py')
	try 1 failed!! Error in device "Arduino-Switch": Error in communication with Arduino board (107)
	done
```

So, I removed the Arduino-input from the config file, and the same errors emerge. I produced a debug Corelog from Java MicroManager App, testing these variations of the MDA(0 interval , 2 Channel, 100 loops) to help isolate the issue. It seems related, I speculate, to both the new engine and sequence buffer size (I have 132 gbs available):

1. (2) 255 mb sequence buffer, new Core engine 

2024-09-20T17:20:18.041794 tid3796 [dbg,App] [UI] JButton "Acquire!"
2024-09-20T17:20:18.068014 tid17968 [IFO,dev:Arduino-Switch] Sequence had 0 transitions
2024-09-20T17:20:19.178535 tid17968 [IFO,dev:Arduino-Switch] Sequence had 13 transitions
2024-09-20T17:20:21.558523 tid17968 [IFO,dev:Arduino-Switch] Sequence had 14 transitions (??)
...

2. 32 gb sequence buffer, new Core engine

2024-09-20T17:21:34.277656 tid3796 [dbg,Core] Did set circular buffer size to 32000 MB
2024-09-20T17:21:43.501757 tid3796 [dbg,App] [UI] JButton "Acquire!" clicked in AcqControlDlg
2024-09-20T17:21:43.520498 tid17968 [IFO,dev:Arduino-Switch] Sequence had 1 transitions
2024-09-20T17:21:44.654981 tid17968 [IFO,dev:Arduino-Switch] Sequence had 13 transitions
...

3. 32 gb sequence buffer, old engine

2024-09-20T17:22:08.911268 tid3796 [dbg,App] [UI] JMenu "Tools" clicked in MainFrame.
2024-09-20T17:22:11.866271 tid3796 [dbg,App] [UI] JCheckBox "Use new Acquisition Engine (experimental)" toggled off in OptionsDlg.

2024-09-20T17:22:16.218792 tid3796 [dbg,App] [UI] JButton "Acquire!" clicked in AcqControlDlg.
2024-09-20T17:22:16.393767 tid3564 [dbg,App] [AE] ##### BEGIN acquisition event ...
2024-09-20T17:22:20.789042 tid3564 [dbg,App] [AE] ##### END acquisition event ...
2024-09-20T17:22:20.836491 tid3564 [IFO,dev:Arduino-Switch] Sequence had 203 transitions
2024-09-20T17:22:20.887462 tid21576 [IFO,App] 200 images stored in 4670 ms.

The pymmcore_plus log matches the new core engine log, but with more variation in the length of the sequence the Arduino stutters through:

2024-09-20T17:07:41.970    tid0x5848 [INFO,pymmcore-plus] MDA Started: metadata={'pymmcore_widgets': {'version': '0.7.2'}, 'napari_micromanager': {'split_channels': False}} axis_order=('t', 'p', 'c') stage_positions=(Position(x=None, y=None, z=None, name=None, sequence=None),) channels=(Channel(config='Blue', group='Channel', exposure=19.0, do_stack=True, z_offset=0.0, acquire_every=1, camera=None), Channel(config='Violet', group='Channel', exposure=19.0, do_stack=True, z_offset=0.0, acquire_every=1, camera=None)) time_plan=TIntervalLoops(prioritize_duration=False, interval=datetime.timedelta(0), loops=100) ...

2024-09-20T17:17:58.283367 tid18404 [IFO,dev:Arduino-Switch] Sequence had 13 transitions
2024-09-20T17:17:59.301270 tid5764 [IFO,dev:Dhyana] Sequence thread exiting
2024-09-20T17:17:59.329    tid0x47e4 [INFO,pymmcore-plus] index=mappingproxy({'t': 36, 'p': 0, 'c': 0})...
2024-09-20T17:17:59.361075 tid18404 [IFO,dev:Arduino-Switch] Sequence had 17 transitions
2024-09-20T17:18:00.349382 tid6656 [IFO,dev:Dhyana] Sequence thread exiting
2024-09-20T17:18:00.360    tid0x47e4 [INFO,pymmcore-plus] index=mappingproxy({'t': 42, 'p': 0, 'c': 0})...
2024-09-20T17:18:00.368594 tid18404 [IFO,dev:Arduino-Switch] Sequence had 14 transitions
2024-09-20T17:18:01.279910 tid20368 [IFO,dev:Dhyana] Sequence thread exiting
2024-09-20T17:18:01.317    tid0x47e4 [INFO,pymmcore-plus] index=mappingproxy({'t': 48, 'p': 0, 'c': 0}) ...
2024-09-20T17:18:01.363577 tid18404 [IFO,dev:Arduino-Switch] Sequence had 16 transitions




# Forum Response for Hardware Sequencing

^1785be
### Trouble with Hardware-Triggered MDA Sequence Synchronizing Arduino LED Controller State and sCMOS Global Exposure - Usage & Issues - [forum.image.sc](https://forum.image.sc/t/trouble-with-hardware-triggered-mda-sequence-synchronizing-arduino-led-controller-state-and-scmos-global-exposure/99659)

the code that determines whether 2 events can be combined into a hardware-triggered sequence is [here](https://github.com/pymmcore-plus/pymmcore-plus/blob/c13023ab801129797523c0dd13bfdb808e815efb/src/pymmcore_plus/core/_sequencing.py#L158).

first, I can definitely say that, at this point only sequences with an interval of 0 will be hardware sequenceable (just as in MM i believe). Anything else (even a short delay of 1/70 as in your script) will hit this line here and fail to be sequenced:

> in the napari-micromanager plugin, the MDA sequence widget does not allow the user to set the time interval to 0

with the above in mind, this is definitely a problem for you one that can be easily fixed. However, for now, let’s leave napari out of this and stick with your (very helpful) simplified script. Have you tried, for example, using no interval?:

```python
mda_sequence = useq.MDASequence(
    time_plan=useq.TIntervalLoops(interval=0, loops=10),
    channels=["Blue", "Violet"],
)
```

(even if the napari widget isn’t currently capable of that, it’s definitely possible to create an MDASequence with no time delay)

Please try running your same script with an interval of 0 and let me know if it helps.

---

some general tips that may also help:

1. When you create an instance of `MDASequence`, you can iterate over it to see the events that would be created:

```python
In [2]: import useq

In [3]: mda_sequence = useq.MDASequence(
   ...:     time_plan=useq.TIntervalLoops(interval=0, loops=5),
   ...: )

In [4]: list(mda_sequence)
Out[4]:

[
    MDAEvent(index=mappingproxy({'t': 0}), min_start_time=0.0),
    MDAEvent(index=mappingproxy({'t': 1}), min_start_time=0.0),
    MDAEvent(index=mappingproxy({'t': 2}), min_start_time=0.0),
    MDAEvent(index=mappingproxy({'t': 3}), min_start_time=0.0),
    MDAEvent(index=mappingproxy({'t': 4}), min_start_time=0.0)
]
```

if you’d like to check whether the default micro-manager engine in pymmcore_plus is capable of sequencing any/all of those events when loaded with your microscope config you can pass the sequence through the engine’s `event_iterator`. See in the example below how the same sequence that was 5 events above gets turned into 1 sequenced event below:

```python
In [3]: from pymmcore_plus import CMMCorePlus
   ...: mmc = CMMCorePlus.instance()
   ...: mmc.loadSystemConfiguration()
   ...: print(list(mmc.mda.engine.event_iterator(mda_sequence)))
[
    SequencedEvent(
        index={'t': 0},
        min_start_time=0.0,
        events=(
            MDAEvent(index=mappingproxy({'t': 0}), min_start_time=0.0),
            MDAEvent(index=mappingproxy({'t': 1}), min_start_time=0.0),
            MDAEvent(index=mappingproxy({'t': 2}), min_start_time=0.0),
            MDAEvent(index=mappingproxy({'t': 3}), min_start_time=0.0),
            MDAEvent(index=mappingproxy({'t': 4}), min_start_time=0.0)
        ),
        exposure_sequence=(),
        x_sequence=(),
        y_sequence=(),
        z_sequence=()
    )
]
```

if you _don’t_ see your events getting turned into a `SequencedEvent`, then you’ll know something is going wrong… and then you need to determine which events were not sequencable and why. the easiest way to get a _reason_ why something may or may not be sequenceable is to do the following:

```python
In [12]: from pymmcore_plus.core._sequencing import can_sequence_events

In [13]: events = list(mda_sequence)

In [14]: can_sequence_events(mmc, events[0], events[1], return_reason=True)
Out[14]: (True, '')
```

whereas, with a time delay:

```python
In [15]: mda_sequence = useq.MDASequence(
    ...:     time_plan=useq.TIntervalLoops(interval=1/70, loops=5),
    ...: )

In [16]: events = list(mda_sequence)

In [17]: can_sequence_events(mmc, events[0], events[1], return_reason=True)
Out[17]: (False, 'Must pause at least 0.014286 s between events.')
```

that will also let you know if its some other hardware related thing (unrelated to time delay) that is preventing hardware triggering


## Response

Thank you @talley for your helpful and detailed response (and also for your work on these projects!).

First, I'll acknowledge that I tested your confirmation that, indeed, the time interval 0 does initiate hardware sequencing and camera streaming through the Napari interface (and with the Useq schema in general). 

Thank you for your direction to the sequencability code. Researching the pymmcore_plus API a bit more I made a useful (lazy) way to find the sequencable properties of a loaded MMCore Config file:

```python
# Print True or False for every property's sequencability (without Device names)
for settings in mmc.iterProperties():
    print(f'{settings.isSequenceable()} : The setting: {settings.name} is sequencable')
```

This helped me then isolate issues with specific Device Properties that were not sequencable. The issue seems to be related to my lack of understanding towards the MicroManager Configuration file setup. It seems that, based on my configuration, the MMCore is not interpreting the setup of my hardware how I would like; specifically, the sequences uploaded to the Arduino are limited by the Arduino's maximum Sequence length (12). I will provide some detailed context for how I came to this hypothesis.

Here are details from the [Arduino Device page](https://micro-manager.org/Arduino#usage-notes) for how I am using the device:

|Name |Description|
|---|---|
|Arduino-Switch |Digital output pattern set across pins 8 to 13. See usage in Digital IO.|
|Arduino-Shutter |Toggles the digital outputs pattern across pins 8 to 13. Set all pins off when the shutter is closed, and restores the value set in Switch-State when the shutter is opened.|

Here is my Configured setup:

```python
In [1]: mmc.describe()

Out [1]: MMCore version 11.1.1, Device API version 71, Module API version 10
┌─────────────────┬────────────┬─────────┬──────────────────┬─────────────────┐
│ Device Label    │ Type       │ Current │ Library::Device… │ Description     │
├─────────────────┼────────────┼─────────┼──────────────────┼─────────────────┤
│ COM12           │ Serial     │         │ SerialManager::… │ Serial          │
│                 │            │         │                  │ communication   │
│                 │            │         │                  │ port            │
│ Dhyana          │ 📷 Camera  │ Camera  │ TUCam::TUCam     │ TUCSEN Camera   │
│ Arduino-Hub     │ 🔌 Hub     │         │ Arduino::Arduin… │ Hub (required)  │
│ Arduino-Switch  │ 🟢 State   │         │ Arduino::Arduin… │ Digital out     │
│                 │            │         │                  │ 8-bit           │
│ Arduino-Shutter │ 💡 Shutter │ Shutter │ Arduino::Arduin… │ Shutter         │
│ Arduino-Input   │ Generic    │         │ Arduino::Arduin… │ ADC             │
│ Core            │ 💙 Core    │         │ ::Core           │ Core device     │
└─────────────────┴────────────┴─────────┴──────────────────┴─────────────────┘
```

I found that the "Sequencable" setting in my [Arduino firmware](https://github.com/micro-manager/mmCoreAndDevices/blob/main/DeviceAdapters/Arduino/AOTFcontroller/AOTFcontroller.ino) is *not*, itself, sequencable--not that I expected it to be--and including the setting in the Channel Group configuration was part of the problem. Similar to other settings such as "Blanking." It is the Arduino-Switch 'State' property that is sequenced, but requires the 'Sequence' Property to be 'On':

```python
arduino_sequencing = mmc.getPropertyObject("Arduino-Switch", "Sequencing")
arduino_sequencing.isSequenceable()
Out[87]: False

arduino_blanking = mmc.getPropertyObject("Arduino-Switch", "Blanking Mode")
arduino_blanking.isSequenceable()
Out[87]: False

# For State Switch to be sequencable:
mmc.setProperty('Arduino-Switch', 'Sequence', 'On')
switch = mmc.getPropertyObject('Arduino-Switch', 'State')
switch.isSequenceable()
Out[17]: True

```

Therefore, I reduced my Channel configuration to just contain the 'State' property:

```python
for configs in mmc.iterConfigGroups():
    print(configs)

Out[2]:
	ConfigGroup 'Channel'
	=====================
	Blue:
	  Arduino-Switch:
	    - State: 4 # Pinout Byte code corresponding to 488nm LED
	Violet:
	  Arduino-Switch:
	    - State: 16 # Pinmout Byte code corresponding to 405nm LED

In[18]: can_sequence_events(mmc, events[0], events[1], return_reason=True)
Out[19]: (True, '')
```

However, it seems to hardware sequence only 12 MDA Events at a time, resulting in a software-triggered hiccup every 12 frames. Interestingly, once the acquisition is complete, *and with Auto-Shutter 'ON'*, the Camera-Arduino-LED circuit loop is left to work autonomously; the LEDs flash under the lens at the exposure rate of the camera as intended. I believe this "error" explains why this occurs:

```python
lib\site-packages\pymmcore_plus\mda\_engine.py:378, in MDAEngine.setup_sequenced_event(self=<pymmcore_plus.mda._engine.MDAEngine object>, event=SequencedEvent(index=mappingproxy({'t': 6, 'p': ...=(), x_sequence=(), y_sequence=(), z_sequence=()))

376 with suppress(RuntimeError):
377 core.stopPropertySequence(dev, prop)
--> 378 core.loadPropertySequence(dev, prop, value_sequence)

core = <CMMCorePlus at 0x2a4b6e5d3a0>
value_sequence = ['4', '16', '4', '16', '4', '16', '4', '16', '4', '16', '4', '16']
dev = 'Arduino-Switch'
prop = 'State'
380 # TODO: SLM
381
382 # preparing a Sequence while another is running is dangerous.
383 if core.isSequenceRunning():

RuntimeError: Error in device "Arduino-Switch": Error in communication with Arduino board (107)
```

The error is useful in context [Arduino firmware source code](https://github.com/micro-manager/mmCoreAndDevices/blob/main/DeviceAdapters/Arduino/AOTFcontroller/AOTFcontroller.ino) . Here are the properties the Arduino expects to receive from MMCore.

```c
   const int SEQUENCELENGTH = 12;  // this should be good enough for everybody;)
   byte triggerPattern_[SEQUENCELENGTH] = {0,0,0,0,0,0,0,0,0,0,0,0};
   unsigned int triggerDelay_[SEQUENCELENGTH] = {0,0,0,0,0,0,0,0,0,0,0,0};
   int patternLength_ = 0;
   byte repeatPattern_ = 0;
   volatile long triggerNr_; // total # of triggers in this run (0-based)
   volatile long sequenceNr_; // # of trigger in sequence (0-based)
   int skipTriggers_ = 0;  // # of triggers to skip before starting to generate patterns
   byte currentPattern_ = 0;
   const unsigned long timeOut_ = 1000;
   bool blanking_ = false;
   bool blankOnHigh_ = false;
   bool triggerMode_ = false;
   boolean triggerState_ = false;
```

Current hypothesis: The Arduino expects a sequence *pattern* that it will loop through, hardware sequenced by Camera-Output-Trigger TTL on pin 2. I think that instead of giving the Arduino a 'sequenceNr_', the MMCore mda is attempting to send a new pattern each mda "loop" essentially keeping the computer "in-the-loop." I am having a hard time intuiting *why* this would occur--I imagine I am just simply missing some key information! 

With regards to the Config settings, this has been easier to test within the napari-micromanager setup. When just building my own MDA I notice I do not as easily get a proper acquisition sequence with the Camera. It seems the Camera needs to be included in the MDA sequence somehow, but it hasn't been clear to me how.

Let me know if I can provide any more details. Apologies for the long post, but I figure this documentation may help anyone running into a similar issue. 

```python
value_sequence = ['4', '16', '4', '16', '4', '16', '4', '16', '4', '16', '4', '16']
dev = 'Arduino-Switch'
prop = 'State'
mmc.setPropertySequence
mmc.startPropertySequence
```

```python
In [1]: mmc.describe()

Out [1]: MMCore version 11.1.1, Device API version 71, Module API version 10
┌─────────────────┬────────────┬─────────┬──────────────────┬─────────────────┐
│ Device Label    │ Type       │ Current │ Library::Device… │ Description     │
├─────────────────┼────────────┼─────────┼──────────────────┼─────────────────┤
│ COM12           │ Serial     │         │ SerialManager::… │ Serial          │
│                 │            │         │                  │ communication   │
│                 │            │         │                  │ port            │
│ Dhyana          │ 📷 Camera  │ Camera  │ TUCam::TUCam     │ TUCSEN Camera   │
│ Arduino-Hub     │ 🔌 Hub     │         │ Arduino::Arduin… │ Hub (required)  │
│ Arduino-Switch  │ 🟢 State   │         │ Arduino::Arduin… │ Digital out     │
│                 │            │         │                  │ 8-bit           │
│ Arduino-Shutter │ 💡 Shutter │ Shutter │ Arduino::Arduin… │ Shutter         │
│ Arduino-Input   │ Generic    │         │ Arduino::Arduin… │ ADC             │
│ Core            │ 💙 Core    │         │ ::Core           │ Core device     │
└─────────────────┴────────────┴─────────┴──────────────────┴─────────────────┘

In [46]: Arduino = mmc.getAdapterObject('Arduino')

In [57]: Arduino.loaded_devices
Out[57]: 
	(<Device 'Arduino-Hub' (Arduino::Arduino-Hub) on CMMCorePlus at 0x1fe770b8180: 4 properties>,
	 <Device 'Arduino-Switch' (Arduino::Arduino-Switch) on CMMCorePlus at 0x1fe770b8180: 8 properties>,
	 <Device 'Arduino-Shutter' (Arduino::Arduino-Shutter) on CMMCorePlus at 0x1fe770b8180: 4 properties>,
	 <Device 'Arduino-Input' (Arduino::Arduino-Input) on CMMCorePlus at 0x1fe770b8180: 12 properties>)


Arduino = mmc.getDeviceObject('Arduino-Switch')
Arduino.description()
Out[74]: 'Digital out 8-bit'

blanking = mmc.getPropertyObject("Arduino-Switch", "Blanking Mode")
blanking.allowedValues()
Out[85]: ('Off', 'On')

blanking.isSequenceable()
Out[87]: False

blanking.value
Out[89]: 'Off'

blanking.setValue('On')

blanking.value
Out[93]: 'On'

blanking.isSequenceable()
Out[94]: False
```

```python
lib\site-packages\pymmcore_plus\mda\_engine.py:378, in MDAEngine.setup_sequenced_event(self=<pymmcore_plus.mda._engine.MDAEngine object>, event=SequencedEvent(index=mappingproxy({'t': 6, 'p': ...=(), x_sequence=(), y_sequence=(), z_sequence=()))

376 with suppress(RuntimeError):

377 core.stopPropertySequence(dev, prop)

--> 378 core.loadPropertySequence(dev, prop, value_sequence)

core = <CMMCorePlus at 0x2a4b6e5d3a0>

value_sequence = ['4', '16', '4', '16', '4', '16', '4', '16', '4', '16', '4', '16']

dev = 'Arduino-Switch'

prop = 'State'

380 # TODO: SLM

381

382 # preparing a Sequence while another is running is dangerous.

383 if core.isSequenceRunning():

  

RuntimeError: Error in device "Arduino-Switch": Error in communication with Arduino board (107)
```
---

if you determine that all it was was using an interval of 0, we can easily fix the widget in napari to make it easier to set this

