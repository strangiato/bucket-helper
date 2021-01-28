"""Application used for managing and configuring s3 buckets."""

import json
import logging
import sys

import boto3

import botocore

from config import AppConfig

from dotenv import load_dotenv

import environ

# load environment and assign it to the environ config
load_dotenv()
app_cfg = environ.to_config(AppConfig)

# setup logging
logger = logging.getLogger(__name__)

logger.setLevel(app_cfg.log.level)
formatter = logging.Formatter(app_cfg.log.formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def create_bucket(s3, bucket_name):
    """Create the bucket and return the bucket object."""
    try:
        bucket = s3.create_bucket(Bucket=bucket_name)
        logger.info(f"Created bucket {bucket_name}")
    except Exception:
        logger.exception(
            f"Unable to create the bucket '{bucket_name}' on the S3 instance"
        )
        sys.exit(1)

    return bucket


def set_public_policy(s3, bucket):
    """Set the bucket read access to public."""
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AddPerm",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": ["arn:aws:s3:::{0}/*".format(bucket)],
            }
        ],
    }
    bucket_policy = json.dumps(bucket_policy)

    try:
        s3.put_bucket_policy(Bucket=bucket, Policy=bucket_policy)
        logger.info(f"Updated bucket policy to public for {bucket}")

    except Exception:
        logger.exception(f"Unable to set public policy to bucket {bucket}")
        sys.exit(1)

    return bucket_policy


def create_topic(sns, bucket, topic, push_endpoint=None):
    """Create a topic for the bucket and configure the push events."""
    attributes = {}
    if push_endpoint:
        attributes["push-endpoint"] = push_endpoint
        attributes["kafka-ack-level"] = "broker"

    try:
        topic_arn = sns.create_topic(Name=topic, Attributes=attributes)["TopicArn"]
        logger.info(f"Created topic {topic}")

    except Exception:
        logger.exception(f"Unable to create topic {topic}")
        sys.exit(1)

    bucket_notifications_configuration = {
        "TopicConfigurations": [
            {
                "Id": f"{topic}",
                "TopicArn": f"arn:aws:sns:s3a::{topic}",
                "Events": ["s3:ObjectCreated:*"],
            }
        ]
    }

    try:
        s3.put_bucket_notification_configuration(
            Bucket=bucket,
            NotificationConfiguration=bucket_notifications_configuration,
        )
        logger.info(
            f"Created notification for bucket {bucket} on topic {topic}"
        )

    except Exception:
        logger.exception(
            f"Unable to create notification for bucket {bucket} on topic {topic}"
        )
        sys.exit(1)

    return topic_arn


if __name__ == "__main__":

    logger.info(f"S3 endpoint URL: {app_cfg.s3.endpoint_url}")

    s3 = boto3.resource(
        "s3",
        endpoint_url=app_cfg.s3.endpoint_url,
        aws_access_key_id=app_cfg.s3.access_key,
        aws_secret_access_key=app_cfg.s3.secret_key,
        region_name="default",
        config=botocore.client.Config(signature_version="s3"),
    )

    bucket_name = app_cfg.s3.bucket.name

    bucket = create_bucket(s3, bucket_name)

    if app_cfg.s3.bucket.public:
        set_public_policy(s3, bucket_name)

    if app_cfg.s3.bucket.topic.name:

        sns = boto3.client(
            "sns",
            endpoint_url=app_cfg.s3.endpoint_url,
            aws_access_key_id=app_cfg.s3.access_key,
            aws_secret_access_key=app_cfg.s3.secret_key,
            region_name="default",
            config=botocore.client.Config(signature_version="s3"),
        )

        create_topic(
            sns,
            bucket_name,
            app_cfg.s3.bucket.topic,
            push_endpoint=app_cfg.s3.bucket.topic.push_endpoint,
        )
