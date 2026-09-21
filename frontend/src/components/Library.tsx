import React, { useEffect, useRef, useState } from "react";
import {
    Box,
    Chip,
    Collapse,
    Fab,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import Checkbox from "@mui/material/Checkbox";
import IconButton from "@mui/material/IconButton";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import SendIcon from "@mui/icons-material/Send";
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { getLibrary, submitSelections } from "../api/library";


type Playlist = {
    id: string;
    display_name: string | null;
    videos: LibraryVideo[];
}

type LibraryVideo = {
    id: string;
    title: string;
    source: string;
    download_url: string | null;
    thumbnail_url?: string | null;
    external_url?: string | null;
};

type LibraryData = Record<
    string,
    Record<string, Playlist>
>;

type LastSelectedVideo = {
    source: string;
    collection: string;
    index: number;
};


export default function Library() {
    const [library, setLibrary] = useState<LibraryData | null>(null);
    const [selectedVideos, setSelectedVideos] = useState<Set<string>>(
        new Set()
    );
    const [collapsedCollections, setCollapsedCollections] = useState<Set<string>>(
        new Set()
    );
    const lastSelectedVideo = useRef<LastSelectedVideo | null>(null);

    const getVideoKey = (source: string, collection: string, videoId: string) =>
        `${source}-${collection}-${videoId}`;

    const selectVideo = (
        source: string,
        collection: string,
        videoIndex: number,
        videos: LibraryVideo[],
        shiftKey: boolean
    ) => {
        const currentVideoKey = getVideoKey(
            source,
            collection,
            videos[videoIndex].id
        );
        const previousSelection = lastSelectedVideo.current;
        const shouldUseRange =
            shiftKey &&
            previousSelection?.source === source &&
            previousSelection.collection === collection;

        lastSelectedVideo.current = {
            source,
            collection,
            index: videoIndex,
        };

        setSelectedVideos((currentSelection) => {
            const nextSelection = new Set(currentSelection);
            const rangeStart = shouldUseRange
                ? Math.min(previousSelection.index, videoIndex)
                : videoIndex;
            const rangeEnd = shouldUseRange
                ? Math.max(previousSelection.index, videoIndex)
                : videoIndex;
            const shouldDeselect = currentSelection.has(currentVideoKey);

            for (let index = rangeStart; index <= rangeEnd; index += 1) {
                const videoKey = getVideoKey(
                    source,
                    collection,
                    videos[index].id
                );

                if (shouldDeselect) {
                    nextSelection.delete(videoKey);
                } else {
                    nextSelection.add(videoKey);
                }
            }

            return nextSelection;
        });
    };

    const toggleCollection = (
        source: string,
        collection: string,
        videos: LibraryVideo[]
    ) => {
        const videoKeys = videos.map((video) =>
            getVideoKey(source, collection, video.id)
        );
        const allSelected = videoKeys.every((videoKey) =>
            selectedVideos.has(videoKey)
        );

        setSelectedVideos((currentSelection) => {
            const nextSelection = new Set(currentSelection);

            videoKeys.forEach((videoKey) => {
                if (allSelected) {
                    nextSelection.delete(videoKey);
                } else {
                    nextSelection.add(videoKey);
                }
            });

            return nextSelection;
        });
        lastSelectedVideo.current = null;
    };

    const toggleCollectionCollapsed = (collectionKey: string) => {
        setCollapsedCollections((currentCollapsed) => {
            const nextCollapsed = new Set(currentCollapsed);

            if (nextCollapsed.has(collectionKey)) {
                nextCollapsed.delete(collectionKey);
            } else {
                nextCollapsed.add(collectionKey);
            }

            return nextCollapsed;
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!library) {
            return;
        }

        const videos = Object.entries(library).flatMap(
            ([source, collections]) =>
                Object.entries(collections).flatMap(([collection, playlist]) =>
                    playlist.videos.filter((video) =>
                        selectedVideos.has(getVideoKey(source, collection, video.id))
                    ).map((video) => ({
                        ...video,
                        playlist_id: playlist.id,
                    }))
                )
        );

        const blob = await submitSelections(videos);
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "archive_org-cards.zip";
        a.click();

        URL.revokeObjectURL(downloadUrl);
    };

    useEffect(() => {
        const loadLibrary = () => {
            getLibrary()
                .then((response: LibraryData) => {
                    setLibrary(response);
                })
                .catch(console.error);
        };

        loadLibrary();
    }, []);

    return (
        <Box
            sx={{
                width: "100%",
                maxWidth: 1000,
                mx: "auto",
                px: 3,
                py: 5,
            }}
        >
            <Box sx={{ mb: 4 }}>
                <Typography
                    variant="h3"
                    component="h1"
                    sx={{ fontWeight: 700, mb: 1 }}
                >
                    📚 Library
                </Typography>

                <Typography color="text.secondary">
                    Browse videos available in your library.
                </Typography>
            </Box>

            {!library ? (
                <Typography color="text.secondary">
                    Loading library...
                </Typography>
            ) : Object.keys(library).length === 0 ? (
                <Typography color="text.secondary">
                    Your library is empty.
                </Typography>
            ) : (
                Object.entries(library).map(
                    ([source, collections]) => (
                        <Box key={source} sx={{ mb: 5 }}>
                            <Typography
                                variant="h5"
                                sx={{
                                    fontWeight: 700,
                                    mb: 2,
                                }}
                            >
                                {source}
                            </Typography>

                            {Object.entries(collections).map(
                                ([collection, playlist]) => {
                                    const selectedCount = playlist.videos.filter((video) =>
                                        selectedVideos.has(
                                            getVideoKey(source, collection, video.id)
                                        )
                                    ).length;
                                    const allSelected =
                                        playlist.videos.length > 0 &&
                                        selectedCount === playlist.videos.length;
                                    const collectionKey = `${source}-${collection}`;
                                    const isCollapsed = collapsedCollections.has(
                                        collectionKey
                                    );

                                    return (
                                    <Box
                                        key={collectionKey}
                                        sx={{ mb: 4 }}
                                    >
                                        <Box
                                            sx={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 1.5,
                                                mb: 1.5,
                                            }}
                                        >
                                            <Checkbox
                                                checked={allSelected}
                                                indeterminate={
                                                    selectedCount > 0 && !allSelected
                                                }
                                                disabled={playlist.videos.length === 0}
                                                onChange={() =>
                                                    toggleCollection(
                                                        source,
                                                        collection,
                                                        playlist.videos
                                                    )
                                                }
                                                slotProps={{
                                                    input: {
                                                        "aria-label": `Select all videos in ${collection}`,
                                                    },
                                                }}
                                            />
                                            <IconButton
                                                size="small"
                                                onClick={() =>
                                                    toggleCollectionCollapsed(collectionKey)
                                                }
                                                aria-expanded={!isCollapsed}
                                                aria-label={`${isCollapsed ? "Expand" : "Collapse"} ${collection}`}
                                            >
                                                <ExpandMoreIcon
                                                    sx={{
                                                        transform: isCollapsed
                                                            ? "rotate(-90deg)"
                                                            : "rotate(0deg)",
                                                        transition: "transform 150ms ease",
                                                    }}
                                                />
                                            </IconButton>
                                            <Typography
                                                variant="h6"
                                                sx={{ fontWeight: 600 }}
                                            >
                                                {playlist.display_name}
                                            </Typography>

                                            <Chip
                                                label={`${playlist.videos.length} ${
                                                    playlist.videos.length === 1
                                                        ? "video"
                                                        : "videos"
                                                }`}
                                                size="small"
                                                variant="outlined"
                                            />
                                        </Box>

                                        <Collapse in={!isCollapsed}>
                                            <TableContainer
                                                component={Paper}
                                                sx={{
                                                    borderRadius: 2,
                                                    overflowX: "hidden",
                                                    maxHeight: 400,
                                                    overflowY: "auto",
                                                }}
                                            >
                                                <Table>
                                                <TableHead>
                                                    <TableRow>
                                                        <TableCell padding="checkbox" />
                                                        <TableCell
                                                            sx={{
                                                                fontWeight: 700,
                                                            }}
                                                        >
                                                            Video
                                                        </TableCell>
                                                        <TableCell
                                                            sx={{
                                                                fontWeight: 700,
                                                            }}
                                                        >
                                                            Link
                                                        </TableCell>
                                                    </TableRow>
                                                </TableHead>

                                                <TableBody>
                                                    {playlist.videos.map((video, videoIndex) => {
                                                        const videoKey = getVideoKey(
                                                            source,
                                                            collection,
                                                            video.id
                                                        );
                                                        const isSelected = selectedVideos.has(
                                                            videoKey
                                                        );

                                                        return (
                                                        <TableRow
                                                            key={video.id}
                                                            hover
                                                            selected={isSelected}
                                                            onClick={(event) =>
                                                                selectVideo(
                                                                    source,
                                                                    collection,
                                                                    videoIndex,
                                                                    playlist.videos,
                                                                    event.shiftKey
                                                                )
                                                            }
                                                            sx={{
                                                                cursor: "pointer",
                                                                "&:last-child td": {
                                                                    borderBottom: 0,
                                                                },
                                                            }}
                                                        >
                                                            <TableCell padding="checkbox">
                                                                <Checkbox
                                                                    checked={isSelected}
                                                                    onChange={() => undefined}
                                                                    onClick={(event) => {
                                                                        event.stopPropagation();
                                                                        selectVideo(
                                                                            source,
                                                                            collection,
                                                                            videoIndex,
                                                                            playlist.videos,
                                                                            event.shiftKey
                                                                        );
                                                                    }}
                                                                    slotProps={{
                                                                        input: {
                                                                            "aria-label": `Select ${video.title}`,
                                                                        },
                                                                    }}
                                                                />
                                                            </TableCell>
                                                            <TableCell>
                                                                <Typography>
                                                                    {
                                                                        video.title
                                                                    }
                                                                </Typography>
                                                            </TableCell>
                                                            <TableCell>
                                                                <IconButton
                                                                    component="a"
                                                                    href={video.external_url ?? undefined}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    aria-label={`Open ${video.title} in new tab`}
                                                                    size="small"
                                                                    onClick={(event) => event.stopPropagation()}
                                                                >
                                                                    <OpenInNewIcon fontSize="small" />
                                                                </IconButton>
                                                            </TableCell>
                                                        </TableRow>
                                                        );
                                                    })}
                                                </TableBody>
                                                </Table>
                                            </TableContainer>
                                        </Collapse>
                                    </Box>
                                    );
                                }
                            )}
                        </Box>
                    )
                )
            )}

            {selectedVideos.size > 0 && (
                <Fab
                    variant="extended"
                    color="primary"
                    sx={{
                        position: "fixed",
                        right: 24,
                        bottom: 24,
                        zIndex: 1100,
                    }}
                    onClick={handleSubmit}
                    aria-label={`Submit ${selectedVideos.size} selected videos`}
                >
                    <SendIcon sx={{ mr: 1 }} />
                    Submit ({selectedVideos.size})
                </Fab>
            )}
        </Box>
    );
}