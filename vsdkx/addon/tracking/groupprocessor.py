from vsdkx.core.structs import AddonObject

from vsdkx.addon.tracking.processor import TrackerProcessor


class GroupTrackerProcessor(TrackerProcessor):
    def post_process(self, addon_object: AddonObject) -> AddonObject:
        addon_object.inference.extra["tracked_groups"], \
        addon_object.shared["trackable_groups"] = \
            self._box_counter(addon_object.inference.extra["groups"])

        return addon_object
