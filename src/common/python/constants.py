import custom_exceptions

DELAY_INTERVAL = 40
DIVISOR = 1000
IDENTIFIER = "Identifier:"
SNAPSHOT_POSTFIX = "-snapshot"
TEMP_POSTFIX = "-temp"
EXPORT_TASK_POSTFIX = "-export-task"
RDS_SNAPSHOTS_BUCKET_NAME = "rds-snapshots"

DELETE = "Delete"
RENAME = "Rename"
SNAPSHOT = "SnapshotCreation"
DB_RESTORE = "Restore"
CLUSTER_RESTORE = "ClusterRestore"
EXPORT_SNAPSHOT = "SnapshotExportTask"

TASK_ERROR_MAP = {
    'Rename' : custom_exceptions.RenameException,
    'Restore' : custom_exceptions.InstanceRestoreException,
    'ClusterRestore': custom_exceptions.ClusterRestoreException,
    'Delete': custom_exceptions.DeletionException,
    'SnapshotCreation': custom_exceptions.SnapshotCreationException
}

CLUSTER_UNAVAILABLE = "cluster_not_available"
CLUSTER_NOT_FOUND = "DBClusterNotFoundFault"
INSTANCE_UNAVAILABLE = "instance_not_available"
INSTANCE_NOT_FOUND = "DBInstanceNotFound"
NOT_FOUND = "not found"
DB_SNAPSHOT_EXISTS = "DBSnapshotAlreadyExists"
CLUSTER_SNAPSHOT_EXISTS = "DBClusterSnapshotAlreadyExistsFault"
WAITER_FAILURE = "Waiter encountered a terminal failure state"
RATE_EXCEEDED = "Rate exceeded"
WAITER_MAX = "Max attempts exceeded"

TASK_FAILED = "TASK_FAILED"
TASK_COMPLETE = "TASK_COMPLETE"


