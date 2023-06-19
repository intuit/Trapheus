import boto3
from datetime import datetime, timedelta
import time
from sklearn.linear_model import LinearRegression

#method to execute a linear regression
def simple_linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_squared = sum([xi * xi for xi in x])
    sum_xy = sum([xi * yi for xi, yi in zip(x, y)])

    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n

    return slope, intercept

"""
The code retrieves CPUUtilization metric from Amazon cloudwatch for a specified RDS instance, and trains a linear 
regression model on the CPU data to predict the optimal time to take a snapshot.This assumes we have historical database
with a cpu usage pattern and the trained model predicts the optimal time for the next snapshot to be taken based on the 
pattern
"""
def lambda_handler(event, context):
    client = boto3.client('cloudwatch')
    response = client.get_metric_statistics(
        Namespace='AWS/RDS',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'DBInstanceIdentifier',
                'Value': 'database-1'
            }
        ],
        StartTime=int(time.time() - 3600),
        EndTime=int(time.time()),
        Period=60,
        Statistics=['Average']
    )
    data = []
    for data_point in response['Datapoints']:
        data.append({
            'timestamp': data_point['Timestamp'],
            'cpu_usage': data_point['Average']
        })
    # Train a simple linear regression model on the CPU data
    timestamps = [int(data_point['timestamp'].timestamp()) for data_point in data]
    cpu_usages = [data_point['cpu_usage'] for data_point in data]
    slope, intercept = simple_linear_regression(timestamps, cpu_usages)

    # Predict the optimal time to take a snapshot using Trapheus
    current_timestamp = int(time.time())
    predicted_cpu_usage = slope * current_timestamp + intercept
    print(f"Predicted CPU usage at current time: {predicted_cpu_usage}")

    # Find the next timestamp with lower predicted CPU usage
    while True:
        current_timestamp += 60  # Check every minute
        predicted_cpu_usage = slope * current_timestamp + intercept
        if predicted_cpu_usage < 0.8:  # Adjust this threshold based on your requirements
            break

    optimal_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_timestamp))
    print(f"Optimal time to take a snapshot: {optimal_time}")
