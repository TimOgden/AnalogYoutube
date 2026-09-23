import { useEffect, useState } from "react";
import { getVideos } from "../api/videos";

interface VideoViewerProps {

}

export default function VideoViewer({ }: VideoViewerProps) {
    const [videos, setVideos] = useState([]);

    useEffect(() => {
        getVideos()
            .then((response: any) => {
                setVideos(response);
            })
            .catch(console.error);
    }, []);

    return (<>
    </>)
}