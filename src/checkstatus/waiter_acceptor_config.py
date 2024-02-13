DB_CLUSTER_AVAILABLE = [
    {
        "expected": "available",
        "matcher": "pathAll",
        "state": "success",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "deleted",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "deleting",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "failed",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "inaccessible-encryption-credentials",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "stopped",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    }
]

DB_CLUSTER_DELETED = [
    {
        "expected": True,
        "matcher": "path",
        "state": "success",
        "argument": "length(DBClusters) == `0`"
    },
    {
        "expected": "DBClusterNotFound",
        "matcher": "error",
        "state": "success"
    },
    {
        "expected": "creating",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "modifying",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "rebooting",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    },
    {
        "expected": "resetting-master-credentials",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "DBClusters[].Status"
    }
]

SSM_AUTOMATION_EXECUTION_COMPLETED = [
    {
        "expected": "Success",
        "matcher": "pathAll",
        "state": "success",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "CompletedWithSuccess",
        "matcher": "pathAll",
        "state": "success",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "TimedOut",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "Cancelling",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "Cancelled",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "Failed",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    },
    {
        "expected": "CompletedWithFailure",
        "matcher": "pathAny",
        "state": "failure",
        "argument": "AutomationExecutionMetadataList[].AutomationExecutionStatus"
    }
]