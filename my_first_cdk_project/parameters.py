import ipaddress
from pickle import FALSE, TRUE

# VPC
bucketName = "thisisuserbucketfromparametersfile"
regionName = "eu-west-1"
vpc_cidr = "10.1.0.0/16"
cidr_mask = 24
set_resource = TRUE


#EC2
instance_type = "t3.micro"

#VPN config
targetOneIpAddress = "10.2.0.84"
targetTwoIpAddress = "10.2.0.83"
CustomerGatewayIP = "3.70.235.142"
