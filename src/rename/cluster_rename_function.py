import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_rename_dbcluster(event, context):
    """Handles rename of a DB cluster and its corresponding readers and writers"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    rename_response = {}
    try:
        #rename revert scenario in case of db cluster restore failure
        if event.get('Error') == 'ClusterRestoreException' and \
                'Identifier' in event.get('Cause'):
            rename_response = cluster_instance_rename_reversal(event, rds)
        else:
            rename_response = cluster_instance_rename(event, rds)
        #rename of the db cluster
        rds.modify_db_cluster(
            DBClusterIdentifier = rename_response["original_cluster_identifier"],
            ApplyImmediately = True,
            NewDBClusterIdentifier = rename_response["modified_cluster_identifier"]
        )
        result['taskname'] = constants.RENAME
        result['identifier'] = rename_response["modified_cluster_identifier"]
        return result
    except Exception as error:
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(str(error))
        else:
            raise custom_exceptions.RenameException(str(error))


def cluster_instance_rename_reversal(event, rds):
    """in case of failure at the Restore step, revert the initial rename of cluster readers and writers to unblock any activity on the db"""
    response = {}
    response = util.get_identifier_from_error(event)
    try:
        describe_response = rds.describe_db_clusters(
            DBClusterIdentifier = response["original_identifier"]
        )
        # revert the rename of the reader and writer instances before renaming the cluster
        for db_cluster_member in describe_response['DBClusters'][0]['DBClusterMembers']:
            old_dbinstance_id = db_cluster_member['DBInstanceIdentifier']
            new_dbinstance_id = util.get_modified_identifier(old_dbinstance_id)["instance_id"]
            rds.modify_db_instance(
                DBInstanceIdentifier = old_dbinstance_id,
                ApplyImmediately = True,
                NewDBInstanceIdentifier = new_dbinstance_id
            )
        response["original_cluster_identifier"] = response["original_identifier"]
        response["modified_cluster_identifier"] = response["modified_identifier"]
        return response
    except Exception as error:
        error_message = util.get_error_message(response["modified_identifier"], error)
        raise Exception(error_message)

def cluster_instance_rename(event,rds):
    """rename of the reader and writer instances in a cluster"""
    response = {}
    original_cluster_identifier = event['identifier']
    modified_cluster_identifier = event['identifier'] + constants.TEMP_POSTFIX
    try:
        describe_response = rds.describe_db_clusters(
            DBClusterIdentifier = original_cluster_identifier
        )
        #rename the reader and writer instances before renaming the cluster
        for db_cluster_member in describe_response['DBClusters'][0]['DBClusterMembers']:
            old_dbinstance_id = db_cluster_member['DBInstanceIdentifier']
            new_dbinstance_id = old_dbinstance_id + constants.TEMP_POSTFIX
            rds.modify_db_instance(
                DBInstanceIdentifier = old_dbinstance_id,
                ApplyImmediately = True,
                NewDBInstanceIdentifier = new_dbinstance_id
            )
        response["original_cluster_identifier"] = original_cluster_identifier
        response["modified_cluster_identifier"] = modified_cluster_identifier
        return response
    except Exception as error:
        error_message = util.get_error_message(modified_cluster_identifier, error)
        raise Exception(error_message)
