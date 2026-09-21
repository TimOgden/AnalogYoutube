import { useEffect, useState } from "react";
import {
    Box,
    Chip,
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
import SendIcon from "@mui/icons-material/Send";
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { getLibrary } from "../api/library";


type LibraryVideo = {
    id: string;
    title: string;
    source: string;
    external_url: string;
};

type LibraryData = Record<
    string,
    Record<string, LibraryVideo[]>
>;


export default function Library() {
    const [library, setLibrary] = useState<LibraryData | null>(null);
    const [selectedVideos, setSelectedVideos] = useState<Set<string>>(
        new Set()
    );

    const getVideoKey = (source: string, collection: string, videoId: string) =>
        `${source}-${collection}-${videoId}`;

    const toggleVideo = (videoKey: string) => {
        setSelectedVideos((currentSelection) => {
            const nextSelection = new Set(currentSelection);

            if (nextSelection.has(videoKey)) {
                nextSelection.delete(videoKey);
            } else {
                nextSelection.add(videoKey);
            }

            return nextSelection;
        });
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
                                ([collection, videos]) => (
                                    <Box
                                        key={`${source}-${collection}`}
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
                                            <Typography
                                                variant="h6"
                                                sx={{ fontWeight: 600 }}
                                            >
                                                {collection}
                                            </Typography>

                                            <Chip
                                                label={`${videos.length} ${
                                                    videos.length === 1
                                                        ? "video"
                                                        : "videos"
                                                }`}
                                                size="small"
                                                variant="outlined"
                                            />
                                        </Box>

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
                                                    {videos.map((video) => {
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
                                                            onClick={() => toggleVideo(videoKey)}
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
                                                                    onChange={() => toggleVideo(videoKey)}
                                                                    onClick={(event) => event.stopPropagation()}
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
                                                                    href={video.external_url}
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
                                    </Box>
                                )
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
                    aria-label={`Submit ${selectedVideos.size} selected videos`}
                >
                    <SendIcon sx={{ mr: 1 }} />
                    Submit ({selectedVideos.size})
                </Fab>
            )}
        </Box>
    );
}