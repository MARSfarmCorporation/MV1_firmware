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
    List all image names in an S3 bucket with an optional prefix and strip the prefix and leading slashes from the image names.

    :param bucket_name: The name of the S3 bucket.
    :param prefix: The prefix to filter objects in the bucket.
    :return: A list of image names in the S3 bucket with the prefix and leading slashes stripped.
    """
    s3 = boto3.client('s3')
    image_names = []
    
    # Pagination to handle large lists of objects
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                # Strip the prefix from the image name
                stripped_key = obj['Key'][len(prefix):] if obj['Key'].startswith(prefix) else obj['Key']
                # Remove any leading slashes from the stripped key
                stripped_key = stripped_key.lstrip('/')
                image_names.append(stripped_key)
    
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

def upload_images_to_s3(images_to_upload):
    """
    Upload images to an S3 bucket with an additional prefix and metadata.

    :param images_to_upload: List of image names to upload.
    """
    s3 = boto3.resource('s3')
    for image_name in images_to_upload:
        try:
            file_path = os.path.join(IMAGE_DIR, image_name)
            with open(file_path, 'rb') as data:
                s3_path = f"Backups/{image_name}"
                # Remove the .jpg extension from the image name for currtime metadata
                currtime = os.path.splitext(image_name)[0]
                s3.Bucket(S3_BUCKET).put_object(
                    Key=s3_path,
                    Body=data,
                    Metadata={
                        'device_id': DEVICE_ID,
                        'currtime': currtime
                    }
                )
                print(f"Uploaded {image_name} to {s3_path} with device_id {DEVICE_ID}")
        except Exception as e:
            print(f"Failed to upload {image_name} due to {e}")

if __name__ == "__main__":
    bucket_name = S3_BUCKET  # Replace with your S3 bucket name
    prefix = DEVICE_ID  # Replace with your prefix if needed
    
    # Get lists of image names
    S3_image_name_list = list_images_in_s3(bucket_name, prefix)
    local_image_name_list = list_local_image_names()
    
    # Compare lists
    images_to_upload = compare_image_lists(local_image_name_list, S3_image_name_list)
    
    # Upload images
    upload_images_to_s3(images_to_upload)
