from fastapi import FastAPI, HTTPException
from web_scraper.scrape_socials import scrapeSocials
from models.job import Job, JobRequest
from config.db import connectDb
from bson import ObjectId
from bson.errors import InvalidId

app = FastAPI()

# Connect to database
connectDb()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/job")
async def root_2(job: JobRequest):
    try:
        j = Job(jd_url=job.jd_url, hr_id=job.hr_id)
        j.save()
        return {
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/job")
async def get_job(job_id: str):
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(job_id):
            raise HTTPException(
                status_code=400, detail="Invalid job ID format")

        # Query the job by ID
        job = Job.objects(id=job_id).first()  # type: ignore
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job
    except HTTPException:
        raise
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")
