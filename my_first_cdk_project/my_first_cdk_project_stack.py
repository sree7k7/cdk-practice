from contextvars import Token
import constructs

from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    # aws_sqs as sqs,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct
import aws_cdk.aws_ec2 as ec2
# import aws_cdk.aws_s3 as s3
import aws_cdk as core



class MyArtifactStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, is_prod=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        if is_prod:
            artifactBucket = s3.Bucket(
                self,
                "ProdBucket",
                versioned=False,
                encryption=s3.BucketEncryption.S3_MANAGED,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=RemovalPolicy.DESTROY,
                bucket_name="thisisprodbucket0432x"
            )
        else:
            artifactBucket = s3.Bucket(
                    self,
                    "defaultBucket",
                    removal_policy=RemovalPolicy.DESTROY,
                bucket_name="thisisdevbucket0432x"

                )
        output = CfnOutput(
            self,
            "BucketName",
            value=artifactBucket.bucket_name,
            description=f"this is output of bucket",
            export_name="BucketNameArtifactBucket"
        )