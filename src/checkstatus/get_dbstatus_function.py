import os
import boto3
import constants
import utility as util

def lambda_get_dbinstance_status(event, context):
    """Method to obtain status of a RDS instance post actions such as snapshot creation, rename, restore or delete"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    taskname = event['output']['taskname']
    identifier = event['output']['identifier']
    snapshot_id = util.get_snapshot_id(event['output'])
    try:
        result["task"] = eval_dbinstance_status(rds, context, taskname, identifier, snapshot_id)
        result['identifier'] = identifier
        result['taskname'] = taskname
        result['snapshot_id'] = snapshot_id
        return result
    except Exception as error:
        return util.eval_exception(error, identifier, taskname)

def eval_dbinstance_status(rds_client, context, taskname, identifier, snapshot_id):
    max_attempts = util.get_waiter_max_attempts(context)
    if taskname == constants.SNAPSHOT:
        waiter = rds_client.get_waiter('db_snapshot_available')
        waiter.wait(
            DBInstanceIdentifier = identifier,
            DBSnapshotIdentifier = (snapshot_id),
            WaiterConfig = {
                'Delay': constants.DELAY_INTERVAL,
                'MaxAttempts': max_attempts
            }
        )
    else:
        waiter = rds_client.get_waiter('db_instance_available')
        if taskname == constants.DELETE:
            waiter = rds_client.get_waiter('db_instance_deleted')
        waiter.wait(
            DBInstanceIdentifier = identifier,
            WaiterConfig = {
                'Delay': constants.DELAY_INTERVAL,
                'MaxAttempts': max_attempts
            }
        )
    return constants.TASK_COMPLETE