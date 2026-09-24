import YouTubeQRGenerator from "./cardGenerators/YouTubeQRGenerator";
import LocalUploadQRGenerator from "./cardGenerators/LocalUploadQRGenerator";
import Library from "./Library";
import { useState } from "react";


export default function QRGenerators() {
    const [isGenerating, setIsGenerating] = useState<boolean>(false);

    return (
        <main>
            <YouTubeQRGenerator isGenerating={isGenerating} setIsGenerating={setIsGenerating}/>
            <LocalUploadQRGenerator isGenerating={isGenerating} setIsGenerating={setIsGenerating}/>
            <Library isGenerating={isGenerating} setIsGenerating={setIsGenerating}/>
        </main>
    )
}