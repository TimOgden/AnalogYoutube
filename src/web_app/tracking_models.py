from pydantic import BaseModel


class TrackingResponse(BaseModel):
    by_video_df: list[dict]
    total_watched_minutes: float
