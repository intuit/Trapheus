import os
import boto3
import constants
import custom_exceptions

def lambda_delete_dbinstance(event, context):
    """Handles deletion of a RDS db instance"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier'] + constants.TEMP_POSTFIX
    try:
        rds.delete_db_instance(
            DBInstanceIdentifier = instance_id,
            SkipFinalSnapshot = True
        )
        result['taskname'] = constants.DELETE
        result['identifier'] = instance_id
        return result
    except Exception as error:
        error_message = constants.IDENTIFIER + instance_id + ' \n' + str(error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.DeletionException(error_message)
