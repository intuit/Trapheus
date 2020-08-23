import os
import boto3
import constants
import utility as util
import DBClusterStatusWaiter

def lambda_get_cluster_status(event, context):
    """Method to obtain status of a RDS db cluster post actions such as snapshot creation, rename, restore or delete"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    taskname = event['output']['taskname']
    identifier = event['output']['identifier']
    try:
        result['task'] = eval_cluster_status(rds, context, taskname, identifier)
        if result['task'] == constants.TASK_COMPLETE and \
                taskname == constants.RENAME or taskname == constants.CLUSTER_RESTORE:
            result['task'] = eval_cluster_member_status(rds, context, identifier)
        result['identifier'] = identifier
        result['taskname'] = taskname
        result['isCluster'] = event['isCluster']
        return result
    except Exception as error:
        return util.eval_exception(error, identifier, taskname)

def eval_cluster_status(rds_client, context, taskname, identifier):
    max_attempts = util.get_waiter_max_attempts(context)
    if taskname == constants.SNAPSHOT:
        waiter = rds_client.get_waiter('db_cluster_snapshot_available')
        waiter.wait(
            DBClusterIdentifier = identifier,
            DBClusterSnapshotIdentifier = (identifier + constants.SNAPSHOT_POSTFIX),
            WaiterConfig = {
                'Delay': constants.DELAY_INTERVAL,
                'MaxAttempts': max_attempts
            }
        )
    else:
        DBClusterStatusWaiter.check_dbcluster_status(taskname, identifier, rds_client, max_attempts)
    return constants.TASK_COMPLETE


def eval_cluster_member_status(rds_client, context, identifier):
    """Method to obtain status of every member instance of an DB cluster"""
    dbcluster_description = rds_client.describe_db_clusters(
        DBClusterIdentifier=identifier
    )
    for db_cluster_member in dbcluster_description['DBClusters'][0]['DBClusterMembers']:
        waiter = rds_client.get_waiter('db_instance_available')
        waiter.wait(
            DBInstanceIdentifier = db_cluster_member['DBInstanceIdentifier'],
            WaiterConfig = {
                'Delay': constants.DELAY_INTERVAL,
                'MaxAttempts': util.get_waiter_max_attempts(context)
            }
        )
    return constants.TASK_COMPLETE
