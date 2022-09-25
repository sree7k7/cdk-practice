
import aws_cdk as cdk
import aws_cdk as core
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct
from my_first_cdk_project.parameters import cidr_mask, vpc_cidr


class CustomVpcStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        custom_vpc = _ec2.Vpc(
            self,
            "CustomVpc",
            cidr=vpc_cidr,
            max_azs=3,
            nat_gateways=0,            
            subnet_configuration = [
                _ec2.SubnetConfiguration(
                    name="PublicSubnetA",
                    subnet_type=_ec2.SubnetType.PUBLIC,

                    # the properties below are optional
                    cidr_mask=cidr_mask
                    # map_public_ip_on_launch=False,

            
                ),
                _ec2.SubnetConfiguration(
                    name="PrivateSubnetB",
                    subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED,                    
                    cidr_mask=cidr_mask

                )
            ]
        )
        cdk.Tags.of(custom_vpc).add("Environmentx", "Dev")

        mybucket = s3.Bucket(
            self,
            "mybucket",
            bucket_name = "testsri0432x",
            access_control = s3.BucketAccessControl.PRIVATE,
            encryption = s3.BucketEncryption.S3_MANAGED,
            versioned = False,
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY
        )
        cdk.Tags.of(mybucket).add("bucket", "Devbucket")





        

        # role = iam.Role(
        #     self,
        #     "BackupRole",
        #     managed_policies=[
        #         iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
        #         iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
        #     ],
        #     assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        # )

        # # sg_group = add_ingress_rule(
        # #     peer=_ec2.Peer.ipv4('5.103.44.42/32'),
        # #     connection=_ec2.Port(
        # #         from_port=22,
        # #         to_port=22,
        # #         protocol=_ec2.Protocol.TCP,
        # #         string_representation='SSH'
        # #     )
        # # )
        # instance = _ec2.Instance(
        #     self,
        #     'Instance',
        #     instance_type=_ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.MICRO),
        #     vpc=custom_vpc,
        #     machine_image=_ec2.MachineImage.latest_amazon_linux(
        #         generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        #     ),
        #     # security_group=sg_group,
        #     role=role,
        #     # user_data=_ec2.UserData.custom(user_data)
        # )


