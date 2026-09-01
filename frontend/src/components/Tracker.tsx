import { useEffect, useState } from "react";
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
        <div>
            <h1>📺 Viewing History Dashboard</h1>
            <p>
                This dashboard shows a record of videos watched, detailing
                the content, time, and device used.
            </p>

            {!trackingData || trackingData.length === 0 ? (
                <p>No viewing history found yet. Time to scan some QR codes!</p>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Video Title</th>
                            <th>Author Name</th>
                            <th>Minutes Watched</th>
                        </tr>
                    </thead>

                    <tbody>
                        {trackingData.map((row, index) => (
                            <tr key={`${row.title}-${index}`}>
                                <td>{row.title}</td>
                                <td>{row.author_name}</td>
                                <td>{row.watched_minutes.toFixed(2)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}