import os
from unittest import TestCase
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/export/copy_across_regions')))
import constants
from export.copy_across_regions import check_region_support_snapshot_export_to_s3_function

os.environ["Region"] = "us-west-2"
os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"


class TestCheckRegionSupportSnapshotExportToS3Function(TestCase):

    def setUp(self):
        self.event = create_event()

    @patch("utility.supports_snapshot_export_region", return_value=True)
    def test_lambda_check_region_support_snapshot_export_to_s3_supports(self, mock_supports_snapshot_export_region):
        result = check_region_support_snapshot_export_to_s3_function.lambda_check_region_support_snapshot_export_to_s3(
            self.event, {})
        self.assertEqual(result['taskname'], constants.EXPORT_SNAPSHOT_SUPPORT)

    @patch("utility.supports_snapshot_export_region", return_value=False)
    @patch("utility.get_instance_snapshot_arn", return_value="testarn")
    def test_lambda_check_region_support_snapshot_export_to_s3_snapshot_present_in_export_supporting_region(self,
                                                                                                            mock_supports_snapshot_export_region,
                                                                                                            mock_get_instance_snapshot_arn):
        result = check_region_support_snapshot_export_to_s3_function.lambda_check_region_support_snapshot_export_to_s3(
            self.event, {})
        self.assertEqual(result['taskname'], constants.EXPORT_FROM_REGION_THAT_SUPPORTS_SNAPSHOT_EXPORT_TO_S3)

    @patch("utility.supports_snapshot_export_region", return_value=False)
    @patch("utility.get_instance_snapshot_arn", return_value="")
    def test_lambda_check_region_support_snapshot_export_to_s3_copy_snapshot(self,
                                                                             mock_supports_snapshot_export_region,
                                                                             mock_get_instance_snapshot_arn):
        result = check_region_support_snapshot_export_to_s3_function.lambda_check_region_support_snapshot_export_to_s3(
            self.event, {})
        self.assertEqual(result['taskname'], constants.COPY_SNAPSHOT)


def create_event():
    event = {"identifier": "database-1", "task": "task"}
    return event
