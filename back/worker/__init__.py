import json
import logging
import os
import pathlib
import shutil
from datetime import datetime

import cv2
import pika
import requests
from dotenv import load_dotenv
from minio import Minio
from sqlalchemy.orm import scoped_session

from back.database import SessionLocal
from back.models import Job


def run_worker():
    # logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    load_dotenv()

    WORKING_DIR = os.getenv("IMAGE_PROCESSING_WORKING_DIR")
    print(f"Working dir {WORKING_DIR}")
    pathlib.Path(WORKING_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize minio client
    print("Connecting to S3...")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_BUCKET_PROCESSING = os.getenv("S3_BUCKET_PROCESSING")
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key=S3_ACCESS_KEY,
        secret_key=S3_SECRET_KEY,
    )
    # Make 'image_processing' bucket if not exist.
    found = client.bucket_exists(S3_BUCKET_PROCESSING)
    if not found:
        client.make_bucket(S3_BUCKET_PROCESSING)
    else:
        print(f"Bucket {S3_BUCKET_PROCESSING} already exists")

    # Set bucket policy to allow download
    # Example anonymous read-only bucket policy.
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{S3_BUCKET_PROCESSING}",
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{S3_BUCKET_PROCESSING}/*",
            },
        ],
    }
    client.set_bucket_policy(S3_BUCKET_PROCESSING, json.dumps(policy))

    # Initialize RabbitMQ connection and channel
    print("Connecting to RabbitMQ...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # Declare exchange and queue
    channel.exchange_declare(exchange="image_processing", exchange_type="direct")
    channel.queue_declare(queue="image_processing")
    channel.queue_bind(queue="image_processing", exchange="image_processing")

    session = scoped_session(SessionLocal)

    def callback(ch, method, properties, body):
        message = json.loads(body)
        job_id = message["job_id"]

        print("Message received:", message)

        job = session.query(Job).get(job_id)
        job.status = "PROCESSING"
        job.started_at = datetime.utcnow()
        session.commit()
        print("Job", job)

        res = requests.get(job.image_url, stream=True)

        if res.status_code == 200:
            file_path = f"{WORKING_DIR}/{job.id}_original"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(res.raw, f)
            print(f"Image sucessfully downloaded: {file_path}")

            blur_kernel_size_x = job.process_params["blur_kernel_size_x"]
            blur_kernel_size_y = job.process_params["blur_kernel_size_y"]

            image = cv2.imread(file_path)
            blurred = cv2.blur(image, (blur_kernel_size_x, blur_kernel_size_y))
            processed_path = f"{WORKING_DIR}/{job.id}_processed.png"
            cv2.imwrite(processed_path, blurred)
            print(f"Image processed: {processed_path}")
            client.fput_object(
                S3_BUCKET_PROCESSING,
                f"{job.id}_processed.png",
                processed_path,
            )
            job.status = "COMPLETED"
            job.processed_image_s3 = f"{S3_BUCKET_PROCESSING}/{job_id}_processed.png"
            job.finished_at = datetime.utcnow()
            session.commit()
            print(f"Image uploaded: {job.processed_image_s3}")

        else:
            print("ERROR: Image couldn't be retrieved")

        # try:
        #     # Load the image and apply blurring
        #     image = cv2.imread(image_path)
        #     blurred = cv2.GaussianBlur(
        #         image,
        #         (blur_params["kernel_size"], blur_params["kernel_size"]),
        #         blur_params["sigma"],
        #     )
        #
        #     # Save the blurred image
        #     blurred_path = image_path[:-4] + "_blurred.jpg"
        #     cv2.imwrite(blurred_path, blurred)
        #
        #     # Publish result message to RabbitMQ exchange
        #     result = {
        #         "image_path": image_path,
        #         "blurred_path": blurred_path,
        #         "status": "success",
        #     }
        #     channel.basic_publish(
        #         exchange="image_processing_results", routing_key="", body=json.dumps(result)
        #     )
        #
        # except Exception as e:
        #     # If there is an error in processing an image, log the error and continue to next image
        #     print(f"Error processing image {image_path}: {str(e)}")

    channel.basic_consume(
        queue="image_processing", on_message_callback=callback, auto_ack=True
    )
    print("Listening for new job...")
    channel.start_consuming()
