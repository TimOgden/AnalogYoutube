import { useState } from "react";
import styles from "../styles/QRGenerator.module.less";
import { Button, CircularProgress, TextField } from "@mui/material";
import { submitUrls } from '../../api/qrGeneration.ts';

export default function YouTubeQRGenerator() {
    const [isGenerating, setIsGenerating] = useState(false);
    const [urls, setUrls] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        setIsGenerating(true);
        try {
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
        } finally {
            setIsGenerating(false);
        }
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

                <Button
                    type="submit"
                    variant="contained"
                    disabled={!urls.trim()}
                    startIcon={
                        isGenerating
                            ? <CircularProgress size={18} color="inherit" />
                            : undefined
                    }
                >
                    {isGenerating ? "Generating Cards..." : "Generate Cards"}
                </Button>
            </form>
        </section>
    );
}