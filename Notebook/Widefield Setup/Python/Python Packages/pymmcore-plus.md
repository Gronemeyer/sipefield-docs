---
github: https://github.com/pymmcore-plus
---
![mm diagram](https://user-images.githubusercontent.com/1609449/202301602-00ba0fd8-df4f-4993-b0ad-8e3d1cefaf42.png)
https://forum.microlist.org/t/belatedly-announcing-pymmcore-plus-an-ecosystem-of-pure-python-tools-for-running-experiments-with-micro-manager-core/2268
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


# Custom Acquisition Engine
To execute a sequence, you must:
1. Create a `CMMCorePlus` instance (and probably load a configuration file)
2. Pass an iterable of `useq.MDAEvent` objects to the `run_mda()` method.

```python
'''
This code with execute a single event to snap an image (default action of MDAEvent)
'''
from pymmcore_plus import CMMCorePlus
from useq import MDAEvent

# Create the core instance.
mmc = CMMCorePlus.instance()  

mmc.loadSystemConfiguration()  

# Create a super-simple sequence, with one event
mda_sequence = [MDAEvent()] 

# Run it!
mmc.run_mda(mda_sequence)
```

# MDAEvent Object
The `useq.MDAEvent` object is the basic building block of an experiment. It is a relatively simple dataclass that defines a single action to be performed. Some key attributes you might want to set are:

- **exposure** (`float`): The exposure time (in milliseconds) to use for this event.
- **channel** (`str | dict[str, str]`): The configuration group to use. If a `dict`, it should have two keys: `group` and `config` (the configuration group and preset, respectively). If a `str`, it is assumed to be the name of a preset in the `Channel` group.
- **x_pos**, **y_pos**, **z_pos** (`float`): An `x`, `y`, and `z` stage position to use for this event.
- **min_start_time** (`float`): The minimum time to wait before starting this event.(in seconds, relative to the start of the experiment)

```python
snap_a_dapi = MDAEvent(channel="Preset-Channel-From-Micro-Manager", exposure=100, x_pos=1100, y_pos=1240)
```

# MDASequence Class
allows you to declare a "plan" for each axis in your experiment (channels, time, z, etc...) along with the order in which the axes should be iterated.

You can use `useq` objects rather than `dicts` for all of these fields. This has the advantage of providing type-checking and auto-completion in your IDE.

The following two sequences are equivalent:

```python
import useq

mda_sequence1 = useq.MDASequence(
    time_plan={"interval": 2, "loops": 10},
    z_plan={"range": 4, "step": 0.5},
    channels=[
        {"config": "DAPI", "exposure": 50},
        {"config": "FITC", "exposure": 80},
    ]
)

mda_sequence2 = useq.MDASequence(
    time_plan=useq.TIntervalLoops(interval=2, loops=10),
    z_plan=useq.ZRangeAround(range=4, step=0.5),
    channels=[
        useq.Channel(config="DAPI", exposure=50),
        useq.Channel(config="FITC", exposure=80),
    ]
)

assert mda_sequence1 == mda_sequence2
```

## Run MDA sequence
`MDASequence` **_is_** an [iterable](https://docs.python.org/3/glossary.html#term-iterable) of `MDAEvent`... which is exactly what we need to pass to the [`run_mda()`](https://pymmcore-plus.github.io/pymmcore-plus/api/cmmcoreplus/#pymmcore_plus.core._mmcore_plus.CMMCorePlus.run_mda) method.
```python
# Run it!
mmc.run_mda(mda_sequence)
```

# Handling Acquired Data
## Connect to `frameReady` event
```python
from pymmcore_plus import CMMCorePlus
import numpy as np
import useq

mmc = CMMCorePlus.instance()
mmc.loadSystemConfiguration()

@mmc.mda.events.frameReady.connect # connect to frameReady event
def on_frame(image: np.ndarray, event: useq.MDAEvent):
    # do what you want with the data
    print(
        f"received frame: {image.shape}, {image.dtype} "
        f"@ index {event.index}, z={event.z_pos}"
    )

mda_sequence = useq.MDASequence(
    time_plan={"interval": 0.5, "loops": 10},
    z_plan={"range": 4, "step": 0.5},
)

mmc.run_mda(mda_sequence)
```

# Hardware Triggered Sequence

Having the computer "in-the-loop" for every event in an MDA sequence can add unwanted overhead that limits performance in rapid acquisition sequences. Because of this, some devices support _hardware triggering_. This means that the computer can tell the device to queue up and start a sequence of events, and the device will take care of executing the sequence without further input from the computer.

Default acquisition engine in `pymmcore-plus` can opportunistically use hardware triggering whenever possible. For now, this behavior is off by default (in order to avoid unexpected behavior), but you can enable it by setting `CMMCorePlus.mda.engine.use_hardware_sequencing = True`:

```python
'''
Enable hardware triggering for acquisition
'''
from pymmcore_plus import CMMCorePlus

mmc = CMMCorePlus.instance()
mmc.loadSystemConfiguration()

# enable hardware triggering
mmc.mda.engine.use_hardware_sequencing = True
```

# [Event-Driven Acquisition](https://pymmcore-plus.github.io/pymmcore-plus/guides/event_driven_acquisition/)

## `Iterable[MDAEvent]`

The key thing to observe here is the signature of the `MDARunner.run()` method:

```python
from typing import Iterable
import useq

# **The `run` method expects an _iterable_ of `useq.MDAEvent` objects.** 
class MDARunner:
    def run(self, events: Iterable[useq.MDAEvent]) -> None: ...
```


> [!NOTE] Iterable
> An `Iterable` is any object that implements an `__iter__()` method that returns an iterator object. This includes sequences of known length, like `list`, `tuple`, but also many other types of objects, such as generators, `deque`, and more. Other types such as `Queue` can easily be converted to an iterator as well, as we'll see below.


```python
'''
create a generator that yields `useq.MDAEvent` objects, but simulate a "burst" of events when a certain condition is met:
'''
import random
import time
from typing import Iterator

import useq

def some_condition_is_met() -> bool:
    # Return True 20% of the time ...
    # Just an example of some probabilistic condition
    # This could be anything, the results of analysis, etc.
    return random.random() < 0.2

# generator function that yields events
def my_events() -> Iterator[useq.MDAEvent]:
    i = 0
    while True:
        if some_condition_is_met():
            # yield a burst of events
            for _ in range(5):
                yield useq.MDAEvent(metadata={'bursting': True})
        elif i > 5:
            # stop after 5 events
            # (just an example of some stop condition)
            return
        else:
            # yield a regular single event
            yield useq.MDAEvent()

        # wait a bit before yielding the next event 
        time.sleep(0.1)
        i += 1
```

To run this "experiment" using pymmcore-plus, we can pass the output of the generator to the `MDARunner.run()` method:

```python
from pymmcore_plus import CMMCorePlus

core = CMMCorePlus()
core.loadSystemConfiguration()

core.run_mda(my_events())
```

It's worth noting that the `MDASequence`class is itself an `Iterable[MDAEvent]`. It implements an `__iter__` method that yields the events in the sequence, and it can be passed directly to the `run_mda()` method. It is a _deterministic_ sequence, so it wouldn't be used on its own to implement conditional event sequences; it can, however, be used in conjunction with other iterables to implement more complex sequences.

Take this simple sequence as an example:

```python
my_sequence = useq.MDASequence(
    time_plan={'loops': 5, 'interval': 0.1},
    channels=["DAPI", "FITC"]
)
```

With a generator, we could yield the events in this sequence when the condition is met (saving us from constructing the events manually)

```python
# example usage in the
def my_events() -> Iterator[useq.MDAEvent]:
    while True:
        if some_condition_is_met():
            yield from my_sequence  # yield the events in the sequence
        else:
            ...
```

With a `Queue`, we could `put` the events in the sequence into the queue:

```python
# ... we can put events into the queue
# according to whatever logic we want:
for event in my_sequence:
    q.put(event)
```

