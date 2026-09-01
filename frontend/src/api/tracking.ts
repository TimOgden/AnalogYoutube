export type TrackingRow = {
    title: string;
    author_name: string;
    watched_minutes: number;
};

export async function getTrackingData(): Promise<TrackingRow[]> {
    const response = await fetch("/api/tracking");

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}