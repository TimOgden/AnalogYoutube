import React, { useEffect, useState } from "react";
import {
    Box,
    Card,
    CardActionArea,
    CardContent,
    CardMedia,
    Checkbox,
    Chip,
    CircularProgress,
    Fab,
    Typography,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import DeleteIcon from "@mui/icons-material/Delete";
import { getVideos, deleteVideos } from "../api/videos";
import { regenerateCards } from "../api/qrGeneration";


type Video = {
    video_id: string;
    title: string;
    source: "library" | "local" | "youtube";
    thumbnail_path: string;
    thumbnail_url: string;
    video_path: string | null;
    video_url: string | null;
    author_name: string | null;
    playlist_id: string | null;
};


const SOURCE_ORDER: Video["source"][] = [
    "youtube",
    "library",
    "local",
];

const SOURCE_LABELS: Record<Video["source"], string> = {
    library: "Library",
    local: "Local Videos",
    youtube: "YouTube",
};


export default function VideoViewer() {
    const [videos, setVideos] = useState<Video[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [selectedVideoIds, setSelectedVideoIds] = useState<Set<string>>(
        new Set(),
    );

    useEffect(() => {
        getVideos()
            .then((response: Video[]) => {
                setVideos(response);
            })
            .catch(console.error);
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        setIsGenerating(true);
        try {
            e.preventDefault();

            const blob = await regenerateCards(videos.filter((video) => selectedVideoIds.has(video.video_id)));

            const downloadUrl = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "cards.zip";
            a.click();

            URL.revokeObjectURL(downloadUrl);

            setSelectedVideoIds(new Set());
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDelete = async (e: React.FormEvent) => {
        setIsDeleting(true);
        try {
            e.preventDefault();
            deleteVideos(selectedVideoIds)
                .then((response: Video[]) => {
                    setVideos(response);
                    setSelectedVideoIds(new Set());
                })
                .catch(console.error);
        } finally {
            setIsDeleting(false);
        }
    }

    function toggleVideo(videoId: string) {
        setSelectedVideoIds((current) => {
            const updated = new Set(current);

            if (updated.has(videoId)) {
                updated.delete(videoId);
            } else {
                updated.add(videoId);
            }

            return updated;
        });
    }

    return (
        <Box
            sx={{
                width: "100%",
                maxWidth: 1200,
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
                    Library
                </Typography>

                <Typography color="text.secondary">
                    Browse your videos and regenerate QR cards.
                </Typography>
            </Box>

            {SOURCE_ORDER.map((source) => {
                const sourceVideos = videos.filter(
                    (video) => video.source === source,
                );

                if (sourceVideos.length === 0) {
                    return null;
                }

                return (
                    <Box key={source} sx={{ mb: 6 }}>
                        <Box
                            sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1.5,
                                mb: 2,
                            }}
                        >
                            <Typography
                                variant="h5"
                                sx={{ fontWeight: 700 }}
                            >
                                {SOURCE_LABELS[source]}
                            </Typography>

                            <Chip
                                size="small"
                                variant="outlined"
                                label={`${sourceVideos.length} ${
                                    sourceVideos.length === 1
                                        ? "video"
                                        : "videos"
                                }`}
                            />
                        </Box>

                        <Box
                            sx={{
                                display: "grid",
                                gridTemplateColumns: {
                                    xs: "1fr",
                                    sm: "repeat(2, 1fr)",
                                    md: "repeat(3, 1fr)",
                                    lg: "repeat(4, 1fr)",
                                },
                                gap: 2,
                            }}
                        >
                            {sourceVideos.map((video) => {
                                const selected =
                                    selectedVideoIds.has(video.video_id);

                                return (
                                    <Card
                                        key={video.video_id}
                                        variant="outlined"
                                        sx={{
                                            position: "relative",
                                            height: "100%",
                                            borderWidth: selected ? 2 : 1,
                                        }}
                                    >
                                        <CardActionArea
                                            onClick={() =>
                                                toggleVideo(video.video_id)
                                            }
                                            sx={{
                                                height: "100%",
                                                display: "flex",
                                                flexDirection: "column",
                                                alignItems: "stretch",
                                                justifyContent: "flex-start",
                                            }}
                                        >
                                            <Box
                                                sx={{
                                                    position: "absolute",
                                                    top: 4,
                                                    right: 4,
                                                    zIndex: 1,
                                                    bgcolor:
                                                        "background.paper",
                                                    borderRadius: "50%",
                                                }}
                                            >
                                                <Checkbox
                                                    checked={selected}
                                                    tabIndex={-1}
                                                    disableRipple
                                                    slotProps={{
                                                        input: {
                                                            "aria-label":
                                                                `Select ${video.title}`,
                                                        },
                                                    }}
                                                />
                                            </Box>

                                            <CardMedia
                                                component="img"
                                                image={
                                                    video.thumbnail_url
                                                }
                                                alt={`Thumbnail for ${video.title}`}
                                                sx={{
                                                    width: "100%",
                                                    aspectRatio: "16 / 9",
                                                    objectFit: "cover",
                                                }}
                                            />

                                            <CardContent
                                                sx={{
                                                    width: "100%",
                                                    boxSizing: "border-box",
                                                }}
                                            >
                                                <Typography
                                                    variant="subtitle1"
                                                    sx={{
                                                        fontWeight: 600,
                                                        lineHeight: 1.3,
                                                    }}
                                                >
                                                    {video.title}
                                                </Typography>

                                                {video.author_name && (
                                                    <Typography
                                                        variant="body2"
                                                        color="text.secondary"
                                                        sx={{ mt: 0.75 }}
                                                    >
                                                        {video.author_name}
                                                    </Typography>
                                                )}
                                            </CardContent>
                                        </CardActionArea>
                                    </Card>
                                );
                            })}
                        </Box>
                    </Box>
                );
            })}

            {selectedVideoIds.size > 0 && (
                <Box
                    sx={{
                        position: "fixed",
                        right: 24,
                        bottom: 24,
                        zIndex: 1100,
                        display: "flex",
                        gap: 1.5,
                        flexWrap: "wrap",
                        justifyContent: "flex-end",
                    }}
                >
                    <Fab
                        variant="extended"
                        color="secondary"
                        onClick={handleDelete}
                        disabled={isDeleting}
                        aria-label={`Delete ${selectedVideoIds.size} selected items`}
                    >
                        {isDeleting ? (
                            <>
                                <CircularProgress
                                    size={20}
                                    color="inherit"
                                    sx={{ mr: 1 }}
                                />
                                Deleting...
                            </>
                        ) : (
                            <>
                                <DeleteIcon sx={{ mr: 1 }} />
                                Delete ({selectedVideoIds.size})
                            </>
                        )}
                    </Fab>
                    <Fab
                        variant="extended"
                        color="primary"
                        onClick={handleSubmit}
                        disabled={isGenerating}
                        aria-label={`Submit ${selectedVideoIds.size} selected items`}
                    >
                        {isGenerating ? (
                            <>
                                <CircularProgress
                                    size={20}
                                    color="inherit"
                                    sx={{ mr: 1 }}
                                />
                                Generating...
                            </>
                        ) : (
                            <>
                                <SendIcon sx={{ mr: 1 }} />
                                Submit ({selectedVideoIds.size})
                            </>
                        )}
                    </Fab>
                </Box>
                
            )}
        </Box>
    );
}