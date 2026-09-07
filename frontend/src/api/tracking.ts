export type TrackingRow = {
    title: string;
    author_name: string;
    watched_minutes: number;
};

export async function getTrackingData(selectedDuration: number): Promise<TrackingRow[]> {
    const response = await fetch(`/api/tracking?duration=${selectedDuration}`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}