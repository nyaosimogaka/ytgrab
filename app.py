import streamlit as st
import yt_dlp
import mimetypes
import os

# Make ffmpeg executable
os.chmod('./ffmpeg', 0o755)

st.title("YouTube Downloader")

url = st.text_input("Enter YouTube Video/Livestream URL")

download_type = st.selectbox(
    "Select download type:",
    ["Merged (Audio + Video)", "Video only", "Audio only"]
)

if st.button("Download"):
    if url:
        with st.spinner("Downloading..."):
            os.makedirs("downloads", exist_ok=True)
            format_map = {
                "Video only": "bv[ext=mp4]/bv",
                "Audio only": "ba[ext=m4a]/ba",
                "Merged (Audio + Video)": "bv*+ba/best"
            }

            ydl_opts = {
                'format': format_map[download_type],
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': True
            }

            # Only set ffmpeg if merging is needed
            if download_type == "Merged (Audio + Video)":
                ydl_opts.update({
                    'ffmpeg_location': './ffmpeg',
                    'merge_output_format': 'mp4'
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                st.success("Download complete!")
                st.download_button(
                    label="Click to download file",
                    data=open(filename, "rb"),
                    file_name=os.path.basename(filename),
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid URL.")
