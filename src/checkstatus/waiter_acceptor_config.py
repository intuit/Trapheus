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