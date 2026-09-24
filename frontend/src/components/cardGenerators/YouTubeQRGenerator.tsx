import { useState } from "react";
import styles from "../styles/QRGenerator.module.less";
import { TextField } from "@mui/material";
interface YoutubeQRGeneratorProps {
    onUrlsChange: (urls: string[]) => void;
}

export default function YouTubeQRGenerator({ onUrlsChange }: YoutubeQRGeneratorProps) {
    const [urls, setUrls] = useState("");

    return (
        <section className={styles.card}>
            <h2>Create Cards from YouTube</h2>

            <p className={styles.description}>
                Paste YouTube URLs below to generate printable QR cards.
            </p>

            <form className={styles.form}>

                <TextField
                    id="youtube-urls"
                    value={urls}
                    onChange={(e) => {
                        const value = e.target.value;
                        setUrls(value);
                        onUrlsChange(
                            value
                                .split("\n")
                                .map((url) => url.trim())
                                .filter(Boolean)
                        );
                    }}
                    placeholder={
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n" +
                        "https://youtu.be/..."
                    }
                    multiline
                    fullWidth
                />
            </form>
        </section>
    );
}