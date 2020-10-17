import custom_exceptions

DELAY_INTERVAL = 40
DIVISOR = 1000
IDENTIFIER = "Identifier:"
SNAPSHOT_POSTFIX = "-snapshot"
TEMP_POSTFIX = "-temp"
EXPORT_TASK_POSTFIX = "-export-task"
RDS_SNAPSHOTS_BUCKET_NAME_PREFIX = "rds-snapshots-"

DELETE = "Delete"
RENAME = "Rename"
SNAPSHOT = "SnapshotCreation"
DB_RESTORE = "Restore"
CLUSTER_RESTORE = "ClusterRestore"
ERROR = "Error"
CAUSE = "Cause"
EXPORT_SNAPSHOT = "SnapshotExport"
EXPORT_SNAPSHOT_SUPPORT = "SnapshotExportSupported"
COPY_SNAPSHOT = "SnapshotCopy"

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
EXPORT_SNAPSHOT_TO_S3_IN_REGION_THAT_SUPPORTS_SNAPSHOT_EXPORT_TO_S3 = "Case of exporting snapshot to s3 in a region " \
                                                                      "that supports snapshot export to s3."
REGION_SUPPORTS_SNAPSHOT_EXPORT_TO_S3 = "region_supports_snapshot_export_to_s3"
INVALID_PARAMETER_COMBINATION_ERROR_MESSAGE = "InvalidParameterCombination) when calling the DescribeExportTasks " \
                                              "operation: This operation is not currently supported."

TASK_FAILED = "TASK_FAILED"
TASK_COMPLETE = "TASK_COMPLETE"


