import boto3
from datetime import datetime

bucket_name = 'crimson-db-backups'
client = boto3.client('s3')
resource = boto3.resource('s3')
bucket = resource.Bucket(bucket_name)

backup_name_prefix = 'crimson_db'

data = open('app.db', 'rb')
try:
    resource.meta.client.copy(
        {
            'Key': f"{backup_name_prefix}_current.db",
            'Bucket': bucket_name,
        },
        bucket_name,
        f"{backup_name_prefix}_yesterday.db",
    )
    # client.copy_object(Key=f"{backup_name_prefix}_yesterday.db", CopySource=f"{backup_name_prefix}_current.db")
except:
    pass

bucket.put_object(Key=f"{backup_name_prefix}_current.db", Body=data)
date_str = datetime.now().strftime("%Y-%m-%d")
# client.copy_object(Key=f"{backup_name_prefix}_{date_str}.db", CopySource=f"{backup_name_prefix}_current.db", Bucket=bucket_name)
resource.meta.client.copy(
    {
        'Key': f"{backup_name_prefix}_current.db",
        'Bucket': bucket_name,
    },
    bucket_name,
    f"{backup_name_prefix}_{date_str}.db",
)