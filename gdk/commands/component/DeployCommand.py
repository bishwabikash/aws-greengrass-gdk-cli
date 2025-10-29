import logging
import time

import gdk.commands.component.component as component
import gdk.common.utils as utils
from gdk.aws_clients.Greengrassv2Client import Greengrassv2Client
from gdk.commands.Command import Command
from gdk.commands.component.config.ComponentDeployConfiguration import ComponentDeployConfiguration


class DeployCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "deploy")

        self.project_config = ComponentDeployConfiguration(command_args)
        self.greengrass_client = Greengrassv2Client(self.project_config.region)

    def run(self):
        try:
            self.try_publish()
            deployment_response = self._deploy_component(
                self.project_config.component_name, 
                self.project_config.component_version
            )
            self._monitor_deployment_status(deployment_response["deploymentId"])
        except Exception:
            logging.error(
                "Failed to deploy version '%s' of the component '%s' to target '%s'.",
                self.project_config.component_version,
                self.project_config.component_name,
                self.project_config.target_arn,
            )
            raise

    def try_publish(self):
        """
        Ensures the component is published before attempting deployment.
        """
        component_name = self.project_config.component_name
        component_version = self.project_config.component_version
        
        logging.debug("Checking if the component '%s' version '%s' is published.", component_name, component_version)
        
        # Check if component version exists in the cloud
        try:
            component_arn = f"arn:aws:greengrass:{self.project_config.region}:{utils.get_account_id()}:components:{component_name}"
            existing_version = self.greengrass_client.get_highest_cloud_component_version(component_arn)
            
            if existing_version != component_version:
                logging.warning(
                    "The component '%s' version '%s' is not published or doesn't match the latest version '%s'.\n"
                    "Publishing the component before deploying it.", 
                    component_name, component_version, existing_version
                )
                component.publish({})
            else:
                logging.info("Component '%s' version '%s' is already published.", component_name, component_version)
                
        except Exception:
            logging.warning(
                "Could not verify if component '%s' version '%s' is published.\n"
                "Attempting to publish the component before deploying it.", 
                component_name, component_version
            )
            component.publish({})

    def _deploy_component(self, component_name, component_version):
        """
        Deploys the component to the specified target.
        
        Args:
            component_name: Name of the component to deploy
            component_version: Version of the component to deploy
            
        Returns:
            Dictionary containing deployment response
        """
        logging.info(
            "Deploying component '%s' version '%s' to target '%s'.", 
            component_name, component_version, self.project_config.target_arn
        )

        # Prepare component configuration for deployment
        components = {
            component_name: {
                "componentVersion": component_version
            }
        }

        # Extract deployment options
        options = self.project_config.options
        deployment_policies = options.get("deployment_policies", None)
        iot_job_configuration = options.get("iot_job_configuration", None)
        component_update_policy = options.get("component_update_policy", None)

        # Create the deployment
        deployment_response = self.greengrass_client.create_deployment(
            target_arn=self.project_config.target_arn,
            components=components,
            deployment_name=self.project_config.deployment_name,
            deployment_policies=deployment_policies,
            iot_job_configuration=iot_job_configuration,
            component_update_policy=component_update_policy
        )

        logging.info(
            "Successfully created deployment '%s' with ID '%s'.",
            deployment_response.get("deploymentName"),
            deployment_response.get("deploymentId")
        )

        return deployment_response

    def _monitor_deployment_status(self, deployment_id, timeout_minutes=10):
        """
        Monitors the deployment status and provides updates.
        
        Args:
            deployment_id: ID of the deployment to monitor
            timeout_minutes: Maximum time to wait for deployment completion
        """
        logging.info("Monitoring deployment status for deployment ID '%s'...", deployment_id)
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while True:
            try:
                deployment_status = self.greengrass_client.get_deployment_status(deployment_id)
                status = deployment_status.get("deploymentStatus")
                
                logging.info("Deployment status: %s", status)
                
                if status in ["COMPLETED", "FAILED", "CANCELED"]:
                    if status == "COMPLETED":
                        logging.info("Deployment completed successfully!")
                    else:
                        logging.error("Deployment ended with status: %s", status)
                        if "failureReason" in deployment_status:
                            logging.error("Failure reason: %s", deployment_status["failureReason"])
                    break
                
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    logging.warning(
                        "Deployment monitoring timed out after %d minutes. "
                        "Deployment may still be in progress. Check AWS console for updates.",
                        timeout_minutes
                    )
                    break
                
                # Wait before next check
                time.sleep(30)
                
            except Exception as e:
                logging.error("Error monitoring deployment status: %s", str(e))
                break