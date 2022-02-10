from vsdkx.core.interfaces import Addon
from vsdkx.core.structs import AddonObject


class TrajectoryProcessor(Addon):
    def __init__(self, addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(
            addon_config, model_settings, model_config, drawing_config)
        self.centroid_mean = addon_config.get('centroid_mean', 3)

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
            in addon_object.shared.get("trackable_objects", {})
        }

    def _get_current_direction(self, tracked_objects: dict):
        """
        Sets the current movement direction of the trackable object.
        Supported directions are 'up', 'down', 'left', 'right',
        'downleft', 'downright', 'upleft', 'upright' or '' if direction can't
        be set.
        """

        for _, tracked_object in tracked_objects.items():

            starting_centroid_index = min(len(tracked_object.centroids),
                                          self.centroid_mean)

            prev_centroids = tracked_object.centroids[-starting_centroid_index]
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
