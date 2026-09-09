import { useState } from "react";
import styles from "../styles/QRGenerator.module.less";
import { TextField } from "@mui/material";
import { submitUrls } from '../../api/qrGeneration.ts';

export default function YouTubeQRGenerator() {
    const [urls, setUrls] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const urlList = urls
            .split("\n")
            .map(url => url.trim())
            .filter(Boolean);

        const blob = await submitUrls(urlList, "youtube");

        const downloadUrl = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "youtube-cards.zip";
        a.click();

        URL.revokeObjectURL(downloadUrl);
    };

    return (
        <section className={styles.card}>
            <h2>Create Cards from YouTube</h2>

            <p className={styles.description}>
                Paste YouTube URLs below to generate printable QR cards.
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>

                <TextField
                    id="youtube-urls"
                    value={urls}
                    onChange={(e) => setUrls(e.target.value)}
                    placeholder={
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n" +
                        "https://youtu.be/..."
                    }
                    multiline
                    fullWidth
                />

                <button
                    type="submit"
                    disabled={!urls.trim()}
                >
                    Generate Cards
                </button>
            </form>
        </section>
    );
}