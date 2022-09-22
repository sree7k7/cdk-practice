import constructs

from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    # aws_sqs as sqs,
    aws_s3 as s3
)
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
# import aws_cdk.aws_s3 as s3



class MyFirstCdkProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        s3.Bucket(
            self,
            "myBucketId",
            bucket_name="mycdkbucketbysri",
            versioned=True,
            encryption=s3.BucketEncryption.KMS_MANAGED,
            removal_policy=RemovalPolicy.DESTROY            
        )
        bucket = s3.Bucket(
            self, 
            id="mysecondcdkbucketbysri",
            bucket_name="mysecondcdkbucketbysri",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True,
            # removal_policy=s3._RemovalPolicy_9f93c814
            removal_policy=RemovalPolicy.DESTROY

        )
        # This will deploy a vpc will all default resources, so see: cdk synth
        # vpc = ec2.Vpc(self, "VPC")