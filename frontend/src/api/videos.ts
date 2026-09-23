export async function getVideos(){
    const response = await fetch(`/api/videos`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}