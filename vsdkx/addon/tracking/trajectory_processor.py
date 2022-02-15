import numpy as np

from vsdkx.core.interfaces import Addon
from vsdkx.core.structs import AddonObject


class TrajectoryProcessor(Addon):
    """
    Calculate movement direction for objects based on their past and present
    coordinates on the frame

    Attributes:
        centroid_index (int): nth old position of object to compare present
        position for direction.
        temporal_length (int): The amount of centroid points to compare against
        the present centroid position.
    """
    def __init__(self, addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(
            addon_config, model_settings, model_config, drawing_config)
        self.centroid_index = addon_config.get('centroid_index', 3)
        self.temporal_length = addon_config.get('temporal_length', 10)

    def post_process(self, addon_object: AddonObject) -> AddonObject:
        """
        Calculate movement directions and write them information in
        extra dict under 'movement_directions' key.
        """
        self._get_current_direction(
            addon_object.shared.get("trackable_objects", {})
        )
        self._construct_trajectory_dict(addon_object)

        return addon_object

    def _construct_trajectory_dict(self, addon_object: AddonObject):
        """
        write dictionary mapping object id mappings to movement directions to
        extra dict.

        Args:
            addon_object(AddonObject): Addon object containing
            'trackable_objects' key set in shared attribute.
        """
        addon_object.inference.extra['movement_directions'] = {
            object_id: tracked_object.direction
            for object_id, tracked_object
            in addon_object.shared.get("trackable_objects", {}).items()
        }

    def _get_current_direction(self, tracked_objects: dict):
        """
        Sets the current movement direction of the trackable object.
        Supported directions are 'up', 'down', 'left', 'right',
        'downleft', 'downright', 'upleft', 'upright' or '' if direction can't
        be set.
        """

        for _, tracked_object in tracked_objects.items():

            # Compare the position of the last centroid to the average position
            # of the last n centroids (where n = temporal length).
            # When the trajectory has recorded less points than the defined
            # temporal length, we consider the average of all recorded points

            starting_centroid_index = min(len(tracked_object.centroids),
                                          self.centroid_index)
            tracked_object_len = len(tracked_object.centroids)
            temporal_len = self.temporal_length \
                if tracked_object_len == self.temporal_length \
                else tracked_object_len

            prev_centroids = np.mean(
                tracked_object.centroids[(tracked_object_len - temporal_len):-1],
                axis=0
            )\
                if tracked_object_len > 1 else \
                tracked_object.centroids[-starting_centroid_index]
            current_centroids = tracked_object.centroids[-1]

            tracked_object.direction = ''

            if prev_centroids[1] < current_centroids[1]:
                tracked_object.direction += 'down'
            elif prev_centroids[1] > current_centroids[1]:
                tracked_object.direction += 'up'

            if prev_centroids[0] < current_centroids[0]:
                tracked_object.direction += 'left'
            elif prev_centroids[0] > current_centroids[0]:
                tracked_object.direction += 'right'
