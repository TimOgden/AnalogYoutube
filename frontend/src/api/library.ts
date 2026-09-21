export type LibraryResponse = {
    
}

export async function getLibrary(): Promise<LibraryResponse> {
    const response = await fetch(`/api/library`);

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}