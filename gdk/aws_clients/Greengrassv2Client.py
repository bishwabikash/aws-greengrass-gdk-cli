import logging
import boto3


class Greengrassv2Client:
    """
    Greengrasv2 client utils wrapper
    """

    def __init__(self, _region):
        self.client = boto3.client("greengrassv2", region_name=_region)

    def get_highest_cloud_component_version(self, component_arn) -> str:
        """
        Gets highest version of the component from the sorted order of its versions from an account in a region.

        Returns highest version of the component if it exists already. Else returns None.
        """

        try:
            component_versions = self.get_component_version(component_arn)
            if not component_versions:
                return None
            return component_versions[0]["componentVersion"]
        except Exception:
            logging.error("Error while getting the component versions using arn: %s.", component_arn)
            raise

    def get_component_version(self, component_arn) -> dict:
        comp_list_response = self.client.list_component_versions(arn=component_arn)
        return comp_list_response["componentVersions"]

    def create_gg_component(self, file_path) -> None:
        """
        Creates a GreengrassV2 private component version using its recipe.

        Raises an exception if the recipe is invalid or the request is not successful.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                response = self.client.create_component_version(inlineRecipe=f.read())
                logging.info(
                    "Created private version '%s' of the component '%s' in the account.",
                    response.get("componentVersion"),
                    response.get("componentName"),
                )
            except Exception:
                logging.error("Failed to create a private version of the component using the recipe at '%s'.", file_path)
                raise

    def create_deployment(self, target_arn, components, deployment_name=None, deployment_policies=None, 
                         iot_job_configuration=None, component_update_policy=None) -> dict:
        """
        Creates a deployment for GreengrassV2 components to target devices or device groups.

        Args:
            target_arn: ARN of the target device or device group
            components: Dictionary of components to deploy with their configurations
            deployment_name: Optional name for the deployment
            deployment_policies: Optional deployment policies
            iot_job_configuration: Optional IoT job configuration
            component_update_policy: Optional component update policy

        Returns:
            Dictionary containing deployment response

        Raises an exception if the deployment creation fails.
        """
        try:
            deployment_request = {
                "targetArn": target_arn,
                "components": components
            }
            
            if deployment_name:
                deployment_request["deploymentName"] = deployment_name
            
            if deployment_policies:
                deployment_request["deploymentPolicies"] = deployment_policies
            
            if iot_job_configuration:
                deployment_request["iotJobConfiguration"] = iot_job_configuration
                
            if component_update_policy:
                deployment_request["componentUpdatePolicy"] = component_update_policy

            response = self.client.create_deployment(**deployment_request)
            
            logging.info(
                "Created deployment '%s' with ID '%s' for target '%s'.",
                response.get("deploymentName", "Unnamed"),
                response.get("deploymentId"),
                target_arn
            )
            
            return response
            
        except Exception:
            logging.error("Failed to create deployment for target '%s'.", target_arn)
            raise

    def get_deployment_status(self, deployment_id) -> dict:
        """
        Gets the status of a deployment.

        Args:
            deployment_id: ID of the deployment to check

        Returns:
            Dictionary containing deployment status information
        """
        try:
            response = self.client.get_deployment(deploymentId=deployment_id)
            return response
        except Exception:
            logging.error("Failed to get deployment status for deployment ID '%s'.", deployment_id)
            raise
