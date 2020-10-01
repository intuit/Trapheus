import os
from unittest import TestCase
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/export/copy_across_regions')))
import custom_exceptions
from export.copy_across_regions import copy_snapshot_to_s3_export_supportable_region_function

export_snapshot_supported_region = "eu-west-1"
mock_status = 'mock_status'
os.environ["Region"] = "us-west-2"
os.environ["ExportSnapshotSupportedRegion"] = export_snapshot_supported_region
os.environ['SNAPSHOT_COPY_EXPORT_TASK_KEY'] = "test_copy_key"
copy_db_snapshot_response = {
    'DBSnapshot': {
        'Status': mock_status,
    }
}

class TestCheckRegionSupportSnapshotExportToS3Function(TestCase):
    def setUp(self):
        self.event = create_event()


    @patch("utility.get_instance_snapshot_arn", return_value="testarn")
    @patch("export.copy_across_regions.copy_snapshot_to_s3_export_supportable_region_function.boto3.client")
    @patch("export.copy_across_regions.copy_snapshot_to_s3_export_supportable_region_function.copy_db_snapshot",
           return_value=copy_db_snapshot_response)
    def test_lambda_copy_snapshot_to_s3_export_supportable_region_boto3_client_takes_proper_region(self
                                                                                                   , mock_get_instance_snapshot_arn
                                                                                                   , mock_boto3_client
                                                                                                   , mock_copy_db_snapshot
                                                                                                   ):
        copy_snapshot_to_s3_export_supportable_region_function.lambda_copy_snapshot_to_s3_export_supportable_region(
            self.event, {})
        mock_boto3_client.assert_called_with('rds', export_snapshot_supported_region)

    @patch("utility.get_instance_snapshot_arn", return_value="testarn")
    @patch("export.copy_across_regions.copy_snapshot_to_s3_export_supportable_region_function.copy_db_snapshot",
           return_value=copy_db_snapshot_response)
    def test_lambda_copy_snapshot_to_s3_export_supportable_region_success(self, mock_copy_db_snapshot):
        result = copy_snapshot_to_s3_export_supportable_region_function. \
            lambda_copy_snapshot_to_s3_export_supportable_region(self.event, {})
        self.assertEqual(result['status'], mock_status)

    @patch("utility.get_instance_snapshot_arn", return_value="testarn")
    @patch("export.copy_across_regions.copy_snapshot_to_s3_export_supportable_region_function.copy_db_snapshot",
           return_value=copy_db_snapshot_response)
    def test_lambda_copy_snapshot_to_s3_export_supportable_region_empty_export_snapshot_supported_region(self
                                                                                                         , mock_get_instance_snapshot_arn
                                                                                                         , mock_copy_db_snapshot):
        os.environ["ExportSnapshotSupportedRegion"] = ""
        with self.assertRaises(custom_exceptions.ExportSnapshotSupportedRegionNotProvidedException) as err:
            copy_snapshot_to_s3_export_supportable_region_function. \
                lambda_copy_snapshot_to_s3_export_supportable_region(self.event, {})
            self.assertTrue("Provide the ExportSnapshotSupportedRegion parameter. Currently is" in err.exception)


def create_event():
    event = {"identifier": "database-1"}
    return event
