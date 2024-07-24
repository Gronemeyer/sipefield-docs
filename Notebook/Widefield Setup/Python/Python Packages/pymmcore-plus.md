---
github: https://github.com/pymmcore-plus
---
![mm diagram](https://user-images.githubusercontent.com/1609449/202301602-00ba0fd8-df4f-4993-b0ad-8e3d1cefaf42.png)

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

