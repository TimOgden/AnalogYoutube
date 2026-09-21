export type LibraryVideo = {
    id: string;
    title: string;
    source: string;
    download_url: string | null;
    thumbnail_url?: string | null;
    external_url?: string | null;
};

export type SelectedLibraryVideo = LibraryVideo & {
    playlist_id: string;
};

export type Playlist = {
    id: string;
    display_name: string | null;
    videos: LibraryVideo[];
};

export type LibraryResponse = Record<string, Record<string, Playlist>>;

export async function getLibrary(): Promise<LibraryResponse> {
    const response = await fetch(`/api/library`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}

export async function submitSelections(
    videos: SelectedLibraryVideo[]
) {
    const response = await fetch(`/api/generate/selections`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ videos }),
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.blob();
}