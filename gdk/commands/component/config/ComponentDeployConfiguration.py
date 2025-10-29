import logging
from pathlib import Path

import gdk.common.consts as consts
import gdk.common.utils as utils
from gdk.commands.component.config.ComponentConfiguration import ComponentConfiguration


class ComponentDeployConfiguration(ComponentConfiguration):
    def __init__(self, args) -> None:
        super().__init__(args)
        self.arguments = args
        self._get_deploy_config_from_args()
        self._get_deploy_config_from_file()

    def _get_deploy_config_from_args(self):
        """
        Gets deploy configuration from the arguments provided to the command.
        """
        self.target_arn = self.arguments.get("target_arn", None)
        self.deployment_name = self.arguments.get("deployment_name", None)
        self.region = self.arguments.get("region", None)
        self.options = self.arguments.get("options", None)

    def _get_deploy_config_from_file(self):
        """
        Gets deploy configuration from the gdk config file.
        """
        deploy_config = self.config.get("deploy", {})
        
        # Use command line args if provided, otherwise fall back to config file
        if not self.target_arn:
            self.target_arn = deploy_config.get("target_arn", None)
        
        if not self.deployment_name:
            self.deployment_name = deploy_config.get("deployment_name", None)
            
        if not self.region:
            self.region = deploy_config.get("region", None)
            
        if not self.options:
            self.options = deploy_config.get("options", {})
        elif isinstance(self.options, str):
            # Handle options passed as JSON string or file path
            self.options = utils.get_json_from_file_or_string(self.options)

        # Validate required configuration
        if not self.target_arn:
            raise Exception(
                f"Target ARN is not specified in the gdk config file '{self.config_file}' or as a command argument. "
                "Please specify the target ARN for deployment."
            )
            
        # Use publish region as fallback for deploy region
        if not self.region:
            publish_config = self.config.get("publish", {})
            self.region = publish_config.get("region", None)
            
        if not self.region:
            raise Exception(
                f"Region is not specified in the gdk config file '{self.config_file}' or as a command argument. "
                "Please specify the AWS region for deployment."
            )

        # Generate deployment name if not provided
        if not self.deployment_name:
            self.deployment_name = f"{self.component_name}-{self.component_version}-deployment"

        logging.debug("Using target ARN: %s", self.target_arn)
        logging.debug("Using deployment name: %s", self.deployment_name)
        logging.debug("Using region: %s", self.region)
        logging.debug("Using options: %s", self.options)