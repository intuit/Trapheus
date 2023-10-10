#!/usr/bin/env python3

import subprocess


def main():
    package_command_list = ['sam', 'package', '--template-file', 'template.yaml', '--output-template-file', 'deploy.yaml']
    deploy_command_list = ['sam', 'deploy', '--template-file', 'deploy.yaml', '--capabilities', 'CAPABILITY_NAMED_IAM']
    s3_bucket = input('Enter the s3 bucket name created as part of pre-requisite: ')
    if s3_bucket:
        package_command_list.append('--s3-bucket')
        package_command_list.append(s3_bucket)
    region = input('Enter the region [for instance, us-west-2]: ')
    if region:
        package_command_list.append('--region')
        package_command_list.append(region)

        deploy_command_list.append('--region')
        deploy_command_list.append(region)
        print()
        print ('packaging trapheus for use ...')
        try:
            subprocess.run(package_command_list, shell=False, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')


    stack_name = input('Enter a stack name: ')
    if stack_name:
        deploy_command_list.append('--stack-name')
        deploy_command_list.append(stack_name)
        deploy_command_list.append('--parameter-overrides')
    sender_email = input('Enter sender email to send email FROM in case of failure: ')
    if sender_email:
        deploy_command_list.append('SenderEmail=' + sender_email)
    recipient_email = input('Enter recipeint email to send email TO in case of failure: ')
    if recipient_email:
        deploy_command_list.append('RecipientEmail=' + recipient_email)
    slack_webhook_urls = input('Enter slack webhooks to publish failure notifications to: ')
    if slack_webhook_urls:
        deploy_command_list.append('--SlackWebhookUrls=' + slack_webhook_urls)
    vpc = input('Are ypu using vpc[y/n]: ')
    if vpc == 'y' or vpc == 'Y':
        deploy_command_list.append('UseVPCAndSubnets=true')
        vpc_id = input('Enter vpc ID: ')
        if vpc_id:
            deploy_command_list.append('vpcId=' + vpc_id)
            subnets = input('Enter comman seperated list of PRIVATE subnets: ')
            if subnets:
                deploy_command_list.append('Subnets=' +subnets)
    print()
    print('Deploying trapheus to AWS ...')
    try:
        subprocess.run(deploy_command_list, shell=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')


if __name__ == "__main__":
    main()
