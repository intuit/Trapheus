import os
import boto3
import constants
import utility as util
import custom_exceptions
import SSMAutomationExecutionStatusWaiter

def lambda_get_automation_execution_status(event, context):
    """Method to obtain status of a SSM automation execution"""
    region = os.environ['Region']
    ssm = boto3.client('ssm', region)
    result = {}
    execution_id = event['output']['automation_execution_id']
    try:
        max_attempts = util.get_waiter_max_attempts(context)
        SSMAutomationExecutionStatusWaiter.check_automation_execution_status(execution_id, max_attempts, ssm)
        result['task'] = constants.TASK_COMPLETE
        result['taskname'] = event['output']['taskname']
        return result
    except Exception as error:
        raise custom_exceptions.SSMAutomationExecutionException(error)