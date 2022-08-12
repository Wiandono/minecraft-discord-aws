This repository contains:

* **Minecraft CloudFormation file** for easily and cheaply deploying your Minecraft server to AWS with spot pricing.
* **AWS Lambda Code** with [Zappa](https://github.com/zappa/Zappa) that serves as a Discord Bot Interaction Endpoint URL
* **[pyinvoke](https://github.com/pyinvoke/invoke) Tasks file** to manage your Discord bot commands in your Discord
  Guild/Server.
* **A setup guide** for everything

The CloudFormation template is shamelessly copied from the
[Complete Minecraft Server Deployment (CloudFormation)](https://github.com/vatertime/minecraft-spot-pricing) with some
adjustments. For more details about the template, please check that repository. I will only explain the modifications
that I made to the template used in this project.

The template can be used as it is without the other components in this project if you only want to deploy the server.

# Table of contents

- [Prerequisite](#prerequisite)
- [Usage](#usage)
- [Setting Up AWS](#setting-up-aws)
    - [Modifications from the original template](#modifications-from-the-original-template)
    - [Getting started](#getting-started)
    - [Parameters](#parameters)
- [Setting Up Discord](#setting-up-discord)
- [Setting Up Lambda](#setting-up-lambda)
- [Setting Up Bot Commands](#setting-up-bot-commands)
- [Thank you](#thank-you)

# Prerequisite

[(Back to top)](#table-of-contents)

This guide will assume that you have already setup your AWS account. If not, please
register [here](https://aws.amazon.com/).

# Usage

[(Back to top)](#table-of-contents)

1. Install [Python 3.8](https://www.python.org/downloads/release/python-380/) (you can update this to another version,
   as long as Lambda have the support for it. Don't forget to update the `runtime` value in zappa_settings.json).

2. Clone this repository.

3. Install [Pipenv](https://pipenv.pypa.io/en/latest/). If you're using PyCharm you can setup the Pipenv interpreter.

   *Once finished, you can run:*

    ```sh
    pipenv install
    ```

   *to install all the necessary dependencies.*

4. Continue in [Setting up AWS](#setting-up-aws) and [Setting up Discord](#setting-up-discord).

# Setting up AWS

[(Back to top)](#table-of-contents)

## Modifications from the original template

The main goals of the modification are:

* Further optimizing the cost.
* Add more environment variables for the Docker image.
* Optimize the server performance.

**Instance Type**

This template lists t3a and t4g family instances starting from t3a.small and t4g.small. This type of instance should 
already be enough to support 2–5 players.

**Subnet**

To enable One Zone pricing class for EFS, this template only uses one subnet.

**Environment Variables**

The following environment variables are added:

* SIMULATION_DISTANCE
* SNOOPER_ENABLED
* SPAWN_PROTECTION
* ONLINE_MODE
* USE_AIKAR_FLAGS
* MAX_TICK_TIME
* ENABLE_AUTOPAUSE
* PLAYER_IDLE_TIMEOUT
* MODRINTH_PROJECTS

## Getting started

If you're planning to also create the Discord Bot to control your server, please take note of the following information:

* AWS Region from step 2 (e.g, ap-southeast-1)
* CloudFormation stack name from step 9

1. Navigate to the CloudFormation console.

2. Ensure that you've selected a suitable AWS Region (closest to you and your friends) via the selector at the top 
right.

3. Create a new stack.

4. Select Create template in Designer.

5. Change the template language to YAML.

6. In the bottom left, change from Components to Template.

7. Copy and paste the `cloudformation.yml` content into the designer.

8. You can click the Validate template button (a checkmark) to check the template or the Create stack button (a cloud 
with an up arrow) to start the stack creation process.

9. Create a stack name for your CloudFormation stack.

10. Fill in the parameters.

11. Create the stack.

## Parameters

**Instance Type**

When you use the t4g family of instances, please make sure that you're using the correct AMI image. If not, your 
CloudFormation will get stuck in the creation process.

In the `cloudformation.yml` file, line 9 to 10, you can see 2 available values:

- /aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id
- /aws/service/ecs/optimized-ami/amazon-linux-2/arm64/recommended/image_id

Please use the first one for t3a and the second one for t4g. You can input this value at the very end of the Specify 
stack details page.

**Maximum Spot Pricing**

The value of this property varies depending on what type of instance you're planning to use. Check the current spot 
pricing for the instance type you want to use [here](https://aws.amazon.com/ec2/spot/pricing/). You can then set the 
value equal to the current price or slightly higher to ensure your request can always be fulfilled and not easily 
terminated when the price is increasing.

**Java memory-heap Limit**

You can increase this limit as you choose an instance with higher memory. However, make certain that you did not attempt
to allocate too much memory. Spare at least 1 GB for the system.

**Max View Distance**

For the survival type of server, a value of 6 to 8 is recommended.

**Max Simulation Distance**

You can set this to Max View Distance + 1, as you essentially do not need to simulate something that you can't see.

**ECS AMI**

t3a instance: /aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id

t4g instance: /aws/service/ecs/optimized-ami/amazon-linux-2/arm64/recommended/image_id

# Setting up Discord

[(Back to top)](#table-of-contents)

1. Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications).

2. After finishing creating your application, you should arrive at the General Information page. This page contains 
information about your Application ID and the Public Key required for the Setting Up Lambda Part.

3. Go to the Bot tab, and click Add Bot.

4. Go to the OAuth2 tab and check the application.command box. This will let you add new slash commands.

5. You can use the generated URL to invite your bot to your Discord server.

# Setting Up Lambda

[(Back to top)](#table-of-contents)

Please do the step-by-step guide in the Usage section first if you haven't already.

Firstly, let's setup your development environment to allow Zappa to do its deployment for you.

1. Log in to your AWS account and navigate to the IAM Console.

2. Add a new user with programmatic access.

3. This user will need the ability to do deployment with Zappa. Please check this [issue](https://github.com/Miserlou/Zappa/issues/244).

   This is the permission that I currently use:

   ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:AttachRolePolicy",
                    "iam:GetRole",
                    "iam:CreateRole",
                    "iam:PassRole",
                    "iam:PutRolePolicy"
                ],
                "Resource": [
                    "arn:aws:iam::<ACCOUNT_ID>:role/*ZappaLambdaExecutionRole"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "apigateway:DELETE",
                    "apigateway:GET",
                    "apigateway:PATCH",
                    "apigateway:POST",
                    "apigateway:PUT",
                    "events:DeleteRule",
                    "events:DescribeRule",
                    "events:ListRules",
                    "events:ListRuleNamesByTarget",
                    "events:ListTargetsByRule",
                    "events:PutRule",
                    "events:PutTargets",
                    "events:RemoveTargets",
                    "lambda:AddPermission",
                    "lambda:CreateFunction",
                    "lambda:DeleteFunction",
                    "lambda:DeleteFunctionConcurrency",
                    "lambda:GetAlias",
                    "lambda:GetFunction",
                    "lambda:GetFunctionConfiguration",
                    "lambda:GetPolicy",
                    "lambda:InvokeFunction",
                    "lambda:ListVersionsByFunction",
                    "lambda:RemovePermission",
                    "lambda:UpdateFunctionCode",
                    "lambda:UpdateFunctionConfiguration",
                    "cloudformation:CreateStack",
                    "cloudformation:DeleteStack",
                    "cloudformation:DescribeStackResource",
                    "cloudformation:DescribeStacks",
                    "cloudformation:ListStackResources",
                    "cloudformation:UpdateStack",
                    "logs:DeleteLogGroup",
                    "logs:DescribeLogStreams",
                    "logs:FilterLogEvents"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:CreateBucket",
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads"
                ],
                "Resource": [
                    "arn:aws:s3:::zappa-*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:DeleteObject",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts"
                ],
                "Resource": [
                    "arn:aws:s3:::zappa-*/*"
                ]
            }
        ]
    }
   ```

4. After you finish creating the IAM user, you should get the Access Key ID and Secret Key. Please store it securely.

5. Now run this command to configure your AWS credentials:

    ```shell
    aws configure
    ```

   If you haven't installed aws-cli, please go to this [page] (https://aws.amazon.com/cli/).

6. You can then enter the access key and secret key of your newly created user.

Next, let's configure Zappa based on your AWS and Discord setup.

1. Navigate to the zappa_settings.json file.

2. Update all environment variables value from line 5 to 8.

    - `APPLICATION_ID` and `BOT_PUBLIC_KEY values can be found in the Setting Up Discord section.

    - `CF_STACK_NAME` and `CF_REGION values can be found in the Setting up AWS section.

3. The value of `aws_region` should be the same as `CF_REGION`.

4. You can update the `project_name` with whatever name that you want to use.

5. We need to add 1 more property in the `zappa_settings.json` file. It's `extra_permissions`. You will need this extra 
permission to allow Lambda to make the necessary API calls to AWS to start, stop, and check on your CloudFormation stack 
resources for you.

    - For this task, we need one more piece of information from your AWS account, which is your AWS Account ID.
    - In your AWS Console, in the top right corner, you should be able to see your account name.
    - Click it and a dropdown should appear.
    - In there you can find your Account ID.

6. With that information in hand, you can then add this new property to your `zappa_settings.json`.

   ```json
       "extra_permissions": [
         {
           "Effect": "Allow",
           "Action": [
             "cloudformation:UpdateStack",
             "cloudformation:DescribeStacks",
             "cloudformation:DescribeStackEvents",
             "iam:PassRole",
             "autoscaling:CreateLaunchConfiguration",
             "autoscaling:UpdateAutoScalingGroup",
             "autoscaling:DeleteLaunchConfiguration",
             "ecs:DescribeServices",
             "ecs:UpdateService"
           ],
           "Resource": [
             "arn:aws:cloudformation:<YOUR AWS REGION>:<YOUR AWS ACCOUNT ID>:stack/<YOUR CF_STACK_NAME>/*",
             "arn:aws:iam::<YOUR AWS ACCOUNT ID>:role/<YOUR CF_STACK_NAME>-*",
             "arn:aws:autoscaling:<YOUR AWS REGION>:<YOUR AWS ACCOUNT ID>:launchConfiguration:*:launchConfigurationName/<YOUR CF_STACK_NAME>-*",
             "arn:aws:autoscaling:<YOUR AWS REGION>:<YOUR AWS ACCOUNT ID>:autoScalingGroup:*:autoScalingGroupName/<YOUR CF_STACK_NAME>-asg",
             "arn:aws:ecs:<YOUR AWS REGION>:<YOUR AWS ACCOUNT ID>:service/<YOUR CF_STACK_NAME>-cluster/<YOUR CF_STACK_NAME>-ecs-service"
           ]
         },
         {
           "Effect": "Allow",
           "Action": [
             "ssm:GetParameter",
             "ec2:DescribeImages",
             "ec2:DescribeInstances",
             "ecs:RegisterTaskDefinition",
             "ecs:DeregisterTaskDefinition",
             "autoscaling:DescribeLaunchConfigurations",
             "autoscaling:DescribeAutoScalingGroups"
           ],
           "Resource": "*"
         }
       ],
   ```

   Please update the `AWS REGION`, `AWS ACCOUNT ID` and `CF_STACK_NAME`

7. You can then deploy your Lambda with Zappa by running this command:

    ```shell
   zappa deploy dev
    ```

   If you make changes to the main.py file, you can update your deployment by running this command:

    ```shell
    zappa update dev
    ```

8. When the deployment is finished, it should tell you the API gateway URL. Take note of this value.

9. Navigate to your Discord Developer Portal and your newly created app.

10. In the General information page, update the Interactions Endpoint URL with the one you just copied.

# Setting up Bot Commands

[(Back to top)](#table-of-contents)

In this last step, we will register a slash command of your bot in a specific guild. If you want to register a global
command instead, you can just go ahead and edit the tasks.py file.

1. Open tasks.py

2. Enter your `APPLICATION ID` and `GUILD_ID`. You can find Guild ID from your server settings.

3. And finally, run this command to register it with your bot:

    ```shell
    invoke register-commands
    ```

4. Finished!

Now you can enjoy playing Minecraft with your friends and have the ability to turn on and turn off the server easily via
Discord.

# Thank you

* [vatertime](https://github.com/vatertime) for the template https://github.com/vatertime/minecraft-spot-pricing.
* [helen](https://oozio.medium.com/) for the inspiration to create the Discord bot https://oozio.medium.com/serverless-discord-bot-55f95f26f743
