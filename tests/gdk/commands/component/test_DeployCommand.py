import unittest
from unittest.mock import MagicMock, patch

from gdk.commands.component.DeployCommand import DeployCommand


class DeployCommandTest(unittest.TestCase):
    @patch("gdk.commands.component.DeployCommand.ComponentDeployConfiguration")
    @patch("gdk.commands.component.DeployCommand.Greengrassv2Client")
    def setUp(self, mock_gg_client, mock_config):
        self.mock_config = mock_config.return_value
        self.mock_config.component_name = "test-component"
        self.mock_config.component_version = "1.0.0"
        self.mock_config.target_arn = "arn:aws:iot:us-east-1:123456789012:thing/test-device"
        self.mock_config.deployment_name = "test-deployment"
        self.mock_config.region = "us-east-1"
        self.mock_config.options = {}

        self.mock_gg_client = mock_gg_client.return_value
        
        self.command_args = {
            "target_arn": "arn:aws:iot:us-east-1:123456789012:thing/test-device",
            "deployment_name": "test-deployment",
            "region": "us-east-1"
        }

    @patch("gdk.commands.component.DeployCommand.ComponentDeployConfiguration")
    @patch("gdk.commands.component.DeployCommand.Greengrassv2Client")
    def test_deploy_command_init(self, mock_gg_client, mock_config):
        deploy_command = DeployCommand(self.command_args)
        
        self.assertIsNotNone(deploy_command)
        self.assertEqual(deploy_command.name, "deploy")
        mock_config.assert_called_once_with(self.command_args)
        mock_gg_client.assert_called_once()

    @patch("gdk.commands.component.DeployCommand.component")
    @patch("gdk.commands.component.DeployCommand.utils")
    @patch("gdk.commands.component.DeployCommand.ComponentDeployConfiguration")
    @patch("gdk.commands.component.DeployCommand.Greengrassv2Client")
    def test_deploy_command_run_success(self, mock_gg_client, mock_config, mock_utils, mock_component):
        # Setup mocks
        mock_config.return_value = self.mock_config
        mock_gg_client.return_value = self.mock_gg_client
        mock_utils.get_account_id.return_value = "123456789012"
        
        self.mock_gg_client.get_highest_cloud_component_version.return_value = "1.0.0"
        self.mock_gg_client.create_deployment.return_value = {
            "deploymentId": "test-deployment-id",
            "deploymentName": "test-deployment"
        }
        self.mock_gg_client.get_deployment_status.return_value = {
            "deploymentStatus": "COMPLETED"
        }

        deploy_command = DeployCommand(self.command_args)
        deploy_command.run()

        # Verify deployment was created
        self.mock_gg_client.create_deployment.assert_called_once()
        self.mock_gg_client.get_deployment_status.assert_called_once_with("test-deployment-id")

    @patch("gdk.commands.component.DeployCommand.ComponentDeployConfiguration")
    @patch("gdk.commands.component.DeployCommand.Greengrassv2Client")
    def test_deploy_command_missing_target_arn(self, mock_gg_client, mock_config):
        # Test that missing target ARN raises an exception
        mock_config.side_effect = Exception("Target ARN is not specified")
        
        with self.assertRaises(Exception) as context:
            DeployCommand({})
        
        self.assertIn("Target ARN is not specified", str(context.exception))


if __name__ == "__main__":
    unittest.main()