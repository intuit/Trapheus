<div align="center">
<img width="300" 
src="screenshots/Trapheus.png">
</div>
<div align="center"><a href="https://circleci.com/gh/intuit/Trapheus"><img src="https://circleci.com/gh/intuit/Trapheus.svg?style=svg" alt="TravisCI Build Status"/></a>
<a href = "https://coveralls.io/github/intuit/Trapheus?branch=master"><img src= "https://coveralls.io/repos/github/intuit/Trapheus/badge.svg?branch=master" alt = "Coverage"/></a>
  <a href="http://www.serverless.com"><img src="http://public.serverless.com/badges/v3.svg" alt="serverless badge"/></a>
  <a href="https://github.com/intuit/Trapheus/releases"><img src="https://img.shields.io/github/v/release/intuit/trapheus.svg" alt="release badge"/></a>
  <a href="https://github.com/intuit/Trapheus/wiki/Support"><img src="https://img.shields.io/badge/support-slack-blue" alt="support badge"/></a>
</div>

- [AWS RDS Snapshot Restoration](#Trapheus)
- [Pre-Requisites](#pre-requisites)
- [Parameters](#parameters)
- [Instructions](#instructions)
- [Execution](#execution)
- [How it Works](#how-it-works)
  - [AWS Step Functions State Machine](#aws-step-functions-state-machine)
- [Contributing to Trapheus](#contributing-to-trapheus)


With Trapheus, it becomes easy to get and restore database instances from snapshots into any dev, staging or production environments. Trapheus supports individual RDS Snapshot as well as cluster snapshot restore operations. 
Trapheus is modelled as a state machine, with the help of AWS step functions, that executes different steps in order to restore an existing database from a snapshot. When restoring the database, Trapheus simply renames the database making it lot faster than the usual SQL dump.
Trapheus can be scheduled using a cloudwatch alarm rule or can be run using any of the supported AWS step function triggers.

**Important:** this application uses various AWS services and there are costs associated with these services after the Free Tier usage - please see the [AWS  pricing page](https://aws.amazon.com/pricing/) for details.


```bash

├── CONTRIBUTING.md                               <-- How to contribute to Trapheus
├── LICENSE.md                                    <-- The MIT license.
├── README.md                                     <-- The Readme file.
├── events
│   └── event.json                                <-- JSON event file to be used for local SAM testing
├── screenshots                                   <-- Folder for screenshots of teh state machine.
│   ├── Trapheus-logo.png
│   ├── cluster_restore.png
│   ├── cluster_snapshot_branch.png
│   ├── failure_handling.png
│   ├── instance_restore.png
│   ├── instance_snapshot_branch.png
│   ├── isCluster_branching.png
│   └── restore_state_machine.png
├── src
│   ├── checkstatus
│   │   ├── DBClusterStatusWaiter.py              <-- Python Waiter(https://boto3.amazonaws.com/v1/documentation/api/latest/guide/clients.html#waiters) for checking the status of the cluster
│   │   ├── get_dbcluster_status_function.py      <-- Python Lambda code for polling the status of a clusterised database
│   │   ├── get_dbstatus_function.py              <-- Python Lambda code for polling the status of a non clusterised RDS instance
│   │   └── waiter_acceptor_config.py             <-- Config module for the waiters
│   ├── common                                    <-- Common modules across the state machine deployed as a AWS Lambda layer.
│   │   ├── common.zip
│   │   └── python
│   │       ├── constants.py                      <-- Common constants used across the state machine.
│   │       ├── custom_exceptions.py              <-- Custom exceptions defined for the entire state machine.
│   │       └── utility.py                        <-- Utility module.
│   ├── delete
│   │   ├── cluster_delete_function.py           <-- Python Lambda code for deleting a clusterised database.
│   │   └── delete_function.py                   <-- Python Lambda code for deleting a non clusterised RDS instance.
│   ├── emailalert
│   │   └── email_function.py                    <-- Python Lambda code for sending out failure emails.
│   ├── rename
│   │   ├── cluster_rename_function.py           <-- Python Lambda code for renaming a clusterised database.
│   │   └── rename_function.py                   <-- Python Lambda code for renaming a non-clusterised RDS instance.
│   ├── restore
│   │   ├── cluster_restore_function.py          <-- Python Lambda code for retoring a clusterised database.
│   │   └── restore_function.py                  <-- Python Lambda code for restoring a non-clusterised RDS instance
│   ├── slackNotification
│   │   └── slack_notification.py                <-- Python Lambda code for sending out a failure alert to configured webhook(s) on Slack.
│   └── snapshot
│       ├── cluster_snapshot_function.py         <-- Python Lambda code for creating a snapshot of a clusterised database.
│       └── snapshot_function.py                 <-- Python Lambda code for creating a snapshot of a non-clusterised RDS instance.
├── template.yaml                                <-- SAM template definition for the entire state machine.
└── tests                                        <-- Test folder.
    └── unit
        ├── mock_constants.py
        ├── mock_custom_exceptions.py
        ├── mock_import.py
        ├── mock_utility.py
        ├── test_cluster_delete_function.py
        ├── test_cluster_rename_function.py
        ├── test_cluster_restore_function.py
        ├── test_cluster_snapshot_function.py
        ├── test_delete_function.py
        ├── test_email_function.py
        ├── test_get_dbcluster_status_function.py
        ├── test_get_dbstatus_function.py
        ├── test_rename_function.py
        ├── test_restore_function.py
        ├── test_slack_notification.py
        └── test_snapshot_function.py

```

## Pre-Requisites

The app requires the following AWS resources to exist before installation:

1. `python3.7` installed on local machine following [this](https://www.python.org/downloads/). 

2. Have `sam` installed in the local machine. Can be installed following the [Installing the AWS SAM CLI](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) documentation.

3. Configure [AWS SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/event-publishing-create-configuration-set.html)
    - Configure the SES sender and receiver email ([SES Console](https://console.aws.amazon.com/ses/)->Email Addresses). 
        - An SES email alert is configured to notify the user about any failures in the state machine. The sender email parameter is needed to configure the email ID through which the alert is sent out. The receiver email parameter is needed to set the email ID to which the alert is sent.
        
4. Create the S3 bucket where the system is going to store the cloud formation templates:
    - Proposed Name: trapheus-cfn-s3-[account-id]-[region]. It is recommended that the name contains your:
        - account-id, as the bucket names need to be global (prevents someone else having the same name)
        - region, to easily keep track when you have trapheus-s3 buckets in multiple regions

5. A VPC (region specific). The same VPC/region should be used for both the RDS instance(s), to be used in Trapheus, and Trapheus' lambdas.  
    - Region selection consideration. Regions that support:
        - [Email receiving](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/regions.html#region-receive-email) . Check [Parameters](#parameters) -> 'RecipientEmail' for more.
    - Example minimal VPC setup:  
        - VPC console: 
            - name: Trapheus-VPC-[region] (specify the [region] where you VPC is created - to easily keep track when you have Trapheus-VPCs in multiple regions) 
            - [IPv4 CIDR block](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html#vpc-sizing-ipv4): 10.0.0.0/16
        - VPC console->Subnets page and create two private subnets:
            - Subnet1: 
                - VPC: Trapheus-VPC-[region]
                - Availability Zone: choose one
                - IPv4 CIDR block: 10.0.0.0/19
            - Subnet2: 
                - VPC: Trapheus-VPC-[region]
                - Availability Zone: choose a different one than the Subnet1 AZ.
                - IPv4 CIDR block: 10.0.32.0/19
        - You have created a VPC with only two private subnets. If you are creating non-private subnets, check [the ratio between private, public subnets, private subnet with dedicated custom network ACL and spare capacity](https://docs.aws.amazon.com/quickstart/latest/vpc/architecture.html). 

6. One or more instances of an RDS database that you wish to restore.
    - Example minimal *free* RDS setup:
        - Engine options: MySQL
        - Templates: Free tier
        - Settings: enter password
        - Connectivity: VPC: Trapheus-VPC-[region]
        

## Parameters

The following are the parameters for creating the cloudformation template:

1. `--s3-bucket` : [Optional] The name of the CloudFormation template S3 bucket from the [Pre-Requisites](#pre-requisites). 
2. `vpcID` : [Required] The id of the VPC from the [Pre-Requisites](#pre-requisites). The lambdas from the Trapheus state machine will be created in this VPC. 
3. `Subnets` : [Required] A comma separated list of private subnet ids (region specific) from the [Pre-Requisites](#pre-requisites) VPC.
4. `SenderEmail` : [Required] The SES sending email configured in the [Pre-Requisites](#pre-requisites)
5. `RecipientEmail` : [Required] Comma separated list of recipient email addresses configured in [Pre-Requisites](#pre-requisites).
6. `UseVPCAndSubnets` : [Optional] Whether to use the vpc and subnets to create a security group and link the security group and vpc to the lambdas. When UseVPCAndSubnets left out (default) or set to 'true', lambdas are connected to a VPC in your account, and by default the function can't access the RDS (or other services) if VPC doesn't provide access (either by routing outbound traffic to a [NAT gateway](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html) in a public subnet, or having a [VPC endpoint](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints.html), both of which incur cost or require more setup). If set to 'false', the [lambdas will run in a default Lambda owned VPC that has access to RDS (and other AWS services)](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html#vpc-internet).
7. `SlackWebhookUrls` : [Optional] Comma separated list of Slack webhooks for failure alerts.

## Instructions

### Setup

#### To setup the Trapheus in your AWS account, follow the steps below:

1. Clone the Trapheus Git repository
2. From the Trapheus repo execute:  
`sam package --template-file template.yaml --output-template-file deploy.yaml --s3-bucket <s3 bucket name from corresponding AWS account and region>`
3. To deploy the stack using the above mentioned parameters execute:   
`sam deploy --template-file deploy.yaml --stack-name <user-defined-stack-name> --region <aws region> --capabilities CAPABILITY_NAMED_IAM --parameter-overrides vpcId=<vpcID> Subnets=<Subnets> SenderEmail=<SenderEmail> RecipientEmail=<RecipientEmail>`  
  3.1. In order to have the minimal Lambda-RDS access configuration and less costs ([UseVPCAndSubnets description above](#parameters) for more), add the `UseVPCAndSubnets=false` at the end of the sam deploy command or:  
`sam deploy --template-file deploy.yaml --stack-name <user-defined-stack-name> --region <aws region> --capabilities CAPABILITY_NAMED_IAM --parameter-overrides vpcId=<vpcID> Subnets=<Subnets> SenderEmail=<SenderEmail> RecipientEmail=<RecipientEmail> UseVPCAndSubnets=false`  
Typically, linking your own VPC to the lambdas and not setting addition NAT gateway or VPC endpoint configuration will result in a ["Connect timeout on endpoint URL: "https://rds.[region].amazonaws.com/"" or "Task timed out after 3.00 seconds" issue](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting-networking.html).  
  3.2. <a name="slack-setup"></a>[Optional] To add Slack notification for failure alerts, add the parameter `SlackWebhookUrls` to the end of the deploy command like so:  
`sam deploy --template-file deploy.yaml --stack-name <user-defined-stack-name> --region <aws region> --capabilities CAPABILITY_NAMED_IAM --parameter-overrides vpcId=<vpcID> Subnets=<Subnets> SenderEmail=<SenderEmail> RecipientEmail=<RecipientEmail> --SlackWebhookUrls=<comma-separated-slack-webhook-urls>`  
More information about setting up Slack webhooks can be found [here](https://api.slack.com/messaging/webhooks)

#### To set up the step function execution through a scheduled run using CloudWatch rule, follow the steps below:

1. Go to DBRestoreStateMachineEventRule section in the template.yaml of the Trapheus repo.
2. We have set it as a scheduled cron rule to run every FRIDAY at 8:00 AM UTC. You can change it to your preferred schedule frequency by updating the **ScheduleExpression** property's value accordingly. Examples:
    * To run it every 7 days,
        `ScheduleExpression: "rate(7 days)"`
    * To run it every FRIDAY at 8:00 AM UTC,
        `ScheduleExpression: "cron(0 8 ? * FRI *)"`
    
    Click [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html) for all details on how to set ScheduleExpression. 
3. Sample targets given in the template file under **Targets** property for your reference has to be updated:
    
    a. Change **Input** property according to your Input property values, accordingly give a better ID for your target by updating the **Id** property.
    
    b. Based on the number of targets for which you want to set the schedule, add or remove the targets.
4. Change the **State** property value to **ENABLED**
5. Lastly, package and redeploy the stack following steps 2 and 3 in [Trapheus setup](#to-setup-the-trapheus-in-your-aws-account-follow-the-steps-below)

**TO BE NOTED**:
The CFT creates the following resources: 
1. **DBRestoreStateMachine** Step function state machine
2. Multiple lambdas to execute various steps in the state machine
3. LambdaExecutionRole: used across all lambdas to perform multiple tasks across RDS
4. StatesExecutionRole: IAM role with permissions for executing the state machine and invoking lambdas
5. S3 bucket: rds-snapshots-<your_account_id> where snapshots will be exported to
6. KMS key: is required to start export task of snapshot to s3
7. DBRestoreStateMachineEventRule: A Cloudwatch rule in disabled state, that can be used following above [instructions](#to-set-up-the-step-function-execution-through-a-scheduled-run-using-cloudwatch-rule-follow-the-steps-below) based on user requirement
8. CWEventStatesExecutionRole: IAM role used by DBRestoreStateMachineEventRule CloudWatch rule, to allow execution of the state machine from CloudWatch

## Execution

To execute the step function, follow the steps below:
1. Navigate to the State machine definition from the *Resources* tab in the cloudformation stack.
2. Click on *Start Execution*.
3. Under *Input*, provide the following json as parameter:
```
{
    "identifier": "<identifier name>",
    "task": "<taskname>",
    "isCluster": true or false
}
```
   a. `identifier`: (Required - String) The RDS instance or cluster identifier that has to be restored. Any type of RDS instance or Amazon aurora clusters are supported in this.
   
   b. `task`: (Required - String) Valid options are `create_snapshot` or `db_restore`.
  
   c. `isCluster`: (Required - Boolean) Set to `true` if the identifier provided is of a cluster else set to `false`
 
The state machine can do one of the following tasks:
1. if `task` is set to `create_snapshot`, the state machine creates/updates a snapshot for the given RDS instance or cluster using the snapshot identifier: *identifier*-snapshot and then executes the pipeline
2. if `task` is set to `db_restore`, the state machine does a restore on the given RDS instance, without updating a snapshot, assuming there is an existing snapshot with an identifier: *identifier*-snapshot

**Cost considerations**

After done with development or using the tool:  

1. if you don't need the RDS instance when not coding or using the tool (for instance, if it is a test RDS), consider stopping or deleting the database. You can always recreate it when you need it.
2. if you don't need the past Cloud Formation templates, it is recommended you empty the CFN S3 bucket.

**Tear down**

To tear down your application and remove all resources associated with the Trapheus DB Restore state machine, follow these steps:

1. Log into the [Amazon CloudFormation Console](https://console.aws.amazon.com/cloudformation/home?#) and find the stack you created.
2. Delete the stack. Note that stack deletion will fail if rds-snapshots-<YOUR_ACCOUNT_NO> s3 bucket is not empty, so first delete the snapshots' exports in the bucket.
3. Delete the AWS resources from the [Pre-Requisites](#pre-requisites). Removal of SES, the CFN S3 bucket (empty it if not deleting) and VPC is optional as you won't see charges, but can re-use them later for a quick start.

## How it Works

**Complete Pipeline**

![DBRestore depiction](screenshots/restore_state_machine.png)

Modelled as a state machine, different steps in the flow such as snapshot creation/updation, instance rename, restore and deletion, completion/failure status of each operation, failure email alert, etc. are executed using individual lambdas for db instances and db clusters respectively.
To track completion/failure of each operation, RDS waiters are used with delays and maximum retry attempts configured based on the lambda timeout. For scenarios of DB cluster availability and deletion, custom waiters have been defined.
Lambda layers are used across all lambdas for common utility methods and custom exception handling.

Based on the input provided to the **DBRestoreStateMachine** step function, the following steps/branches are executed:

1. Using the `isCluster` value, a branching takes place in the state machine to execute the pipeline for a db cluster or for a db instance.

2. If `task` is set to `create_snapshot`, the **snapshot creation/updation** process takes place for a cluster or instance respectively.
Creates a snapshot using the unique identifier: *identifier*-snapshot, if it does not exist. If a snapshot already exists with the aforementioned identifier, it is deleted and a new snapshot is created.

3. If `task` is set to `db_restore`, the db restoration process starts, without a snapshot creation/updation

4. As part of the db restoration process, the first step is a **Rename** of the provided db instance or db cluster and its corresponding instances to a temporary name.
Wait for successful completion of the rename step to be able to use the provided unique `identifier` in the restoration step.

5. Once the rename step is complete, next step is to **Restore** the db-instance or db-cluster using the `identifier` parameter and the snapshot id as *identifier*-snapshot

6. Once the restore is complete and the db-instance or db-cluster is available, the final step is to **Delete** the initially renamed instance or cluster (along with its instances) which was retained for failure handling purposes.
Executed using lambdas created for deletion purposes, once the deletion is successful, the pipeline is complete.

7. At any step, the retries with backoff and failure alerts are handled in every step of the state machine. If there is an occurrence of a failure, an SES email alert is sent as configured during the setup. Optionally, if `SlackWebhookUrls` was provided in the [setup](#slack-setup), failure notifications will also be sent to the appropriate channels.

8. If the restore step fails, as part of failure handling, the **Step-4** of instance/cluster rename is reverted to ensure that the original db-instance or db cluster is available for use.

![DBRestore failure handling depiction](screenshots/failure_handling.png)


## Contributing to Trapheus

Prepare your environment. Install tools as needed.

* [Git Bash](https://gitforwindows.org/) used to run Git from Command Line.
* [Github Desktop](https://desktop.github.com/) Git desktop tool for managing pull requests, branches and repos.
* [Visual Studio Code](https://code.visualstudio.com/) Full visual editor. Extensions for GitHub can be added.
* Or an editor of your choice.


1. Fork Trapheus repo
1. Create a working branch.
    ```bash
    git branch trapheus-change1
    ```
1. Confirm working branch for changes.
   ```bash
    git checkout trapheus-change1
   ```
    You can combine both commands by typing `git checkout -b trapheus-change1`.
1. Make changes locally using an editor and add unit tests as needed.
1. Run the test suite in the repo to ensure existing flows are not breaking.
    ```bash
       cd Trapheus
       python -m pytest tests/ -v #to execute the complete test suite
       python -m pytest tests/unit/test_get_dbstatus_function.py -v #to execute any individual test
    ```
1. Stage edited files.
   ```bash
      git add contentfile.md 
    ```
    Or use `git add . ` for multiple files.

1. Commit changes from staging.
    ```bash
       git commit -m "trapheus-change1"
    ```
1. Push new changes to GitHub
    ```bash
       git push --set-upstream origin trapheus-change1
    ```
1. Verify status of branch
    ```bash
    git status
    ```
    Review `Output` to confirm commit status.


1. Git push
    ```bash
        git push --set-upstream origin trapheus-change1
    ```

1. The `Output` will provide a link to create your Pull Request.
