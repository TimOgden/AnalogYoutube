import styles from "../styles/QRGenerator.module.less";
import FileUpload from "../common/FileUpload";
import { useState, type FormEvent } from "react";
import { submitFiles } from "../../api/qrGeneration";
import { Box, Button, CircularProgress, IconButton, Paper, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";


interface LocalUploadQRGenerator {
    isGenerating: boolean;
    setIsGenerating: (isGenerating: boolean) => void;
}


export default function LocalUploadQRGenerator({ isGenerating, setIsGenerating }: LocalUploadQRGenerator) {
    const [files, setFiles] = useState<File[]>([]);

    function addFiles(newFiles: File[]) {
        setFiles((currentFiles) => [
            ...currentFiles,
            ...newFiles,
        ]);
    }

    function removeFile(fileToRemove: File) {
        setFiles((currentFiles) =>
            currentFiles.filter(
                (file) => file !== fileToRemove,
            ),
        );
    }

    async function handleSubmit(e: FormEvent<HTMLFormElement>) {
        setIsGenerating(true);
        try {
            e.preventDefault();
            if (!files || files.length === 0) {
                alert("Please upload at least one file.");
                return;
            }

            const blob = await submitFiles(files);
            if (!blob || blob.size === 0) {
                alert("No files were returned from the server.");
                return;
            }

            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "local-upload-cards.zip";
            a.click();
            URL.revokeObjectURL(downloadUrl);
        } finally {
            setIsGenerating(false);
        }
    }

    return (
        <section className={styles.card}>
            <h2>Create Cards from Local Files</h2>

            <p className={styles.description}>
                Upload local files below to generate printable QR cards.
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>
                <FileUpload onFilesSelected={addFiles} />
                <Paper
                    variant="outlined"
                    sx={{
                        width: "100%",
                        maxHeight: 250,
                        minHeight: 120,
                        overflowY: "auto",
                        p: 2,
                    }}
                >
                    {!files || files.length === 0 ? (
                        <Typography
                            color="text.secondary"
                            sx={{ textAlign: "center", py: 3 }}
                        >
                            No files selected
                        </Typography>
                    ) : (
                        <Box
                            sx={{
                                display: "flex",
                                flexDirection: "column",
                                gap: 1,
                            }}
                        >
                            {Array.from(files).map((file) => (
                                <Box
                                    key={`${file.name}-${file.lastModified}`}
                                    sx={{
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "space-between",
                                        gap: 2,
                                    }}
                                >
                                    <Typography
                                        variant="body2"
                                        sx={{
                                            overflow: "hidden",
                                            textOverflow: "ellipsis",
                                            whiteSpace: "nowrap",
                                        }}
                                    >
                                        {file.name}
                                    </Typography>

                                    <IconButton
                                        type="button"
                                        size="small"
                                        aria-label={`Remove ${file.name}`}
                                        onClick={() => removeFile(file)}
                                    >
                                        <CloseIcon fontSize="small" />
                                    </IconButton>
                                </Box>
                            ))}
                        </Box>
                    )}
                </Paper>

                <Button
                    type="submit"
                    variant="contained"
                    disabled={!files || files.length === 0 || isGenerating}
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