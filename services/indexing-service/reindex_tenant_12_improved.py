import boto3
import json
import time

sqs = boto3.client('sqs', region_name='ap-south-1')

print("="*70)
print("🔄 REINDEXING TENANT 12 WITH IMPROVED CHUNKING")
print("="*70)
print("\nChanges:")
print("  - Chunk size: 1000 → 1500 characters")
print("  - Chunk overlap: 150 → 300 characters")
print("  - Retrieval: 8 → 12 documents")
print("\nThis should improve answer quality for complex queries.")
print("\n" + "="*70)

print("\n📤 Sending SQS message...")

response = sqs.send_message(
    QueueUrl='https://sqs.ap-south-1.amazonaws.com/068733247141/RagLambdaIndexing.fifo',
    MessageBody=json.dumps({'tenant_id': 12}),
    MessageGroupId='improved-chunking',
    MessageDeduplicationId=f'improved-{int(time.time())}'
)

print(f"✅ Message sent: {response['MessageId']}")
print(f"\n⏳ Waiting 60 seconds for Lambda to complete indexing...")
print("   (Larger chunks take slightly longer to process)")

time.sleep(60)

print("\n✅ Reindexing should be complete!")
print("\nNext steps:")
print("1. Restart your API server to pick up the retrieval changes")
print("2. Test the queries again")
print("3. You should see better answers for complex questions")
