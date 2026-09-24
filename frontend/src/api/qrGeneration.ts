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
    playlist_id: string | null;
}

export async function regenerateCards(videos: Video[]) {
     const response = await fetch("/api/regenerate/multi", {
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


import type { SelectedLibraryVideo } from "./library";

export interface MultiGenerateVideo {
    id?: string;
    video_id?: string;
    title?: string;
    source: string;
    playlist_id: string | null;
    download_url?: string | null;
    thumbnail_url?: string | null;
    external_url?: string | null;
}

export async function generateCards(
    videos: (SelectedLibraryVideo | MultiGenerateVideo)[],
    files: File[] = [],
    urls: string[] = []
) {
    const formData = new FormData();
    formData.append("library_selections", JSON.stringify(videos));
    formData.append("youtube_urls", JSON.stringify(urls));
    files.forEach((file) => formData.append("files", file));

    const response = await fetch("/api/generate/multi", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.blob();
}
