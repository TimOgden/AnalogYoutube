import { useEffect, useState } from "react";
import {
    Box,
    Button,
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

const durations = [
    { label: "All Time", value: 3650 }, // 10 years
    { label: "Last 14 Days", value: 14 },
    { label: "Last 30 Days", value: 30 },
    { label: "Last 90 Days", value: 90 }
];


export default function Tracker() {
    const [trackingData, setTrackingData] = useState<TrackingRow[] | null>(null);
    const [selectedDuration, setSelectedDuration] = useState(durations[0].value);

    useEffect(() => {
        getTrackingData(selectedDuration)
            .then(setTrackingData)
            .catch(console.error);
    }, [selectedDuration]);

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
            </Box>
            <Box sx={{ mb: 4 }}>
                {durations.map((duration) => (
                    <Button
                        key={duration.value}
                        variant={
                            selectedDuration === duration.value
                                ? "contained"
                                : "outlined"
                        }
                        onClick={() => setSelectedDuration(duration.value)}
                        sx={{ mr: 2, mb: 1 }}
                    >
                        {duration.label}
                    </Button>
                ))}
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