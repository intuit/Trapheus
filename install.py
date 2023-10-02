#!/usr/bin/env python3

# import os
import subprocess


def main():
    package_command = 'sam package --template-file template.yaml --output-template-file deploy.yaml'
    deploy_command = 'sam deploy --template-file deploy.yaml --capabilities CAPABILITY_NAMED_IAM '
    s3_bucket = input('Enter the s3 bucket name created as part of pre-requisite: ')
    if s3_bucket:
        package_command = package_command + ' --s3-bucket ' + s3_bucket
    region = input('Enter the region [for instance, us-west-2]: ')
    if region:
        package_command = package_command + ' --region ' + region
        deploy_command = deploy_command + ' --region ' + region
        print()
        print ('packaging trapheus for use ...')
        try:
            subprocess.run(package_command, shell=False, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')


    stack_name = input('Enter a stack name: ')
    if stack_name:
        deploy_command = deploy_command + ' --stack-name ' + stack_name
    deploy_command = deploy_command + ' --parameter-overrides'
    sender_email = input('Enter sender email to send email FROM in case of failure: ')
    if sender_email:
        deploy_command = deploy_command + ' SenderEmail=' + sender_email
    recipient_email = input('Enter recipeint email to send email TO in case of failure: ')
    if recipient_email:
        deploy_command = deploy_command + ' RecipientEmail=' + recipient_email
    slack_webhook_urls = input('Enter slack webhooks to publish failure notifications to: ')
    if slack_webhook_urls:
        deploy_command = deploy_command + ' --SlackWebhookUrls=' + slack_webhook_urls
    vpc = input('Are ypu using vpc[y/n]: ')
    if vpc == 'y' or vpc == 'Y':
        deploy_command = deploy_command + ' UseVPCAndSubnets=true'
        vpc_id = input('Enter vpc ID: ')
        if vpc_id:
            deploy_command = deploy_command + ' vpcId=' + vpc_id
            subnets = input('Enter comman seperated list of PRIVATE subnets: ')
            if subnets:
                deploy_command = deploy_command + ' Subnets=' +subnets
    print()
    print('Deploying trapheus to AWS ...')
    try:
        subprocess.run(deploy_command, shell=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')


if __name__ == "__main__":
    main()
