export type TrackingRow = {
    title: string;
    author_name: string;
    source: string;
    watched_minutes: number;
};

export type TrackingResponse = {
    by_video_df: TrackingRow[];
    total_watched_minutes: number;
};

export async function getTrackingData(selectedDuration: number): Promise<TrackingResponse> {
    const response = await fetch(`/api/tracking?duration=${selectedDuration}`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}