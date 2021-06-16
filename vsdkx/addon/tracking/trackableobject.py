class TrackableObject:
    """
    A class for trackable object containing relevant information

    Attributes:
        object_id (int): ID of object
        centroids (tuple): Tuple with x,y centroid values
        counted (bool): Flag for if object was counted
        direction (string): Direction of object
        position (string): Position of object
        prev_position (string): Position of object from previous frame
        bounding_box (array): Bounding box array
    """

    def __init__(self, object_id, centroid, bounding_box):
        """
        Args:
            object_id (int): ID of the object
            centroid (tuple): X,Y coordinates of the object centroid
        """
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.object_id = object_id
        self.centroids = [centroid]
        self.bounding_box = bounding_box
        # indicates whether object has been counted or not
        self.counted = False
        self.direction = ''
        self.position = ''
        self.prev_position = ''
        self.trajectory_mean = ''

    def __repr__(self) -> str:
        return f"{{'object_id': {self.object_id}}}"
