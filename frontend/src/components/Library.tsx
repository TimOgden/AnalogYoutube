import { useEffect, useState } from "react";
import {
    Box,
    Chip,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import { getLibrary } from "../api/library";


type LibraryVideo = {
    id: string;
    title: string;
    source: string;
};

type LibraryData = Record<
    string,
    Record<string, LibraryVideo[]>
>;


export default function Library() {
    const [library, setLibrary] = useState<LibraryData | null>(null);

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
                                                overflow: "hidden",
                                            }}
                                        >
                                            <Table>
                                                <TableHead>
                                                    <TableRow>
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
                                                            Source
                                                        </TableCell>
                                                    </TableRow>
                                                </TableHead>

                                                <TableBody>
                                                    {videos.map((video) => (
                                                        <TableRow
                                                            key={video.id}
                                                            hover
                                                            sx={{
                                                                "&:last-child td":
                                                                    {
                                                                        borderBottom: 0,
                                                                    },
                                                            }}
                                                        >
                                                            <TableCell>
                                                                <Typography>
                                                                    {
                                                                        video.title
                                                                    }
                                                                </Typography>
                                                            </TableCell>

                                                            <TableCell>
                                                                <Typography>
                                                                    {
                                                                        video.source
                                                                    }
                                                                </Typography>
                                                            </TableCell>
                                                        </TableRow>
                                                    ))}
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
        </Box>
    );
}