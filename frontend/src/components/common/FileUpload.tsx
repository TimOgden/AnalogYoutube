import React, { useState } from 'react';
import { Button } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

export default function FileUpload(setFiles: (files: FileList | null) => void) {

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFiles(e.target.files);
        console.log(e.target.files);
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
                hidden
                multiple
                onChange={handleFileChange}
            />
        </Button>
    );
}