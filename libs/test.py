from minio import Minio
import json
client = Minio('192.168.1.5:9000', access_key='S3OWAIS', secret_key='S3SECRET', secure=False)
client.delete_bucket_policy("123")
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
            ],
            "Resource": "arn:aws:s3:::123",
        },
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload",
            ],
            "Resource": "arn:aws:s3:::123/static/images/*",
        },
    ],
}
client.set_bucket_policy("123", json.dumps(policy))
print(client.get_bucket_policy('123'))
