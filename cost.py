import boto3
import datetime
import json
import os
import requests

ce = boto3.client('ce')
s3 = boto3.client('s3')
ses = boto3.client('ses')

S3_BUCKET = os.environ['S3_BUCKET']
SLACK_WEBHOOK = os.environ['SLACK_WEBHOOK']
EMAIL_SENDER = os.environ['EMAIL_SENDER']
EMAIL_RECEIVER = os.environ['EMAIL_RECEIVER']

def lambda_handler(event, context):

    today = datetime.date.today()
    start = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
    end = today.replace(day=1)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    report_data = []
    total_cost = 0

    for group in response['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])

        report_data.append({
            "service": service,
            "cost": round(cost, 2)
        })

        total_cost += cost

    report = {
        "month": start.strftime('%B %Y'),
        "total_cost": round(total_cost, 2),
        "services": report_data
    }

    report_text = f"AWS Monthly Cost Report ({report['month']})\n\n"

    for item in report_data:
        report_text += f"{item['service']}: ${item['cost']}\n"

    report_text += f"\nTotal Cost: ${round(total_cost,2)}"

    # Upload report to S3
    s3_key = f"cost-reports/{start.strftime('%Y-%m')}-report.json"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=json.dumps(report),
        ContentType="application/json"
    )

    anomaly = False
    if total_cost > 1000:  
        anomaly = True

    # Slack notification
    slack_message = {
        "text": f"*AWS Monthly Cost Report*\nTotal Cost: ${round(total_cost,2)}"
    }

    if anomaly:
        slack_message["text"] += "\n⚠️ Cost anomaly detected!"

    requests.post(SLACK_WEBHOOK, json=slack_message)

    # Send Email via SES
    ses.send_email(
        Source=EMAIL_SENDER,
        Destination={
            'ToAddresses': [EMAIL_RECEIVER]
        },
        Message={
            'Subject': {
                'Data': 'AWS Monthly Cost Report'
            },
            'Body': {
                'Text': {
                    'Data': report_text
                }
            }
        }
    )

    return {
        "status": "Report generated",
        "s3_location": f"s3://{S3_BUCKET}/{s3_key}"
    }
