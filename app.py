import streamlit as st
import yt_dlp
import mimetypes
import os
import glob
import ffmpeg

st.title("YouTube Downloader")

url = st.text_input("Enter YouTube Video/Livestream URL")

download_type = st.selectbox(
    "Select download type:",
    ["Merged (Audio + Video)", "Video only", "Audio only"]
)

if st.button("Download"):
    if url:
        with st.spinner("Downloading..."):
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            for file in glob.glob(f"{downloads_dir}/*"):
                os.remove(file)

            format_map = {
                "Video only": "bv[ext=mp4]/bv",
                "Audio only": "ba[ext=m4a]/ba",
                "Merged (Audio + Video)": "bv[ext=mp4]+ba[ext=m4a]/best"
            }

            ydl_opts = {
                'format': format_map[download_type],
                'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
                'quiet': True,
                'noplaylist': True
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)

                    if download_type == "Merged (Audio + Video)":
                        video_title = info.get("title", "video")
                        base = f"{downloads_dir}/{video_title}"
                        video_file = glob.glob(f"{base}.mp4")[0]  # get video
                        audio_file = glob.glob(f"{base}.m4a")[0]  # get audio
                        merged_file = f"{base}_merged.mp4"

                        ffmpeg.input(video_file).output(audio_file, merged_file, v=1, a=1, strict='experimental').run(overwrite_output=True)
                        filename = merged_file
                    else:
                        filename = yt_dlp.utils.std_headers['outtmpl'] if 'outtmpl' in ydl_opts else ydl.prepare_filename(info)

                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                st.success("Download complete!")

                with open(filename, "rb") as f:
                    file_bytes = f.read()

                if mime_type.startswith("video"):
                    st.video(file_bytes)

                st.download_button(
                    label="Click to download file",
                    data=file_bytes,
                    file_name=os.path.basename(filename),
                    mime=mime_type
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid URL.")
