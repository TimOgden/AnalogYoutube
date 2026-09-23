export async function submitUrls(urls: string[], source: string) {
    const response = await fetch("/api/generate/urls", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            urls,
            source,
        }),
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.blob();
}

export async function submitFiles(files: File[]) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
    }

    const response = await fetch("/api/generate/files", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.blob();
}

interface Video {
    source: string;
    video_id: string;
}

export async function regenerateCards(videos: Video[]) {
     const response = await fetch("/api/generate/multi", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            videos,
        }),
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.blob();
}