import YouTubeQRGenerator from "./cardGenerators/YouTubeQRGenerator";
import LocalUploadQRGenerator from "./cardGenerators/LocalUploadQRGenerator";
import Library from "./Library";

export default function QRGenerators() {
    return (
        <main>
            <YouTubeQRGenerator />
            <LocalUploadQRGenerator />
            <Library />
        </main>
    )
}