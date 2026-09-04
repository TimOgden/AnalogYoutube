import { useState } from "react";
import styles from "./QRGenerator.module.less";
import { TextField } from "@mui/material";
import { submitUrls } from '../api/qrGeneration.ts';

export default function Generator() {
    const [urls, setUrls] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const urlList = urls
            .split("\n")
            .map(url => url.trim())
            .filter(Boolean);

        const blob = await submitUrls(urlList);

        const downloadUrl = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "youtube-cards.zip";
        a.click();

        URL.revokeObjectURL(downloadUrl);
    };

    return (
        <main className={styles.page}>
            <header className={styles.header}>
                <h1>Analog YouTube</h1>
                <p>Turn YouTube videos into physical cards.</p>
            </header>

            <section className={styles.card}>
                <h2>Create Cards</h2>

                <p className={styles.description}>
                    Paste YouTube URLs below to generate printable QR cards.
                    Add one URL per line.
                </p>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <label htmlFor="youtube-urls">
                        YouTube URLs
                    </label>

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
        </main>
    );
}