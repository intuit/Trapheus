class RateExceededException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class InstanceUnavailableException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class InstanceRestoreException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class ClusterRestoreException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class RenameException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class DeletionException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class SnapshotCreationException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class RetryDBSnapshotException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class RetryClusterSnapshotException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

