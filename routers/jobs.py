from celery.result import AsyncResult
from fastapi import APIRouter

from celery_app import celery
from schemas import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    result = AsyncResult(job_id, app=celery)

    if result.state == "SUCCESS":
        return {"job_id": job_id, "status": "done", "message": result.result}
    elif result.state == "FAILURE":
        return {"job_id": job_id, "status": "failed", "message": None}
    else:  # PENDING, STARTED, RETRY
        return {"job_id": job_id, "status": "pending", "message": None}
