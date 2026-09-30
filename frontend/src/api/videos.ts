export async function getVideos(){
    const response = await fetch(`/api/videos`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}

export async function deleteVideos(videoIds: Set<string>) {
    const response = await fetch(`/api/videos`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(Array.from(videoIds))
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`)
    }

    return response.json();
}
