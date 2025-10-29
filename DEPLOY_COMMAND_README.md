# GDK Deploy Command

The `gdk component deploy` command provides a streamlined way to deploy your Greengrass components to target devices or device groups after building and publishing them.

## Overview

The deploy command completes the development workflow by:
1. Ensuring the component is published (automatically publishes if needed)
2. Creating a deployment to the specified target
3. Monitoring the deployment status

## Usage

### Basic Usage

```bash
gdk component deploy
```

This uses the configuration from your `gdk-config.json` file.

### Command Line Options

```bash
gdk component deploy --target-arn <TARGET_ARN> --deployment-name <NAME> --region <REGION> --options <OPTIONS>
```

#### Arguments

- `--target-arn, -t`: ARN of the target device or device group for deployment
- `--deployment-name, -n`: Name for the deployment (optional, auto-generated if not provided)
- `--region, -r`: AWS region for deployment (optional, uses publish region if not specified)
- `--options, -o`: Extra deployment configuration as JSON string or file path

## Configuration

Add a `deploy` section to your `gdk-config.json`:

```json
{
    "component": {
        "com.example.MyComponent": {
            "author": "Your Name",
            "version": "NEXT_PATCH",
            "build": {
                "build_system": "zip"
            },
            "publish": {
                "bucket": "my-s3-bucket",
                "region": "us-east-1"
            },
            "deploy": {
                "target_arn": "arn:aws:iot:us-east-1:123456789012:thing/MyGreengrassDevice",
                "region": "us-east-1",
                "deployment_name": "MyComponent-Deployment",
                "options": {
                    "deployment_policies": {
                        "failureHandlingPolicy": "ROLLBACK",
                        "componentUpdatePolicy": {
                            "timeoutInSeconds": 60,
                            "action": "NOTIFY_COMPONENTS"
                        }
                    }
                }
            }
        }
    },
    "gdk_version": "1.0.0"
}
```

### Configuration Fields

#### Required
- `target_arn`: ARN of the target device or device group

#### Optional
- `region`: AWS region (defaults to publish region)
- `deployment_name`: Custom deployment name (auto-generated if not provided)
- `options`: Advanced deployment configuration

### Target ARN Examples

**Single Device:**
```
arn:aws:iot:us-east-1:123456789012:thing/MyGreengrassDevice
```

**Device Group:**
```
arn:aws:iot:us-east-1:123456789012:thinggroup/MyDeviceGroup
```

## Advanced Options

The `options` field supports all AWS IoT Greengrass deployment configuration:

```json
{
    "options": {
        "deployment_policies": {
            "failureHandlingPolicy": "ROLLBACK",
            "componentUpdatePolicy": {
                "timeoutInSeconds": 60,
                "action": "NOTIFY_COMPONENTS"
            },
            "configurationValidationPolicy": {
                "timeoutInSeconds": 60
            }
        },
        "iot_job_configuration": {
            "jobExecutionsRolloutConfig": {
                "exponentialRate": {
                    "baseRatePerMinute": 10,
                    "incrementFactor": 2,
                    "rateIncreaseCriteria": {
                        "numberOfNotifiedThings": 10,
                        "numberOfSucceededThings": 5
                    }
                }
            },
            "abortConfig": {
                "criteriaList": [
                    {
                        "failureType": "FAILED",
                        "action": "CANCEL",
                        "thresholdPercentage": 50,
                        "minNumberOfExecutedThings": 10
                    }
                ]
            },
            "timeoutConfig": {
                "inProgressTimeoutInMinutes": 60
            }
        }
    }
}
```

## Development Workflow

The complete development workflow now becomes:

```bash
# 1. Initialize project
gdk component init --template HelloWorld --language python -n MyComponent

# 2. Develop your component code
# ... make changes to your component ...

# 3. Build, publish, and deploy in one command
gdk component deploy
```

Or run each step individually:

```bash
gdk component build
gdk component publish  
gdk component deploy
```

## Deployment Monitoring

The deploy command automatically monitors deployment status and provides updates:

- Shows deployment progress
- Reports completion or failure
- Displays failure reasons if deployment fails
- Times out after 10 minutes (deployment may continue in background)

## Error Handling

The deploy command includes robust error handling:

- Automatically publishes component if not already published
- Validates configuration before deployment
- Provides clear error messages for common issues
- Supports retry logic for transient failures

## Prerequisites

1. AWS credentials configured (`aws configure` or environment variables)
2. Component built and published (or deploy command will handle this automatically)
3. Target device or device group exists and is accessible
4. Appropriate IAM permissions for Greengrass deployments

## IAM Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "greengrass:CreateDeployment",
                "greengrass:GetDeployment",
                "greengrass:ListComponentVersions",
                "iot:DescribeThing",
                "iot:DescribeThingGroup"
            ],
            "Resource": "*"
        }
    ]
}
```

## Examples

### Deploy to Single Device
```bash
gdk component deploy --target-arn arn:aws:iot:us-east-1:123456789012:thing/MyDevice
```

### Deploy to Device Group
```bash
gdk component deploy --target-arn arn:aws:iot:us-east-1:123456789012:thinggroup/ProductionDevices
```

### Deploy with Custom Options
```bash
gdk component deploy --options '{"deployment_policies": {"failureHandlingPolicy": "DO_NOTHING"}}'
```

### Deploy with Options from File
```bash
gdk component deploy --options deployment-config.json
```

This enhancement significantly improves the GDK CLI development experience by providing a complete build-publish-deploy workflow in a single tool.