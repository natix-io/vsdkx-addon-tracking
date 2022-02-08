from vsdkx.core.interfaces import Addon
from vsdkx.core.structs import AddonObject


class TrajectoryProcessor(Addon):
    def __init__(self, addon_config: dict, model_settings: dict,
                 model_config: dict, drawing_config: dict):
        super().__init__(
            addon_config, model_settings, model_config, drawing_config)

    def post_process(self, addon_object: AddonObject) -> AddonObject:
        self._get_current_direction(
            addon_object.shared.get("trackable_object", {})
        )
        self._construct_trajectory_dict(addon_object)

        return addon_object

    def _construct_trajectory_dict(self, addon_object: AddonObject):
        addon_object.inference.extra['movement_directions'] = {
            object_id: tracked_object.direction
            for object_id, tracked_object
            in addon_object.shared.get("trackable_object", {})
        }

    def _get_current_direction(self, tracked_objects: dict):
        """
        Sets the current movement direction of the trackable object.
        Supported directions are 'up', 'down', 'left', 'right',
        'downleft', 'downright', 'upleft', 'upright'.
        """

        for _, tracked_object in tracked_objects:

            prev_centroids = tracked_object.centroids[-2]
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
