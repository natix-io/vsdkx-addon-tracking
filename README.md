# ObjectTracking

This project utilized a centroid based object tracker `class TrackerProcessor` in `tracker/processor.py`. The tracker's full workflow is described through the `Tracker._box_counter` method, that is executed in every frame, and which receives an array of bounding boxes as input (with all detected objects in the current frame).

### Tracker._box_counter Workflow steps

1. `CentroidTracker.update`: Updates the tracked objects and their centroids with the new box samples, by calculating the euclidean distance between the previous and new samples. It finally determines if previous samples have disappeared (gone for `x` amount of frames where `x` = `max_disappeared`) and determines whether the new samples correspond to any of the same trackable objects from the previous frames. 
2. Looping over all trackable objects and filters out all new objects, and counts them based on two modes:
    1. `directional`: all objects in the frame are moving in the same direction
    2. `bidirectional`: objects in the frame move in two different directions
 Finally, `Tracker.track_object` returns either an integer with the count of the directional objects, or a dictionary with the count of tracked objects in two directions
 
### Addon Config

The following parameters are required in the addon cofig:

```yaml
max_disappeared: 10, # Maximum amount of frames from marking an object as 'disappeared'
distance_threshold: 540, # Maximum distance threshold between two objects
bidirectional_mode: False, # Flag for turning on/off the bidirectional mode
bidirectional_threshold: 150, # Threshold for bidirectional mode (required when bidirectional_mode is True)
```

Initialization example:

```python
from objecttracking.tracker import Tracker
config = {
    'max_disappeared': 10,
    'distance_threshold': 400,
    'bidirectional_mode': True,
    'bidirectional_threshold': 150,
    'debug_mode': True,
    'min_appearance': 40 # min number of appearence for an object to calculate mean of Y coord

}
tracker = Tracker(config=config)
```
