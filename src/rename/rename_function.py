import os
import boto3
import constants
import custom_exceptions
import utility as util
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_rename_dbinstance(event, context):
    """Handles rename of a DB instance"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    original_instance_identifier = ''
    modified_instance_identifier = ''
    try:
        if event.get('Error') == 'RestoreException' and \
                'Identifier' in event.get('Cause'):
            #rename revert scenario in case of db restore failure
            response = util.get_identifier_from_error(event)
            logger.info("function get_identifier_from_error execution result: {}".format(response))
            modified_instance_identifier = response["modified_identifier"]
            original_instance_identifier = response["original_identifier"]

        else:
            original_instance_identifier = event['identifier']
            modified_instance_identifier = event['identifier'] + '-temp'

        rds.modify_db_instance(
            DBInstanceIdentifier = original_instance_identifier,
            ApplyImmediately = True,
            NewDBInstanceIdentifier = modified_instance_identifier)

        result['taskname'] = constants.RENAME
        result['identifier'] = modified_instance_identifier
        logger.info("function lambda_rename_dbinstance execution result: {}".format(result))
        return result

    except Exception as error:
        error_message = util.get_error_message(original_instance_identifier, error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.RenameException(error_message)
