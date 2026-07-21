import logging
import pathlib

import yt_dlp

logger = logging.getLogger(__name__)


class YoutubeDownloadError(RuntimeError):
    pass


def download_youtube_video(
    url: str,
    output_path: pathlib.Path,
) -> pathlib.Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    options = {
        # Prefer MP4-compatible 1080p video and M4A audio.
        "format": (
            "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]"
            "/best[height<=1080][ext=mp4]"
            "/best[height<=1080]"
        ),
        "merge_output_format": "mp4",
        "cookiesfrombrowser": ("chromium",),
        # yt-dlp expects a filename template. Since the extension may be
        # determined during extraction, omit it here.
        "outtmpl": str(output_path.with_suffix("")) + ".%(ext)s",

        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
        "retries": 5,
        "fragment_retries": 5,
        "player_client": "tv"
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)

            requested_downloads = info.get("requested_downloads") or []
            if requested_downloads:
                downloaded = requested_downloads[0].get("filepath")
                if downloaded:
                    result = pathlib.Path(downloaded)
                else:
                    result = pathlib.Path(
                        downloader.prepare_filename(info)
                    )
            else:
                result = pathlib.Path(
                    downloader.prepare_filename(info)
                )

        # Merging may have changed the final extension.
        mp4_path = output_path.with_suffix(".mp4")
        if mp4_path.exists():
            result = mp4_path

        logger.info(
            'Downloaded "%s" to %s',
            info.get("title", url),
            result,
        )
        return result

    except yt_dlp.utils.DownloadError as exc:
        logger.exception("YouTube download failed for %s", url)
        raise YoutubeDownloadError(str(exc)) from exc