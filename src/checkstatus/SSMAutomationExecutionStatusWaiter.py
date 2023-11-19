import botocore
import constants
import waiter_acceptor_config

def check_automation_execution_status(automation_execution_id, max_attempts, ssm):
    acceptor_config = waiter_acceptor_config.SSM_AUTOMATION_EXECUTION_COMPLETED
    model = botocore.waiter.WaiterModel({
        "version": 2,
        "waiters": {
            "SSMAutomationExecutionStatus": {
                "delay": constants.DELAY_INTERVAL,
                "operation": "GetAutomationExecution",
                "maxAttempts": max_attempts,
                "acceptors": acceptor_config
            }
        }
    })
    waiter = botocore.waiter.create_waiter_with_client('SSMAutomationExecutionStatus', model, ssm)
    try:
        waiter.wait(AutomationExecutionId = automation_execution_id)
    except botocore.exceptions.WaiterError as e:
        raise Exception(e)
