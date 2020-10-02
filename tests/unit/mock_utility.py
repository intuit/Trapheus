import math
import mock_constants as constants
import mock_custom_exceptions as custom_exceptions

def eval_exception(error, identifier, taskname):
    result = {}
    error_message = constants.IDENTIFIER + identifier + ' \n' + str(error)
    if taskname == constants.DELETE and \
            (str(error) == constants.CLUSTER_UNAVAILABLE or
             constants.CLUSTER_NOT_FOUND in str(error) or constants.NOT_FOUND in str(error)):
        result['task'] = constants.TASK_COMPLETE
        result['identifier'] = identifier
        result['taskname'] = taskname
        return result
    elif str(error) == constants.INSTANCE_UNAVAILABLE or constants.INSTANCE_NOT_FOUND in str(error) \
            or str(error) == constants.CLUSTER_UNAVAILABLE or constants.CLUSTER_NOT_FOUND in str(error) \
            or constants.NOT_FOUND in str(error):
        raise custom_exceptions.InstanceUnavailableException(error_message)
    elif constants.RATE_EXCEEDED in str(error) or constants.WAITER_MAX in str(error):
        raise custom_exceptions.RateExceededException(error_message)
    elif constants.WAITER_FAILURE in str(error):
        result['task'] = constants.TASK_FAILED
        result['status'] = error_message
        result['identifier'] = identifier
        result['taskname'] = taskname
        return result
    elif taskname in constants.TASK_ERROR_MAP:
        raise constants.TASK_ERROR_MAP[taskname](error_message)
    else:
        raise Exception(error_message)

def get_identifier_from_error(event):
    response = {}
    start_index = event.get('Cause').find(constants.IDENTIFIER) + len(constants.IDENTIFIER)
    end_index = start_index + (event.get('Cause')[start_index:]).find(" ")
    response["modified_identifier"] = event.get('Cause')[(start_index):(end_index)]
    response["original_identifier"] = response["modified_identifier"] + constants.TEMP_POSTFIX
    return response

def get_modified_identifier(identifier):
    response = {}
    db_instance_id = get_modified_value(identifier)
    db_snapshot_id = db_instance_id + constants.SNAPSHOT_POSTFIX
    response["instance_id"] = db_instance_id
    response["snapshot_id"] = db_snapshot_id
    return response

def get_modified_response(event):
    response = {}
    identifier = event['identifier']
    db_instance_id = get_modified_value(identifier)
    response["instance_id"] = db_instance_id
    response["snapshot_id"] = get_modified_value(get_snapshot_id(event))
    return response

def get_modified_value(value):
    temp_substr = value.rfind(constants.TEMP_POSTFIX)
    modified_value = value[0:temp_substr] \
        if temp_substr > 0 \
        else value
    return modified_value

def eval_snapshot_exception(error, identifier, rds_client,snapshot_id=None):
    error_message = constants.IDENTIFIER + identifier + ' \n' + str(error)
    if snapshot_id is None:
        snapshot_id = identifier + constants.SNAPSHOT_POSTFIX
    if constants.RATE_EXCEEDED in str(error):
        raise custom_exceptions.RateExceededException(error_message)
    elif constants.CLUSTER_SNAPSHOT_EXISTS in str(error):
        waiter = rds_client.get_waiter('db_cluster_snapshot_deleted')
        rds_client.delete_db_cluster_snapshot(
            DBClusterSnapshotIdentifier = snapshot_id
        )
        waiter.wait(DBClusterSnapshotIdentifier = snapshot_id)
        raise custom_exceptions.RetryClusterSnapshotException(error_message)
    elif constants.DB_SNAPSHOT_EXISTS in str(error):
        waiter = rds_client.get_waiter('db_snapshot_deleted')
        rds_client.delete_db_snapshot(
            DBSnapshotIdentifier = snapshot_id
        )
        waiter.wait(DBSnapshotIdentifier = snapshot_id)
        raise custom_exceptions.RetryDBSnapshotException(error_message)
    else:
        raise custom_exceptions.SnapshotCreationException(error_message)

def eval_snapshot_exception_with_snapshot_id(error, identifier, rds_client, snapshot_id):
    eval_snapshot_exception(error, identifier, rds_client, snapshot_id)

def get_waiter_max_attempts(context):
    # converting remaining time from milliseconds to seconds
    remaining_time = context.get_remaining_time_in_millis() / constants.DIVISOR
    # calculating max attempts for waiter task
    max_attempts = math.floor(abs(remaining_time - constants.DELAY_INTERVAL) / constants.DELAY_INTERVAL)
    return max_attempts

def get_error_message(identifier, error):
    error_message = constants.IDENTIFIER + identifier + ' \n' + str(error)
    return error_message

def get_aws_account_id():
    return 1231231234

def get_snapshot_id(event, instance_id=None):
    if instance_id is None:
        instance_id = event['identifier']
    if "snapshot_id" not in event:
        return instance_id + constants.SNAPSHOT_POSTFIX
    snapshot_id = event['snapshot_id']
    return snapshot_id