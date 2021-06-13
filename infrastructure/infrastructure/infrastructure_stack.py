import os

from aws_cdk import (
    core as cdk,
    aws_ecr_assets as ecr_assets,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ec2 as ec2
)

APP_NAME = 'application'

class InfrastructureStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        task_definition = ecs.Ec2TaskDefinition(
            self, ecs.TaskDefinition.__name__,
            network_mode=ecs.NetworkMode.BRIDGE,
            family=APP_NAME
        )
        
        prev_def = None
        for image in ['app', 'nginx']:

            image_asset = ecr_assets.DockerImageAsset(
                self, ecr_assets.DockerImageAsset.__name__ + image,
                directory=os.path.dirname(os.path.realpath(__file__)) + '../../../' + image
            )
            
            container = ecs.ContainerImage.from_docker_image_asset(image_asset)

            container_def = task_definition.add_container(
                id=image,
                image=container,
                memory_limit_mib=256,
                cpu=256,
                logging=ecs.LogDrivers.aws_logs(stream_prefix=APP_NAME),
                essential=True
            )
            if image == 'nginx':
                container_def.add_port_mappings(ecs.PortMapping(container_port=80, protocol=ecs.Protocol.TCP))
                container_def.add_link(prev_def)

            prev_def = container_def
               
        # create cluster
        cluster = ecs.Cluster(
            self, ecs.Cluster.__name__
        )

        # add instances to the cluster
        cluster.add_capacity(
            'capacity',
            instance_type=ec2.InstanceType('c5.large'),
            machine_image_type=ecs.MachineImageType.BOTTLEROCKET,
            desired_capacity=2
        )

        # define service and desired number of instantiations of the task definition 
        # to keep running on the service
        service = ecs.Ec2Service(
            self, ecs.Ec2Service.__name__,
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2
        )

        # define auto scaling for service
        scaling = service.auto_scale_task_count(
            max_capacity=4
        )

        # define auto scaling policy for service
        scaling.scale_on_cpu_utilization(
            'policy',
            target_utilization_percent=50
        )

        # define application load balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, elbv2.ApplicationLoadBalancer.__name__,
            vpc=cluster.vpc,
            internet_facing=True
        )

        # add listener to load balancer
        listener = alb.add_listener(
            APP_NAME,
            port=80,
            open=True
        )

        # add service as target of listener
        listener.add_targets(
            APP_NAME,
            targets=[
                service.load_balancer_target(
                    container_name='nginx',
                    container_port=80
                )   
            ], 
            port=80
        )