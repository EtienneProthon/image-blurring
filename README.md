# image-blurring

## Setup

```
. .venv/bin/activate # Activate the virtual env
docker compose up -d # To launch postgresql, minio, rabbitmq
pip install --editable .
run-worker &
flask --app ./back/api/api.py run
# Open another terminal and run front end
cd front/app
npm install
npm run dev -- --open
```

## Next Steps

- Improve error handling
- Add tests
- Add job retry
- Add pagination
- Deploy inside a kubernetes cluster with autoscaling for the workers pools
- Add replicate for RabbitMq and s3 (minio) to prevent data loss in case of crash and garantee high availability
