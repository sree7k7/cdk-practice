from aws_cdk import (
    Stack,
    RemovalPolicy,
    # aws_sqs as sqs,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct
from .parameters import bucketName



class MyArtifactStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, is_prod=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        #This code defines the parameter value
        # bucket_name = CfnParameter(self, "uploadBucketName", type="String",
        #    description="The name of the Amazon S3 bucket where uploaded files will be stored.")
        # print(regionName)
        # if is_prod:
        #     artifactBucket = s3.Bucket(
        #         self,
        #         "ProdBucket",
        #         versioned=False,
        #         encryption=s3.BucketEncryption.S3_MANAGED,
        #         block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        #         removal_policy=RemovalPolicy.DESTROY
        #         # bucket_name=bucketName
        #     )
        # else:
        #     artifactBucket = s3.Bucket(
        #             self,
        #             "defaultBucket",
        #             removal_policy=RemovalPolicy.DESTROY
        #         # bucket_name="thisisdevbucket0432x"  
        #         )
        
        # mysecondbucket = s3.Bucket(
        #     self,
        #     "mySecondBucket",
        #     bucket_name = "thisbucketnameneeds-to-print-0432",
        #     access_control = s3.BucketAccessControl.PRIVATE,
        #     encryption = s3.BucketEncryption.S3_MANAGED,
        #     versioned = True,
        #     removal_policy=RemovalPolicy.DESTROY,
        #     block_public_access = s3.BlockPublicAccess.BLOCK_ALL
        # )

        # output = CfnOutput(
        #     self,
        #     "BucketName",
        #     value=artifactBucket.bucket_name,
        #     description=f"this is output of bucket",
        #     export_name="BucketNameArtifactBucket"
        # )
        # outp = print(mysecondbucket.bucket_arn)
        # buckname = str(mysecondbucket.bucket_name)
        # print(buckname)
