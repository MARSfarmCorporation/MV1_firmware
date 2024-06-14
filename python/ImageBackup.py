import os
import glob
import boto3
from Sys_Conf import DEVICE_ID, IMAGE_DIR, S3_BUCKET

# Gets the list of image names in the local directory for comparison
def list_local_image_names():

    local_image_names = []
    # Get a list of files in the specified directory
    list_of_files = glob.glob(IMAGE_DIR + '*')
    # Get the name of the file
    for file in list_of_files:
        local_image_names.append(os.path.basename(file))
    return local_image_names
    

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

def compare_image_lists(local_image_name_list, S3_image_name_list):
    """
    Compare local image names with S3 image names and return a list of images
    that exist locally but not in S3.

    :param local_image_name_list: List of local image names.
    :param S3_image_name_list: List of image names in S3.
    :return: List of image names that are local but not in S3.
    """
    # Convert S3_image_name_list to a set for faster lookups
    S3_image_name_set = set(S3_image_name_list)
    
    # List comprehension to get local images not in S3
    images_to_upload = [image for image in local_image_name_list if image not in S3_image_name_set]
    
    return images_to_upload

if __name__ == "__main__":
    bucket_name = S3_BUCKET  # Replace with your S3 bucket name
    prefix = DEVICE_ID  # Replace with your prefix if needed
    
    # Get lists of image names
    S3_image_name_list = list_images_in_s3(bucket_name, prefix)
    local_image_name_list = list_local_image_names()
    
    # Compare lists
    images_to_upload = compare_image_lists(local_image_name_list, S3_image_name_list)
    
    # Print result
    print(f"Images to upload ({len(images_to_upload)}):")
    for image in images_to_upload:
        print(image)