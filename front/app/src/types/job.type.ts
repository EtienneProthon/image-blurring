export type JobType = {
  id: number;
  job_group_id: number;
  created_at: Date;
  started_at: Date;
  finished_at: Date;
  status: string;
  image_url: string;
  process_params: JSON;
  original_image_s3: string;
  processed_image_s3: string;
};
