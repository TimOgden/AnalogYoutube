import styles from "../styles/QRGenerator.module.less";
import FileUpload from "../common/FileUpload";
import { useState } from "react";
import { Box, IconButton, Paper, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";


interface LocalUploadQRGenerator {
    onFilesChange: (files: File[]) => void;
}


export default function LocalUploadQRGenerator({ onFilesChange }: LocalUploadQRGenerator) {
    const [files, setFiles] = useState<File[]>([]);

    function addFiles(newFiles: File[]) {
        setFiles((currentFiles) => {
            const updatedFiles = [...currentFiles, ...newFiles];
            onFilesChange(updatedFiles);
            return updatedFiles;
        });
    }

    function removeFile(fileToRemove: File) {
        setFiles((currentFiles) => {
            const updatedFiles = currentFiles.filter((file) => file !== fileToRemove);
            onFilesChange(updatedFiles);
            return updatedFiles;
        });
    }

    return (
        <section className={styles.card}>
            <h2>Create Cards from Local Files</h2>

            <p className={styles.description}>
                Upload local files below to generate printable QR cards.
            </p>

            <form className={styles.form}>
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
            </form>
        </section>
    );
}