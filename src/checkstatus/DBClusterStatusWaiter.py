import botocore
import constants
import waiter_acceptor_config

def check_dbcluster_status(taskname, identifier, rds, maxAttempts):
    acceptor_config = waiter_acceptor_config.DB_CLUSTER_AVAILABLE
    if taskname == constants.DELETE:
        acceptor_config = waiter_acceptor_config.DB_CLUSTER_DELETED

    model = botocore.waiter.WaiterModel({
        "version": 2,
        "waiters": {
            "DBClusterStatus": {
                "delay": constants.DELAY_INTERVAL,
                "operation": "DescribeDBClusters",
                "maxAttempts": maxAttempts,
                "acceptors": acceptor_config
            }
        }
    })
    waiter = botocore.waiter.create_waiter_with_client('DBClusterStatus', model, rds)
    try:
        waiter.wait(DBClusterIdentifier = identifier)
    except botocore.exceptions.WaiterError as e:
        raise Exception(e)
