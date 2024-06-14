import os
import glob
import boto3
from Sys_Conf import DEVICE_ID, IMAGE_DIR, S3_BUCKET

def list_image_names():
    list_of_image_names = glob.glob(IMAGE_DIR + '*.jpg')
    return list_of_image_names

# Get the list of image names from the S3 bucket
def get_s3_image_names():
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET)
    s3_image_names = []
    for obj in bucket.objects.filter(Prefix=DEVICE_ID):
        s3_image_names.append(obj.key)
    return s3_image_names


def list_images_in_s3(bucket_name, prefix=''):
    """
    List all image names in an S3 bucket with an optional prefix.

    :param bucket_name: The name of the S3 bucket.
    :param prefix: The prefix to filter objects in the bucket.
    :return: A list of image names in the S3 bucket.
    """
    s3 = boto3.client('s3')
    image_names = []
    
    # Pagination to handle large lists of objects
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                image_names.append(obj['Key'])
    
    return image_names

if __name__ == "__main__":
    bucket_name = S3_BUCKET  # Replace with your S3 bucket name
    prefix = DEVICE_ID  # Replace with your prefix if needed
    image_names = list_images_in_s3(bucket_name, prefix)
    print(f"Found {len(image_names)} images in S3 bucket '{bucket_name}':")
    for image_name in image_names:
        print(image_name)