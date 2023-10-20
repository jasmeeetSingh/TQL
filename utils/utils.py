import pandas as pd
from google.cloud import storage

def get_spider_schema_table_files():
    
    spider_query = pd.read_csv("gs://data_tql/spider/processed/spiderQueryData.csv")
    spider_schema = pd.read_csv("gs://data_tql/spider/processed/Schemas/tablesSchemaSpider.csv")
    
    return spider_query, spider_schema

def list_blobs(bucket_name, folder_name):
    """List all files in given COS directory."""    
    blob_names = []
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))
    for blob in blobs:
        blob_names.append(blob.name)
    return blob_names
    
def list_blobs_pd(bucket_name, folder_name):
    """List all files in given COS directory."""       
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=folder_name))

    blob_name = []
    blob_size = []
    blob_time = []
    
    for blob in blobs:
        blob_name.append(blob.name)
        blob_size.append(blob.size)
        blob_time.append(blob.time_created)

    blobs_df = pd.DataFrame(list(zip(blob_name, blob_size, blob_time)), columns=['filePath', 'size', 'timeStamp'])    
    return blobs_df

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from COS bucket."""
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""    
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)