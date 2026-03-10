# AWS_Cost_Report
This architecture automatically collects AWS cost data every month, analyzes it, detects anomalies, generates reports, stores them in S3, and sends notifications to Slack and email for stakeholders.

Also , we need IAM role for lambda .In that we can specify the permission , like this
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": ""
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}

Pass the values in lambda 
S3_BUCKET = 
SLACK_WEBHOOK = 
EMAIL_SENDER = 
EMAIL_RECEIVER = 

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/50c2b7ba-3624-4ba4-a881-72cf47825918" />
