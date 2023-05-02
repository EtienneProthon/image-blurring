# import logging
import json
from datetime import datetime

import pika
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.orm import scoped_session

from back.database import Base, SessionLocal, engine
from back.models import Job, JobGroup, JobGroupView

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Initialize Database connection
# Create tables if they do not exist
Base.metadata.create_all(bind=engine)
# Create view to be able to easily retrieve data regarding job group progress
with engine.connect() as con:
    create_view_sql = text(
        """CREATE OR REPLACE VIEW job_groups_view AS
    SELECT jg.id, jg.created_at,
           COUNT(j.id) AS total_jobs,
           COUNT(CASE WHEN j.status = 'COMPLETED' THEN 1 ELSE NULL END) AS completed_jobs,
           MAX(j.finished_at) AS finished_at
    FROM job_groups jg
    LEFT JOIN jobs j ON j.job_group_id = jg.id
    GROUP BY jg.id;
    """
    )
    res = con.execute(create_view_sql)
    con.commit()

session = scoped_session(SessionLocal)


# This is used to prevent connection auto close by rabbit after timeout
def connect_to_rabbitmq_and_send_message(job_id):
    # Initialize RabbitMQ connection and channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    # Declare exchange and queue
    channel.exchange_declare(exchange="image_processing", exchange_type="direct")
    channel.queue_declare(queue="image_processing")
    message = {"job_id": job_id}
    channel.basic_publish(
        exchange="image_processing",
        routing_key="image_processing",
        body=json.dumps(message),
    )
    connection.close()


# Put not started job inside the queue
def recover_not_started_jobs():
    jobs_not_started = session.query(Job).filter_by(status="NOTSTARTED").all()
    for job in jobs_not_started:
        print("RECOVERING JOB {job.id} NOT STARTED")
        message = {"job_id": job.id}
        channel.basic_publish(
            exchange="image_processing",
            routing_key="image_processing",
            body=json.dumps(message),
        )


recover_not_started_jobs()

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes
app.session = session


@app.route("/job_groups")
def job_groups_api():
    order = request.args.get("order")
    if order is not None:
        if order == "-id":
            job_groups = (
                app.session.query(JobGroupView).order_by(JobGroupView.id.desc()).all()
            )
    else:
        job_groups = app.session.query(JobGroupView).all()
    app.session.remove()
    return jsonify(job_groups)


@app.route("/jobs")
def jobs_api():
    job_group_id = request.args.get("job_group_id")
    if job_group_id is not None:
        jobs = app.session.query(Job).filter_by(job_group_id=job_group_id).all()
    else:
        jobs = app.session.query(Job).all()
    app.session.remove()
    return jsonify(jobs)


@app.route("/job/<job_id>/retry")
def job_retry_api(job_id):
    job = app.session.query(Job).get(job_id)
    job.status = "NOTSTARTED"
    app.session.commit()
    # Add job inside the RabbitMQ queue
    try:
        connect_to_rabbitmq_and_send_message(job.id)
        response = {
            "job_retry": True,
        }
    except Exception as e:
        print(f"ERROR: retrying job {job.id}: {str(e)}")
        job.status = "FAILED"
        job.finished_at = datetime.utcnow()
        app.session.commit()
        response = {
            "job_retry": False,
        }

    return jsonify(response)


@app.route("/process_images", methods=["POST"])
def process_images():
    # Load input data from JSON request
    data = request.get_json()
    print(f"Process request {data}")
    images = data["images"]
    process_params = data["process_params"]

    job_group = JobGroup()
    app.session.add(job_group)
    app.session.commit()
    for image_path in images:
        job = Job(
            job_group_id=job_group.id,
            status="NOTSTARTED",
            image_url=image_path,
            process_params=process_params,
        )
        app.session.add(job)
        app.session.commit()

        # Add job inside the RabbitMQ queue
        try:
            connect_to_rabbitmq_and_send_message(job.id)
        except Exception as e:
            print(f"ERROR: sending job to queue {job.id}: {str(e)}")
            job.status = "FAILED"
            job.finished_at = datetime.utcnow()
            app.session.commit()

    # Return number of job created
    response = {
        "job_created": len(images),
    }
    return jsonify(response)
