# Web Service Starter Kit

This repository contains starter code for quickly deploying the scaffoldings for a basic web service.

## Architecture

An ECS cluster is launched with two EC2 c5.large instances. A service is then configured to run on the cluster. The service runs two instances of the task, which consists of two containers. One container is for NGINX, and the other container is for Gunicorn/Flask. NGINX acts as a reverse proxy, forwarding all traffic to Gunicorn/Flask, which acts as the WSGI application server. An autoscaling group is configured for the service so that average CPU utilization accross the tasks is 50%. An application load balancer is also configured, and it has the two EC2 instances in the cluster registered as targets. The load balancer listens on port 80 and forwards all traffic to the EC2 instances, which then have the traffic processed by the NGINX containers listening on port 80 as well.

All in all, the basic concept is ALB -> NGINX -> GUNICORN -> FLASK.

## Usage Guide

To deploy the application, run `deploy_infra.sh`. You will need python and the AWS CDK CLI installed beforehand.

To run the application locally with Docker, run `start_service.sh`. You will need Docker running. Docker compose will be used to spin up the two containers.

## TODOs

* This is a barebones implementation. Additional settings should be added to the `nginx.conf` file so that unwanted traffic can immediately be dropped

* The cluster itself is not provisioned with autoscaling. Only the ECS service is

* The application has not been load tested. Experiments should be done to determine the optimal number of workers/connections for Gunicorn/NGINX for the desired workload and performance

* Currently the application doesn't do much, and just returns "Hello, World!"
