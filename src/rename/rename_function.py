import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_rename_dbinstance(event, context):
    """Handles rename of a DB instance"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    original_instance_identifier = ''
    try:
        if event.get('Error') == 'RestoreException' and \
                'Identifier' in event.get('Cause'):
            #rename revert scenario in case of db restore failure
            response = util.get_identifier_from_error(event)
            modified_instance_identifier = response["modified_identifier"]
            original_instance_identifier = response["original_identifier"]
            snapshot_id = util.get_snapshot_id(response, original_instance_identifier)

        else:
            original_instance_identifier = event['identifier']
            modified_instance_identifier = event['identifier'] + '-temp'
            snapshot_id = util.get_snapshot_id(event)

        rds.modify_db_instance(
            DBInstanceIdentifier = original_instance_identifier,
            ApplyImmediately = True,
            NewDBInstanceIdentifier = modified_instance_identifier)

        result['taskname'] = constants.RENAME
        result['identifier'] = modified_instance_identifier
        result['snapshot_id'] = snapshot_id
        return result

    except Exception as error:
        error_message = util.get_error_message(original_instance_identifier, error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.RenameException(error_message)
