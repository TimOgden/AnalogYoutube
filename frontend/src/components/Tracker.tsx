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
    const [totalWatchedMinutes, setTotalWatchedMinutes] = useState<number | null>(null);
    const [selectedDuration, setSelectedDuration] = useState(durations[0].value);


    function formatWatchedMinutes(watchedMinutes: number): string {
        if (watchedMinutes < 1) {
            return `${(watchedMinutes * 60).toFixed(0)} seconds`;
        } else if (watchedMinutes < 60) {
            return `${watchedMinutes.toFixed(2)} minutes`;
        }

        const hours = Math.floor(watchedMinutes / 60);
        const minutes = Math.floor(watchedMinutes % 60);
        return `${hours} hours ${minutes} minutes`;
    }

    useEffect(() => {
        getTrackingData(selectedDuration)
            .then((response) => {
                setTrackingData(response.by_video_df);
                setTotalWatchedMinutes(response.total_watched_minutes);
            })
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

            <>
                <Typography variant="h6" sx={{ mb: 2 }}>
                    Total Watch Time: {formatWatchedMinutes(totalWatchedMinutes ?? 0)}
                </Typography>
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
                            {!trackingData || trackingData.length === 0 ?
                                <TableRow
                                    key={'undefined'}
                                    hover
                                    sx={{
                                        "&:last-child td": {
                                            borderBottom: 0,
                                        },
                                    }}>
                                    <TableCell>
                                        <Typography>--</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography>--</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography align="right">--</Typography>
                                    </TableCell>
                                </TableRow>
                            : trackingData.map((row, index) => (
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
                                        <Typography>
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
            </>
        </Box>
    );
}