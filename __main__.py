"""An AWS Python Pulumi program"""

import os
import pulumi
import pulumi_aws as aws
from pathlib import Path


# Choose the lates minimal amzn2 Linux AMI
ami = aws.ec2.get_ami(most_recent="true",
                      owners=["amazon"],
                      region=os.environ.get('awsRegion'),
                      filters=[aws.ec2.GetAmiFilterArgs(name="name",
                                                        values=["*amzn2-ami-minimal-hvm*"])])

group = aws.ec2.SecurityGroup('web-secgrp',
                              description='Enable SSH access',
                              ingress=[
                                  aws.ec2.SecurityGroupIngressArgs(
                                      protocol='tcp',
                                      from_port=22,
                                      to_port=22,
                                      cidr_blocks=['0.0.0.0/0']
                                  )
                              ])

HOME = str(Path.home())
f = open(os.path.join(HOME, ".ssh", "id_rsa.pub"), "r", encoding="utf-8")
public_key = f.read()
f.close()

public_key = public_key.strip()

print(f"Public Key: '{public_key}'\n")

keypair = aws.ec2.KeyPair("deployer-key", public_key=public_key)

server = aws.ec2.Instance('backstage-pulumi-server',
                          instance_type=os.environ.get('instanceType'),
                          instance_name=os.environ.get('instanceName'),
                          vpc_security_group_ids=[group.id],
                          key_name=keypair.key_name,
                          ami=ami.id)

pulumi.export('instance_type', server.instance_type)
pulumi.export('public_key', keypair.public_key)
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)
