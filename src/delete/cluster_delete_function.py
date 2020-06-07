import os
import boto3
import constants
import custom_exceptions

def lambda_delete_dbcluster(event, context):
    """Handles deletion of a DB cluster and its corresponding readers and writers"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    cluster_id = event['identifier'] + constants.TEMP_POSTFIX
    try:
        describe_db_response = rds.describe_db_clusters(
            DBClusterIdentifier = cluster_id
        )
        for db_cluster_member in describe_db_response['DBClusters'][0]['DBClusterMembers']:
            rds.delete_db_instance(
                DBInstanceIdentifier = db_cluster_member['DBInstanceIdentifier'],
                SkipFinalSnapshot = True
            )
        rds.delete_db_cluster(
            DBClusterIdentifier = cluster_id,
            SkipFinalSnapshot = True
        )
        result['taskname'] = constants.DELETE
        result['identifier'] = cluster_id
        return result
    except Exception as error:
        error_message = util.get_error_message(cluster_id, error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.DeletionException(error_message)
