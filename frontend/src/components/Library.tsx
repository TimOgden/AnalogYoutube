import { useEffect, useRef, useState } from "react";
import {
    Box,
    Chip,
    Collapse,
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
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import styles from '../components/styles/QRGenerator.module.less';
import { getLibrary, type SelectedLibraryVideo } from "../api/library";


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


interface LibraryProps {
    onSelectionChange: (videos: SelectedLibraryVideo[]) => void;
    resetVersion: number;
}


export default function Library({
    onSelectionChange,
    resetVersion,
}: LibraryProps) {
    const [library, setLibrary] = useState<LibraryData | null>(null);
    const [selectedVideos, setSelectedVideos] = useState<Set<string>>(
        new Set()
    );
    const [collapsedCollections, setCollapsedCollections] = useState<Set<string>>(
        new Set()
    );
    const lastSelectedVideo = useRef<LastSelectedVideo | null>(null);

    useEffect(() => {
        setSelectedVideos(new Set());
        lastSelectedVideo.current = null;
    }, [resetVersion]);

    const getVideoKey = (source: string, collection: string, videoIndex: number) =>
        `${source}-${collection}-${videoIndex}`;

    const selectVideo = (
        source: string,
        collection: string,
        videoIndex: number,
        shiftKey: boolean
    ) => {
        const currentVideoKey = getVideoKey(
            source,
            collection,
            videoIndex
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
                    index
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
        const videoKeys = videos.map((_, videoIndex) =>
            getVideoKey(source, collection, videoIndex)
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

    useEffect(() => {
        if (!library) {
            onSelectionChange([]);
            return;
        }

        const videos = Object.entries(library).flatMap(
                ([source, collections]) =>
                    Object.entries(collections).flatMap(([collection, playlist]) =>
                        playlist.videos.filter((video) =>
                            selectedVideos.has(
                                getVideoKey(source, collection, playlist.videos.indexOf(video))
                            )
                        ).map((video) => ({
                            ...video,
                            playlist_id: playlist.id,
                        }))
                    )
            );

        onSelectionChange(videos);
    }, [library, selectedVideos, onSelectionChange]);

    useEffect(() => {
        getLibrary()
            .then((response: LibraryData) => {
                setLibrary(response);
                setCollapsedCollections(
                    new Set(
                        Object.entries(response).flatMap(([source, collections]) =>
                            Object.keys(collections).map(
                                (collection) => `${source}-${collection}`
                            )
                        )
                    )
                );
            })
            .catch(console.error);
    }, []);

    return (
        <section className={styles.card}>
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
                    <h2>Create Cards from External Sources</h2>
                    <Typography color="text.secondary">
                        Browse curated public-domain videos from sources like archive.org
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
                                            getVideoKey(
                                                source,
                                                collection,
                                                playlist.videos.indexOf(video)
                                            )
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
                                                                videoIndex
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
            </Box>
        </section>
    );
}