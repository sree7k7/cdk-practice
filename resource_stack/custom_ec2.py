
import aws_cdk as cdk
import aws_cdk as core
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_s3 as s3, CfnOutput, Fn
from constructs import Construct
from my_first_cdk_project.parameters import cidr_mask, vpc_cidr, instance_type
from .vpc import CustomVpcStack


class CustomEc2Stack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        testbucket = s3.Bucket(
            self,
            "bucketID",
            bucket_name = "bucket-testing-for-bucket-policy-sri",
            access_control = s3.BucketAccessControl.PRIVATE,
            encryption = s3.BucketEncryption.S3_MANAGED,
            versioned = False,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL
        )

        # bucket_policy = s3.BucketPolicy(
        #     self,
        #     "bucketpolicy",
        #     bucket=testbucket,
        #     removal_policy=cdk.RemovalPolicy.DESTROY
        # )

        # myCustomPolicy = iam.PolicyDocument({
        # statements: [new iam.PolicyStatement({
        #     actions: [
        #     'kms:Create*',
        #     'kms:Describe*',
        #     'kms:Enable*',
        #     'kms:List*',
        #     'kms:Put*',
        #     ],
        #     principals: [new iam.AccountRootPrincipal()],
        #     resources: ['*'],
        # })],
        # });



        bucketone = s3.Bucket(
            self,
            "myid",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            encryption=s3.BucketEncryption.S3_MANAGED
            
            # encryption_key=kms.Key(
            #     self,
            #    "id",
            #     enable_key_rotation = False,
            # )
        )

        # bucket_policy=iam.PolicyStatement(
        #     actions=[
        #     "s3:Get*", 
        #     "s3:List*"
        #     ],
        #     resources=[bucketone.arn_for_objects('*')],
        #     principals=[iam.AccountRootPrincipal()]
        # )
        # s3.CfnBucketPolicy(self, 'bucketpolicy',
        #     bucket=bucketone.bucket_name,
        #     policy_document=iam.PolicyDocument(statements=[bucket_policy])
        # )




        my_custom_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                actions=["kms:Create*", "kms:Describe*", "kms:Enable*", "kms:List*", "kms:Put*"
                ],
                principals=[iam.AccountRootPrincipal()],
                # resources=[bucketone.bucket_name.arnForObjects('*')]
                resources=["arn:aws:s3:::*"]
            )]
        )
        kms_key = kms.Key(
            self,
           "KMSkey",
            enable_key_rotation = False,
            description="This is KMS key for DNAC project",
            alias="alias/dnacx",
            enabled=False,
            removal_policy=RemovalPolicy.DESTROY,
            policy=my_custom_policy
        )

        # key = kms.Key(self, "MyKey",
        #     policy=my_custom_policy
        # )