# ObjectTracking

This project utilized a centroid based object tracker `class TrackerProcessor` in `tracker/processor.py`. The tracker's full workflow is described through the `Tracker._box_counter` method, that is executed in every frame as a `post_process` step, and which receives an array of bounding boxes as input (with all detected objects in the current frame).

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

### Debug
Object initialization and `post_process` example:

```python
from vsdkx.addon.tracking.processor import TrackerProcessor
from vsdkx.core.interfaces import Addon, AddonObject

add_on_config = {
    'bidirectional_mode': False,
    'bidirectional_threshold': 150,
    'distance_threshold': 500,
    'max_disappeared': 50,
    'class': 'vsdkx.addon.tracking.processor.TrackerProcessor',
    'min_appearance': 1
    }

model_config = {
    'classes_len': 1, 
    'filter_class_ids': [0], 
    'input_shape': [640, 640], 
    'model_path': 'vsdkx/weights/ppl_detection_retrain_training_2.pt'
    }
    
model_settings = {
    'conf_thresh': 0.5, 
    'device': 'cpu', 
    'iou_thresh': 0.4
    }  
  
tracker = TrackerProcessor(addon_on_config, model_settings, model_config)

addon_object = AddonObject(
    frame=np.array(RGB image), 
    inference=Inference(
        boxes=[array([2007,  608, 3322, 2140]), array([ 348,  348, 2190, 2145])], 
        classes=[array([0], dtype=object), array([0], dtype=object)], 
        scores=[array([0.799637496471405], dtype=object), array([0.6711544394493103], dtype=object)], 
        extra={}
        ), 
    shared={}
    )
addon_object = tracker.post_process(addon_object)
```

The resulted `addon_object` after the `post_process` step is executed is: 

```python
AddonObject(
    frame=np.arra(RGB image), 
    inference=Inference(
        boxes=[array([2007,  608, 3322, 2140]), array([ 348,  348, 2190, 2145])], 
        classes=[array([0], dtype=object), array([0], dtype=object)], 
        scores=[array([0.799637496471405], dtype=object), array([0.6711544394493103], dtype=object)],
        extra={'tracked_objects': 0}
        ), 
    shared={
        'trackable_objects': {}, 
        'trackable_objects_history': {
            0: {'object_id': 0}, 
            1: {'object_id': 1}
            }
    }
    )
```
