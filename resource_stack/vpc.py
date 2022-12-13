
import os
import aws_cdk as cdk
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import Tags
import aws_cdk.aws_ssm as ssm
from aws_cdk import aws_s3 as s3, CfnOutput
from constructs import Construct
from simulateddatacenter.parameters import cidr_mask, vpc_cidr, CloudVPCCIDR
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_events as events
import aws_cdk.aws_sqs as sqs
import aws_cdk.aws_apigateway as api
import aws_cdk.aws_events_targets as targets
import aws_cdk as core

class CustomVpcStack(Stack):        
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        custom_vpc = ec2.Vpc(
            self,
            "CustomVpc",
            cidr=vpc_cidr,
            max_azs=3,
            nat_gateways=0,            
            subnet_configuration = [
                ec2.SubnetConfiguration(
                    name="PublicSubnetA",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=cidr_mask
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnetB",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,                    
                    cidr_mask=cidr_mask
                )
            ]
        )
  
################### VPC endpoints #####################

        # ssmmessages = ec2.InterfaceVpcEndpoint(self, "ssmmessages",
        #     vpc=custom_vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssmmessages", 443
        #     )
        # )
        # VPCEndpointEC2 = ec2.InterfaceVpcEndpoint(self, "VPCEndpointEC2",
        #     vpc=custom_vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2", 443)
        # )
        # VPCEndpointec2messages = ec2.InterfaceVpcEndpoint(self, "VPCEndpointec2messages",
        #     vpc=custom_vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2messages", 443)
        # )
        # VPCEndpointssm = ec2.InterfaceVpcEndpoint(self, "VPCEndpointssm",
        #     vpc=custom_vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssm", 443)        
        # )
#####################ec2 role###########################
        role = iam.Role(
            self,
            "BackupRole",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
            ],
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        )
#########################  security Group #####################
        sg_group = ec2.SecurityGroup(self, 'BackupSG', vpc=custom_vpc,
        )
        sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(CloudVPCCIDR),
            connection=ec2.Port(
                from_port=22,
                to_port=22,
                protocol=ec2.Protocol.TCP,
                string_representation='SSH'
            )
        )
        sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc_cidr),
            connection=ec2.Port(
                from_port=443,
                to_port=443,
                protocol=ec2.Protocol.TCP,
                string_representation='HTTPS'
            )
        )
        sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(CloudVPCCIDR),
            connection=ec2.Port(
                from_port=-1,
                to_port=-1,
                protocol=ec2.Protocol.ICMP,
                string_representation='ICMP'
            )
        )
        # sg_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4(CloudVPCCIDR),
        #     connection=ec2.Port(
        #         from_port=-1,
        #         to_port=-1,
        #         protocol=ec2.Protocol.ALL,
        #         string_representation='ALL'
        #     )
        # )          
#####################EC2 ####################
        user_data = f'''
            #!/bin/bash
            amazon-linux-extras install epel -y
            yum install s3fs-fuse -y
            sudo yum update -y
            sudo yum install openswan -y
            sudo mkdir /dnac-backup
            # rm /var/lib/cloud/instance/sem/config_scripts_user
            '''

        instance = ec2.Instance(
            self,
            'Instance',
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3_AMD, ec2.InstanceSize.MICRO),
            vpc=custom_vpc,
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            security_group=sg_group,
            role=role,
            user_data=ec2.UserData.custom(user_data),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            block_devices=[
                ec2.BlockDevice(
                device_name="/dev/xvda",
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size= 20,
                    volume_type= ec2.EbsDeviceVolumeType.GP3
                )
            )
            ]                    
        )
        Tags.of(instance).add("automation", "shellscript")        
        
##########s3####
        ACCOUNT_ID= '${Token[AWS.AccountId.3]}'
        account=os.getenv('CDK_DEFAULT_ACCOUNT')
        bucket = s3.Bucket(
            self,
            "bucket",
            # bucket_name = f'somename-{account}',
            access_control = s3.BucketAccessControl.PRIVATE,
            encryption = s3.BucketEncryption.S3_MANAGED,
            versioned = False,
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL
        )
#         ssm_bucket = ssm.StringParameter(self, "Parameter",
#                 allowed_pattern=".*",
#                 description="The bucket name",
#                 parameter_name="/dnac/s3/bucketname",
#                 string_value=bucket.bucket_name,
#                 tier=ssm.ParameterTier.STANDARD
# )
        # ssm_bucket = ssm.StringParameter.v(
        #     self, 
        #     "/dnac/s3/bucketname",            
        #     # string_value=bucket.bucket_name
        #     )


####################### weblinks ##############
# targetgroup: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/NetworkTargetGroup.html
# vpn: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.awsec2/CfnCustomerGateway.html

