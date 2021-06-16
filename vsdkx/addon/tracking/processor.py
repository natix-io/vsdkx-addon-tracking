import numpy as np
from vsdkx.core.interfaces import Addon
from vsdkx.core.structs import Inference
from numpy import ndarray

from vsdkx.addon.tracking.centroidtracker import CentroidTracker
from vsdkx.addon.tracking.trackableobject import TrackableObject


class TrackerProcessor(Addon):
    """
    A class for tracking multiple objects
    """

    def __init__(self, addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(addon_config, model_settings, model_config,
                         drawing_config)
        self._trackableObjects = {}
        self._trackable_obj = None
        self._ct = CentroidTracker(
            max_disappeared=addon_config['max_disappeared'],
            distance_threshold=
            addon_config['distance_threshold'])
        self._bidirectional_mode = addon_config['bidirectional_mode']
        self._bidirectional_threshold = addon_config['bidirectional_threshold']

    def post_process(self, inference: Inference) -> Inference:
        """
        Checks if input bounding boxes are new or existing objects to track

        Args:
            inference (Inference): The result of the ai

        Returns:
            event_counter (int | dict): Amount of newly tracked events, returns
            an int on unidirectional mode and a dict on a bidirectional mode
            last_updated (dict): Filtered list of trackable objects that were
            updated on the last frame

        """
        event_counter = 0
        events_in_counter = 0
        events_out_counter = 0
        # centroids of bounding boxes
        last_updated = {}

        # exit immediately if no people boxes found
        if len(inference.boxes) == 0:
            self._ct.update(inference.boxes)
            inference.extra["tracked_objects"] = event_counter
            inference.extra["trackable_object"] = last_updated
            return inference
        else:
            objects, bounding_boxes = self._ct.update(inference.boxes)

        # loop over the tracked objects
        for (object_id, centroid) in objects.items():

            self._trackable_obj = self._trackableObjects.get(object_id, None)

            if self._trackable_obj is None:
                self._trackable_obj = TrackableObject(object_id,
                                                      centroid,
                                                      bounding_boxes[
                                                          object_id])
                self._trackable_obj.trajectory_mean = centroid
                self._get_object_position(centroid, 0)
            # otherwise, there is a trackable object so we can utilize it
            # to determine the direction

            else:
                x = [c[1] for c in self._trackable_obj.centroids]
                y = [c[1] for c in self._trackable_obj.centroids]
                direction_of_position = centroid[1] - np.mean(y)

                self._trackable_obj.trajectory_mean = np.mean(x), np.mean(y)
                self._trackable_obj.centroids.append(centroid)
                self._get_current_direction()

                if not self._trackable_obj.counted:
                    self._trackable_obj.counted = True
                    if not self._bidirectional_mode:
                        event_counter += 1

                    elif self._bidirectional_mode:
                        events_in, events_out = \
                            self._get_object_position(centroid,
                                                      direction_of_position)
                        events_in_counter += events_in
                        events_out_counter += events_out
                        event_counter = {'in': events_in_counter,
                                         'out': events_out_counter}
            # store the trackable object in our dictionary
            self._trackable_obj.bounding_box = bounding_boxes[object_id]
            self._trackableObjects[object_id] = self._trackable_obj
            last_updated[object_id] = self._trackable_obj
        inference.extra["tracked_objects"] = event_counter
        inference.extra["trackable_object"] = last_updated
        return inference

    def _get_current_direction(self):
        """
        Sets the current walking direction of the trackable object.
        Supported directions are 'up', 'down'.
        """

        prev_centroids = self._trackable_obj.centroids[-2]
        current_centroids = self._trackable_obj.centroids[-1]

        if prev_centroids[1] < current_centroids[1]:
            self._trackable_obj.direction = 'down'
        elif prev_centroids[1] > current_centroids[1]:
            self._trackable_obj.direction = 'up'

    def _get_object_position(self, centroid, direction):
        """
        Determines the position of an object. The current state of the
        implementation supports two directions:
        1. walking downwards and object has crossed the threshold line = 'in'
        2. walking upwards and object has crossed the threshold line = 'out'

        Args:
            centroid (tuple): Centroid tuple
            direction (float): Float indicating the object's direction
        """
        event_counter_in = 0
        event_counter_out = 0

        # Define the direction towards that a person is walking to & update
        # it on the obj instance
        # todo handle directions in a dynamic way
        if direction >= 0 and \
                centroid[1] > self._bidirectional_threshold:
            self._trackable_obj.position = 'in'
            event_counter_in = + 1

        elif direction <= 0 and \
                centroid[1] < self._bidirectional_threshold:
            self._trackable_obj.position = 'out'
            event_counter_out = + 1

        # If the new direction of the object is different to its
        # previous direction update the people counter camera
        if self._trackable_obj.position != self._trackable_obj.prev_position:
            self._trackable_obj.prev_position = self._trackable_obj.position

        return event_counter_in, event_counter_out
