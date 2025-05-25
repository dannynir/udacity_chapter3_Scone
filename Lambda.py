import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

import json
#import sagemaker
import base64
import boto3
#from sagemaker.serializers import IdentitySerializer
#from sagemaker.predictor import Predictor

runtime_client = boto3.client('sagemaker-runtime')


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-05-25-00-42-45-651"

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    
    predictor = runtime_client.invoke_endpoint(
        EndpointName=ENDPOINT,
        Body=image,  # Must be raw bytes
        ContentType='image/png'
    )
    inferences = json.loads(predictor['Body'].read().decode('utf-8'))
        
    # We return the data back to the Step Function    
    event['body']["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': event
    }


import json

THRESHOLD = .8


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']['body']["inferences"]
    if isinstance(inferences, list):
        inferences = [float(inf) for inf in inferences]
    else:
        inferences = [float(inf) for inf in json.loads(inferences)]

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(float(pred) >= THRESHOLD for pred in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

