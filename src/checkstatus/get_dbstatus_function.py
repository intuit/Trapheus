import os
import boto3
import constants
import utility as util
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_get_dbinstance_status(event, context):
    """Method to obtain status of a RDS instance post actions such as snapshot creation, rename, restore or delete"""
    logger.info('## starting function execution ...')
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    taskname = event['output']['taskname']
    identifier = event['output']['identifier']
    try:
        result["task"] = eval_dbinstance_status(rds, context, taskname, identifier)
        result['identifier'] = identifier
        result['taskname'] = taskname
        logger.info('## FUNCTION RESULT')
        logger.info(result)
        logger.info('## ending function execution')
        return result
    except Exception as error:
        return util.eval_exception(error, identifier, taskname)

def eval_dbinstance_status(rds_client, context, taskname, identifier):
    logger.info('## starting eval_dbinstance_status() function execution ...')
    max_attempts = util.get_waiter_max_attempts(context)
    if taskname == constants.SNAPSHOT:
        waiter = rds_client.get_waiter('db_snapshot_available')
        waiter.wait(
            DBInstanceIdentifier = identifier,
            DBSnapshotIdentifier = (identifier + constants.SNAPSHOT_POSTFIX),
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
    logger.info('## ending eval_dbinstance_status() function execution')
    return constants.TASK_COMPLETE
    