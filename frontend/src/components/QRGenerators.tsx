import YouTubeQRGenerator from "./cardGenerators/YouTubeQRGenerator";
import LocalUploadQRGenerator from "./cardGenerators/LocalUploadQRGenerator";

export default function QRGenerators() {
    return (
        <main>
            <YouTubeQRGenerator />
            <LocalUploadQRGenerator />
        </main>
    )
}