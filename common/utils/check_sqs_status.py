#!/usr/bin/env python3
"""
Check SQS queue status and send test message
"""
import boto3
import json
import uuid
from datetime import datetime

QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/068733247141/RagLambdaIndexing.fifo"
REGION = "ap-south-1"

sqs = boto3.client('sqs', region_name=REGION)

print("=" * 80)
print("SQS QUEUE STATUS CHECK")
print("=" * 80)
print(f"Queue: {QUEUE_URL}")
print(f"Region: {REGION}")
print()

# Get queue attributes
try:
    response = sqs.get_queue_attributes(
        QueueUrl=QUEUE_URL,
        AttributeNames=['All']
    )
    
    attrs = response['Attributes']
    print("📊 Queue Statistics:")
    print(f"   Messages Available: {attrs.get('ApproximateNumberOfMessages', 0)}")
    print(f"   Messages In Flight: {attrs.get('ApproximateNumberOfMessagesNotVisible', 0)}")
    print(f"   Messages Delayed: {attrs.get('ApproximateNumberOfMessagesDelayed', 0)}")
    print()
    
    total_messages = int(attrs.get('ApproximateNumberOfMessages', 0))
    
    if total_messages > 0:
        print(f"⚠️  WARNING: {total_messages} messages waiting in queue!")
        print("   These messages are NOT being processed by Lambda")
        print("   → Lambda trigger is NOT configured")
        print()
    else:
        print("✅ Queue is empty (all messages processed)")
        print()
    
except Exception as e:
    print(f"❌ Error checking queue: {e}")
    print()

# Send test message
print("=" * 80)
print("SENDING TEST MESSAGE")
print("=" * 80)

try:
    test_tenant_id = 11
    message_body = json.dumps({"tenant_id": test_tenant_id})
    
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=message_body,
        MessageGroupId="reindexing",
        MessageDeduplicationId=f"test-{uuid.uuid4()}"
    )
    
    print(f"✅ Test message sent successfully!")
    print(f"   Tenant ID: {test_tenant_id}")
    print(f"   Message ID: {response['MessageId']}")
    print()
    print("📋 Next Steps:")
    print("   1. Wait 1-2 minutes")
    print("   2. Check CloudWatch logs for Lambda function")
    print("   3. If no logs appear → Lambda trigger NOT configured")
    print("   4. If logs appear → Lambda trigger working! ✅")
    print()
    
except Exception as e:
    print(f"❌ Error sending message: {e}")
    print()

print("=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
