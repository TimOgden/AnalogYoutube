import styles from "../styles/QRGenerator.module.less";
import FileUpload from "../common/FileUpload";
import { useState, type FormEvent } from "react";
import { submitFiles } from "../../api/qrGeneration";

export default function LocalUploadQRGenerator() {
    const [files, setFiles] = useState<FileList | null>(null);

    function addFiles(newFiles: FileList | File[]) {
        setFiles((currentFiles) => {
            const mergedFiles = [
                ...(currentFiles ? Array.from(currentFiles) : []),
                ...Array.from(newFiles),
            ];

            const dataTransfer = new DataTransfer();
            mergedFiles.forEach((file) => dataTransfer.items.add(file));
            return dataTransfer.files;
        });
    }

    function removeFile(fileToRemove: File) {
        if (!files || files.length === 0) return;

        const remainingFiles = Array.from(files).filter(
            (file) => file !== fileToRemove,
        );

        const dataTransfer = new DataTransfer();
        remainingFiles.forEach((file) => dataTransfer.items.add(file));
        setFiles(dataTransfer.files);
    }

    async function handleSubmit(e: FormEvent<HTMLFormElement>) {
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
    }

    return (
        <section className={styles.card}>
            <h2>Create Cards from Local Files</h2>

            <p className={styles.description}>
                Upload local files below to generate printable QR cards.
            </p>

            <form onSubmit={handleSubmit} className={styles.form}>
                {FileUpload((files) => addFiles(files ?? []))}
                {files && files.length > 0 && (
                    <div>
                        {Array.from(files).map((file) => (
                            <div key={`${file.name}-${file.lastModified}`}>
                                <span>{file.name}</span>
                                <input
                                    type="text"
                                    placeholder="Enter a title for this file..."
                                    onChange={(e) => {
                                        const title = e.target.value;
                                        
                                    }}
                                />
                                <button
                                    type="button"
                                    aria-label={`Remove ${file.name}`}
                                    onClick={() => removeFile(file)}
                                >
                                    x
                                </button>
                            </div>
                        ))}
                    </div>
                )}
                <button
                    type="submit"
                    disabled={!files || files.length === 0}
                >
                    Generate Cards
                </button>
            </form>
        </section>
    );
}