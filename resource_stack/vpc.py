
from inspect import Parameter
from aws_cdk import (
    Duration,
    CfnTag
)
import aws_cdk as cdk
import aws_cdk as core
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as iam
import aws_cdk.aws_ssm as ssm
from aws_cdk import aws_s3 as s3, CfnOutput
from constructs import Construct
from my_first_cdk_project.parameters import cidr_mask, vpc_cidr, ipaddress, CustomerGatewayIP, targetTwoIpAddress, targetOneIpAddress
from aws_cdk.aws_elasticloadbalancingv2 import NetworkLoadBalancer, NetworkListener, NetworkTargetGroup, Protocol, NetworkListenerAction
from aws_cdk import (
aws_elasticloadbalancingv2 as elbv2,
)
from aws_cdk import aws_elasticloadbalancingv2_targets as elasticloadbalancingv2_targets


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
                    name="PublicSubnetB",
                    subnet_type=_ec2.SubnetType.PRIVATE_ISOLATED,                    
                    cidr_mask=cidr_mask

                )
            ]
        )
        cdk.Tags.of(custom_vpc).add("Environmentx", "Dev")
  
######### VPC endpoints

        ssmmessages = _ec2.InterfaceVpcEndpoint(self, "ssmmessages",
            vpc=custom_vpc,
            service=_ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssmmessages", 443)

        )

        VPCEndpointEC2 = _ec2.InterfaceVpcEndpoint(self, "VPCEndpointEC2",
            vpc=custom_vpc,
            service=_ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2", 443)
        )

        VPCEndpointec2messages = _ec2.InterfaceVpcEndpoint(self, "VPCEndpointec2messages",
            vpc=custom_vpc,
            service=_ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2messages", 443)
        )
        VPCEndpointssm = _ec2.InterfaceVpcEndpoint(self, "VPCEndpointssm",
            vpc=custom_vpc,
            service=_ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssm", 443)        )


        role = iam.Role(
            self,
            "BackupRole",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                # iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMMFullAccess'),
            ],
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com')
        )
#########################  security Group
        sg_group = _ec2.SecurityGroup(
            self,
            'BackupSG',
            vpc=custom_vpc,
        )


        sg_group.add_ingress_rule(
            peer=_ec2.Peer.ipv4('5.103.44.42/32'),
            connection=_ec2.Port(
                from_port=22,
                to_port=22,
                protocol=_ec2.Protocol.TCP,
                string_representation='SSH'
            )
        )
        sg_group.add_ingress_rule(
            peer=_ec2.Peer.ipv4('10.1.0.0/16'),
            connection=_ec2.Port(
                from_port=443,
                to_port=443,
                protocol=_ec2.Protocol.TCP,
                string_representation='HTTPS'
            )
        )
############## Parameter store##############

        parameter = ssm.StringParameter(
            self,
            "UserPassword",
            string_value="sometext",
            parameter_name="/dnac/userpasswd"
        )
###### s3 Bucket Storage####################
        # instance.node.addDependency(storage);
        storage = s3.Bucket(
            self,
            "DNACBucket",
            bucket_name = "dnac-backup-bucket-dfds",
            access_control = s3.BucketAccessControl.PRIVATE,
            encryption = s3.BucketEncryption.S3_MANAGED,
            versioned = True,
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY
        )
        
#####################EC2 ####################
        user_data = f'''
            #!/bin/bash
            amazon-linux-extras install epel -y
            yum install s3fs-fuse -y


            #cdksudo useradd -m kristian -p poliasdw
            mkdir /tmp/hello
            sudo mkdir /dnac-backup
            sudo chmod 777 /dnac-backup/

            #usermanagement
            sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
            sed -i 's/ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config

            sudo useradd kristian
            sudo chpasswd <<<"kristian:{parameter.value_for_string_parameter}"
            sudo usermod -d /dnac-backup/ kristian

            echo "{storage.bucket_name} /dnac-backup fuse.s3fs _netdev,allow_other,iam_role=auto 0 0" >> /etc/fstab
            mount -a
            rm /var/lib/cloud/instance/sem/config_scripts_user
            '''

        instance = _ec2.Instance(
            self,
            'Instance',
            instance_type=_ec2.InstanceType.of(_ec2.InstanceClass.BURSTABLE3, _ec2.InstanceSize.MICRO),
            vpc=custom_vpc,
            machine_image=_ec2.MachineImage.latest_amazon_linux(
                generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            security_group=sg_group,
            role=role,
            user_data=_ec2.UserData.custom(user_data),
            vpc_subnets=_ec2.SubnetSelection(
                subnet_type=_ec2.SubnetType.PUBLIC
            )                    
        )

        
###############  Network load balancer ##############

        loadbalancer = NetworkLoadBalancer(
            self,
            'BackupNetworkLoadbalancer',
            vpc=custom_vpc,
            internet_facing=True,
        )

############### Target group ######################

        ip_target = elasticloadbalancingv2_targets.IpTarget(targetOneIpAddress, 22, "all")
        ip_target = elasticloadbalancingv2_targets.IpTarget(targetTwoIpAddress, 22, "all")

        target_group = NetworkTargetGroup(
            self,
            "TargetGroup",
            vpc=custom_vpc,
            target_type=elbv2.TargetType.IP,
            # targets=[elbv2.CfnTargetGroup.TargetDescriptionProperty(
            #     id=
            # )],
            targets = [ip_target],
            port=22
        )
############## Listener ######################
        
        nlb_listener = NetworkListener(
            self,
            'BackupNetworkListener',
            protocol=Protocol.TCP,
            port=22,
            load_balancer=loadbalancer,
            default_action= NetworkListenerAction.forward([target_group])                                    
            # default_target_groups=[target_group]
            # network_listener_action = elbv2.NetworkListenerAction.forward([target_group],
            #     stickiness_duration=cdk.Duration.minutes(30)
            # )

        )  

############## VPN connection ################


        all_data_out = _ec2.VpnConnection.metric_all_tunnel_data_out()

            # For a specific vpn connection
        vpn_connection = custom_vpc.add_vpn_connection("Dynamic",
                ip=CustomerGatewayIP
            )
        state = vpn_connection.metric_tunnel_state()

###############VPN solution with features ###################

        # cfn_customer_gateway = _ec2.CfnCustomerGateway(self, "MyCfnCustomerGateway",
        #     bgp_asn=65000,
        #     ip_address=CustomerGatewayIP,
        #     type="ipsec.1",

        #     # the properties below are optional
        #     tags=[CfnTag(
        #         key="Name",
        #         value="CGWIP"
        #     )]

        # )

        # vpn_gateway = _ec2.VpnGateway(self, "MyVpnGateway",
        #     type="ipsec.1",

        #     # the properties below are optional
        #     amazon_side_asn=65000
        # )

        # cfn_vPNGateway_route_propagation = _ec2.CfnVPNGatewayRoutePropagation(self, "MyCfnVPNGatewayRoutePropagation",
        #     vpn_gateway_id=vpn_gateway.gateway_id,
        #     route_table_ids=[route_table.logical_id]
        # )

        ##################### Route Table #######################        
    #     route_table = _ec2.CfnRouteTable(self, "MyCfnRouteTable",
    #     vpc_id=custom_vpc.vpc_id,

    #     # the properties below are optional
    #     tags=[CfnTag(
    #         key="Name",
    #         value="vpc-route-table"
    #     )]
    # )


        # cfn_tag = cdk.CfnTag(
        #     key="connection",
        #     value="vpn"
        # )



######### Outputs ############################

        vpcoutput = CfnOutput(
            self,
            "VPCoutPutId",
            value=custom_vpc.vpc_id,
            export_name="VPCoutPutId"
        )


####################### weblinks ##############
# targetgroup: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/NetworkTargetGroup.html
# vpn: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnCustomerGateway.html