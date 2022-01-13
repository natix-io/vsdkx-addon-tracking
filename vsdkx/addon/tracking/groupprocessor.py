from vsdkx.core.structs import AddonObject

from vsdkx.addon.tracking.processor import TrackerProcessor


class GroupTrackerProcessor(TrackerProcessor):
    """
    Track group boxes
    """
    def post_process(self, addon_object: AddonObject) -> AddonObject:
        addon_object.inference.extra["group_counter"], \
        addon_object.shared["last_updated_groups"] = \
            self._box_counter(addon_object.inference.extra["tracked_groups"])

        return addon_object
