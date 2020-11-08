try:
    import unzip_requirements
except ImportError:
    pass

import os
import io
import json
import base64
import boto3
import torch
import torchvision
from torchvision import transforms
from PIL import Image
from requests_toolbelt.multipart import decoder

from class_name import class_name

model = torch.load('mobilenetv2.pt',map_location=torch.device('cpu'))

def transform_image(image_bytes):
    """Apply transformations to an input image."""
    try:
        transformations = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        image = Image.open(io.BytesIO(image_bytes))
        return transformations(image).unsqueeze(0)
    except Exception as e:
        print(repr(e))
        raise(e)


def get_prediction(image_bytes):
    """Get predictions for an image."""
    tensor = transform_image(image_bytes)
    print('Picture transformed')
    return model(tensor).argmax().item()


def classify_image(event, context):
    """Take input image from API and classify it."""
    print("Executing classify_image")
    try:
        # Get image from the request
        print("requesting")
        print(event)
        content_type_header = event['headers']['Content-Type']
        print("content_type_header loaded")
        body = base64.b64decode(event['body'])
        print('Body loaded')

        # Obtain the final picture that will be used by the model
        picture = decoder.MultipartDecoder(body, content_type_header).parts[0]
        print('Picture obtained')
        
        # print("picture",dir(picture))

        # Get predictions
        prediction = get_prediction(image_bytes=picture.content)
        prediction_name = class_name[prediction]
        print(f'Prediction: {prediction}\tPrediction Name: {prediction_name}')

       
        return {
            'statusCode': 200,
            'body': json.dumps({
                'predicted': prediction,
                'predicted name': prediction_name
            })
        }
    except Exception as e:
        print(repr(e))
        return {
            'statusCode': 500,  
            'body': json.dumps({'error': repr(e)})
        }
