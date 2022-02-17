import numpy as np

from vsdkx.core.interfaces import Addon
from vsdkx.core.structs import AddonObject


class SpeedEstimationProcessor(Addon):
    """
    Calculate movement direction for objects based on their past and present
    coordinates on the frame. This algorithm is based on the methodology
    proposed on the following paper:

    https://ieeexplore.ieee.org/document/6614066

    Attributes:
        person_action: (boolean) Flag on estimating actions such as
            standing | walking | running
        camera_length: (int|float) Distance from camera to furthest
            object/ landmark in meters
        fps: (int) Input frame rate
        lens_dimension: (int) Camera lens dimension in millimeters. Optional
            value if 'camera_horizontal_degrees' and
            'camera_vertical_degrees' are specified instead.
        focal_length: (int) Camera's focal length in millimeters. Optional
            value if 'camera_horizontal_degrees' and
            'camera_vertical_degrees' are specified instead.
        camera_horizontal_degrees: (int) Camera's horizontal view in degrees.
            Optional value if 'lens_dimension' and 'focal_length'
            are specified instead.
        camera_vertical_degrees: (int) Camera's vertical view in degrees.
            Optional value if 'lens_dimension' and 'focal_length'
            are specified instead.
        _walking_action: (string) Constant string for walking action
        _running_action: (string) Constant string for running action
        _standing_action: (string) Constant string for standing action
        _kph: (float) Constant for kilometers per hour (kph)
        _average_running_kph: (float) Constant for average running speed in kph
        _average_walking_kph: (float) Constant for average walking speed in kph
    """

    def __init__(self, addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(
            addon_config, model_settings, model_config, drawing_config)
        self.person_action = addon_config.get('person_action', True)
        self.camera_length = addon_config.get('camera_length', 4.5)  # meter
        self.fps = addon_config.get('fps', 30)
        self.lens_dimension = addon_config.get('lens_dimension', 2000)  # mm
        self.focal_length = addon_config.get('focal_length', 4000)
        self.camera_horizontal_degrees = \
            addon_config.get('camera_horizontal_degrees', 0)
        self.camera_vertical_degrees = \
            addon_config.get('camera_vertical_degrees', 0)

        self._walking_action = 'walking'
        self._standing_action = 'standing'
        self._running_action = 'running'

        self._kph = 3.6
        self._average_running_kph = 8.4
        self._average_walking_kph = 5.04 / self.fps

    def post_process(self, addon_object: AddonObject) -> AddonObject:
        """
        Estimates the object's speed and action (for people) and write them
        information in the extra dict under the 'current_speed' and
        'current_action' keys.
        """

        frame_height, frame_width, _ = addon_object.frame.shape
        self._get_object_speed(
            addon_object.shared.get("trackable_objects", {}),
            frame_height,
            frame_width
        )
        self._construct_result_dict(addon_object)

        return addon_object

    def _construct_result_dict(self, addon_object: AddonObject):
        """
        Constructs two dictionaries (conditional) to map the object id to its
        estimated speed and action. The dictionaries are included in the
        inference.extra dict of the addon_object.

        Args:
            addon_object(AddonObject): Addon object containing
            'trackable_objects' key set in shared attribute.
        """
        addon_object.inference.extra['current_speed'] = {
            object_id: tracked_object.current_speed
            for object_id, tracked_object
            in addon_object.shared.get("trackable_objects", {}).items()
        }

        if self.person_action:
            addon_object.inference.extra['current_action'] = {
                object_id: tracked_object.action
                for object_id, tracked_object
                in addon_object.shared.get("trackable_objects", {}).items()
            }

    def _get_movement_action(self, speed: float):
        """
        Assigns the current action of the object based on its speed. The
        actions in question are 'walking | standing | running|' and are
        applicable to people detections.

        Args:
            speed: (float) Estimated speed of tracked object

        Returns:
            action: (string) walking | standing | running|
        """

        if speed >= self._average_running_kph:
            action = self._running_action
        elif speed >= self._average_walking_kph:
            action = self._walking_action
        else:
            action = self._standing_action

        return action

    def _get_object_speed(self,
                          tracked_objects: dict,
                          frame_width: int,
                          frame_height: int):
        """
        Estimates the moving speed of a detected and tracked object.

        Args:
            tracked_objects: (dict) Tracked objects by the object tracker in the
                current frame
            frame_width: (int) The width of the input frame
            frame_height: (int) The height of the input frame
        """

        for _, tracked_object in tracked_objects.items():

            if len(tracked_object.centroids) > 1:
                past_centroid = tracked_object.centroids[-2]
                current_centroid = tracked_object.centroids[-1]

                if self.camera_horizontal_degrees == 0:
                    a_x = 2 * np.arctan(self.lens_dimension /
                                        (2 * self.focal_length))
                else:
                    a_x = self.camera_horizontal_degrees

                if self.camera_vertical_degrees == 0:
                    a_y = 2 * np.arctan(self.lens_dimension /
                                        (2 * self.focal_length))
                else:
                    a_y = self.camera_vertical_degrees

                x_real = 2 * self.camera_length * np.tan(np.degrees(a_x))
                y_real = 2 * self.camera_length * np.tan(np.degrees(a_y))

                v_x = (x_real / frame_width) * (
                        (current_centroid[0] - past_centroid[0]) /
                        (1 / self.fps))

                v_y = (y_real / frame_height) * (
                        (current_centroid[1] - past_centroid[1]) /
                        (1 / self.fps))

                v = np.sqrt((np.power(v_x, 2) + np.power(v_y, 2))) * self._kph

                tracked_object.speeds.append(v)

                # Get average over the frames of the past second

                if len(tracked_object.speeds) > self.fps:
                    tracked_object.current_speed = sum(tracked_object.speeds[
                                                       (len(
                                                           tracked_object.speeds)
                                                        - self.fps - 1):-1]) \
                                                   / self.fps
                else:
                    tracked_object.current_speed = sum(
                        tracked_object.speeds) / len(
                        tracked_object.speeds)

                if self.person_action:
                    tracked_object.action = \
                        self._get_movement_action(tracked_object.current_speed)
            else:
                tracked_object.speeds.append(0)
                continue
