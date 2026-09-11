import React from 'react';
import { Button } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

interface FileUploadProps {
    onFilesSelected: (files: File[]) => void;
} 

export default function FileUpload({
    onFilesSelected
    } : FileUploadProps) {

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
         if (!e.target.files) {
            return;
        }

        onFilesSelected(Array.from(e.target.files));

        // Allows selecting the same file again later if it was removed.
        e.target.value = "";
    };

    return (
        <Button
            component="label"
            variant="contained"
            startIcon={<CloudUploadIcon />}
        >
            Upload Files
            <input
                type="file"
                accept=".mp4,.mov,.avi,.mkv,.flv,.wmv,.webm"
                hidden
                multiple
                onChange={handleFileChange}
            />
        </Button>
    );
}