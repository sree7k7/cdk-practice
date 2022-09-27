#!/usr/bin/env python3
from multiprocessing.sharedctypes import Value
import os

import aws_cdk as cdk
import aws_cdk as core

from my_first_cdk_project.my_first_cdk_project_stack import MyArtifactStack
from resource_stack.vpc import CustomVpcStack
from resource_stack.custom_ec2 import CustomEc2Stack

# env_US = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="us-east-1")
# env_EU = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region="eu-central-1")
app = cdk.App()
# MyArtifactStack(app, "myDevStack", env=env_US
# MyArtifactStack(app, "myDevStack", env=env_US
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    # env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
    # )
# MyArtifactStack(app, "myProdStack", is_prod=True, env=env_EU)
# CustomEc2Stack(app, "EC2", env=env_EU)
CustomEc2Stack(app, "s3")
CustomVpcStack(app, "VPC")        

# cdk.Tags.of(app).add("stacklevelkey", "stacklevelvalue")

app.synth()
