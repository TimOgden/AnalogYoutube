import YouTubeQRGenerator from "./cardGenerators/YouTubeQRGenerator";
import LocalUploadQRGenerator from "./cardGenerators/LocalUploadQRGenerator";
import Library from "./Library";
import { useState } from "react";
import { CircularProgress, Fab } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { generateCards } from "../api/qrGeneration";
import type { SelectedLibraryVideo } from "../api/library";


export default function QRGenerators() {
    const [isGenerating, setIsGenerating] = useState<boolean>(false);
    const [youtubeUrls, setYoutubeUrls] = useState<string[]>([]);
    const [localFiles, setLocalFiles] = useState<File[]>([]);
    const [librarySelections, setLibrarySelections] = useState<
        SelectedLibraryVideo[]
    >([]);
    const [resetVersion, setResetVersion] = useState(0);

    const handleSubmit = async () => {
        setIsGenerating(true);
        try {
            const blob = await generateCards(
                librarySelections,
                localFiles,
                youtubeUrls
            );
            const downloadUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = downloadUrl;
            a.download = "qr-cards.zip";
            a.click();

            URL.revokeObjectURL(downloadUrl);
            
            setYoutubeUrls([]);
            setLocalFiles([]);
            setLibrarySelections([]);
            setResetVersion((version) => version + 1);
        } finally {
            setIsGenerating(false);
        }
    };

    const selectionCount =
        librarySelections.length + localFiles.length + youtubeUrls.length;

    return (
        <main>
            <YouTubeQRGenerator
                onUrlsChange={setYoutubeUrls}
                resetVersion={resetVersion}
            />
            <LocalUploadQRGenerator
                onFilesChange={setLocalFiles}
                resetVersion={resetVersion}
            />
            <Library
                onSelectionChange={setLibrarySelections}
                resetVersion={resetVersion}
            />
            {selectionCount > 0 && (
                    <Fab
                        variant="extended"
                        color="primary"
                        sx={{
                            position: "fixed",
                            right: 24,
                            bottom: 24,
                            zIndex: 1100,
                        }}
                        onClick={handleSubmit}
                        disabled={isGenerating}
                        aria-label={`Submit ${selectionCount} selected items`}
                    >
                        {isGenerating ? (
                            <>
                                <CircularProgress
                                    size={20}
                                    color="inherit"
                                    sx={{ mr: 1 }}
                                />
                                Generating...
                            </>
                        ) : (
                            <>
                                <SendIcon sx={{ mr: 1 }} />
                                Submit ({selectionCount})
                            </>
                        )}
                    </Fab>
                )}
        </main>

    )
}