import json
import boto3

def lambda_handler(event, context):
    # Configuration
    bucket_name = "wordcounttester3"
    topic_arn = "arn:aws:sns:us-west-2:802768592020:WordCountAlerts"
    
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        
        # Get list of objects and find the most recent one
        objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        if not objects:
            return {
                'statusCode': 200,
                'body': json.dumps('No files found in the bucket')
            }
            
        # Find the most recently modified file
        latest_file = max(objects, key=lambda x: x['LastModified'])
        filename = latest_file['Key']
        
        # Get file content and count words
        file_obj = s3.get_object(Bucket=bucket_name, Key=filename)
        word_count = len(file_obj["Body"].read().decode("utf-8").split())
        
        # Print result (goes to CloudWatch logs)
        print(f"Word count in {filename}: {word_count}")
        
        # Send SNS notification
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=topic_arn,
            Message=f"The word count in {filename} is {word_count}",
            Subject="Word Count Result"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Processed {filename} with {word_count} words")
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }