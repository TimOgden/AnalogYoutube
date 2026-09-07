import { useEffect, useState } from "react";
import {
    Box,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
} from "@mui/material";
import { getTrackingData } from "../api/tracking";

type TrackingRow = {
    title: string;
    author_name: string;
    watched_minutes: number;
};


export default function Tracker() {
    const [trackingData, setTrackingData] = useState<TrackingRow[] | null>(null);

    useEffect(() => {
        getTrackingData()
            .then(setTrackingData)
            .catch(console.error);
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
                    📺 Viewing History
                </Typography>

                <Typography variant="body1" color="text.secondary">
                    See what has been watched and how much time was spent
                    watching each video.
                </Typography>
            </Box>

            {!trackingData || trackingData.length === 0 ? (
                <Paper sx={{ p: 4 }}>
                    <Typography color="text.secondary">
                        No viewing history found yet. Time to scan some QR
                        codes!
                    </Typography>
                </Paper>
            ) : (
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
                                <TableCell sx={{ fontWeight: 700 }}>
                                    Video
                                </TableCell>

                                <TableCell sx={{ fontWeight: 700 }}>
                                    Author
                                </TableCell>

                                <TableCell
                                    align="right"
                                    sx={{ fontWeight: 700 }}
                                >
                                    Minutes Watched
                                </TableCell>
                            </TableRow>
                        </TableHead>

                        <TableBody>
                            {trackingData.map((row, index) => (
                                <TableRow
                                    key={`${row.title}-${index}`}
                                    hover
                                    sx={{
                                        "&:last-child td": {
                                            borderBottom: 0,
                                        },
                                    }}
                                >
                                    <TableCell>
                                        <Typography fontWeight={500}>
                                            {row.title}
                                        </Typography>
                                    </TableCell>

                                    <TableCell>
                                        {row.author_name}
                                    </TableCell>

                                    <TableCell align="right">
                                        {Number(
                                            row.watched_minutes
                                        ).toFixed(2)}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Box>
    );
}