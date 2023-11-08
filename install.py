#!/usr/bin/env python3

import subprocess
import argparse

args = ["--s3bucket", "--region", "--stackname", "--senderemail", "--recipientemail", "--slackwebhooks", "--isvpc", "--vpcid", "--subnets"]
parser = argparse.ArgumentParser()
for arg in args:
    parser.add_argument(arg, default=None, required=False, nargs='?', const='')
cli_args = parser.parse_args()

def execute_subprocess(command_list):
    print(f'Executing command list: {command_list}')
    try:
        subprocess.run(command_list, shell=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        raise Exception(e)

def get_input(var_name, input_text):
    if arg_val := getattr(cli_args, var_name, None):
        return arg_val
    else:
        return input(input_text)

def main():
    package_command_list = ['sam', 'package', '--template-file', 'template.yaml', '--output-template-file', 'deploy.yaml']
    deploy_command_list = ['sam', 'deploy', '--template-file', 'deploy.yaml', '--capabilities', 'CAPABILITY_NAMED_IAM']
    s3_bucket = get_input('s3bucket','Enter the s3 bucket name created as part of pre-requisite: ')
    if s3_bucket:
        package_command_list.append('--s3-bucket')
        package_command_list.append(s3_bucket)
        # Adding parameter to solve the limitation:
        # Templates with a size greater than 51,200 bytes must be deployed via an S3 Bucket.
        # The local template will be copied to that S3 bucket and then deployed.
        deploy_command_list.append('--s3-bucket')
        deploy_command_list.append(s3_bucket)
    region = get_input('region','Enter the region [for instance, us-west-2]: ')
    if region:
        package_command_list.append('--region')
        package_command_list.append(region)

        deploy_command_list.append('--region')
        deploy_command_list.append(region)
        print()
        print ('packaging trapheus for use...')
        execute_subprocess(package_command_list)


    stack_name = get_input('stackname','Enter a stack name: ')
    if stack_name:
        deploy_command_list.append('--stack-name')
        deploy_command_list.append(stack_name)
        deploy_command_list.append('--parameter-overrides')
    sender_email = get_input('senderemail','Enter sender email to send email FROM in case of failure: ')
    if sender_email:
        deploy_command_list.append('SenderEmail=' + sender_email)
    recipient_email = get_input('recipientemail','Enter recipient email to send email TO in case of failure: ')
    if recipient_email:
        deploy_command_list.append('RecipientEmail=' + recipient_email)
    slack_webhook_urls = get_input('slackwebhooks','Enter slack webhooks to publish failure notifications to: ')
    if slack_webhook_urls:
        deploy_command_list.append('--SlackWebhookUrls=' + slack_webhook_urls)
    vpc = get_input('isvpc','Are ypu using vpc[y/n]: ')
    if vpc == 'y' or vpc == 'Y':
        deploy_command_list.append('UseVPCAndSubnets=true')
        vpc_id = get_input('vpcid','Enter vpc ID: ')
        if vpc_id:
            deploy_command_list.append('vpcId=' + vpc_id)
            subnets = get_input('subnets','Enter comma seperated list of PRIVATE subnets: ')
            if subnets:
                deploy_command_list.append('Subnets=' +subnets)
    print()
    print('Deploying trapheus to AWS...')
    execute_subprocess(deploy_command_list)


if __name__ == "__main__":
    main()
