import streamlit as st
import yt_dlp
import mimetypes
import os
import glob

# Ensure ffmpeg is executable
# os.chmod('./ffmpeg', 0o755)

st.title("YouTube Downloader")

# Input URL
url = st.text_input("Enter YouTube Video/Livestream URL")

# Choose download type
download_type = st.selectbox(
    "Select download type:",
    ["Merged (Audio + Video)", "Video only", "Audio only"]
)

if st.button("Download"):
    if url:
        with st.spinner("Downloading..."):
            # Create /downloads directory if not exists
            downloads_dir = "downloads"
            os.makedirs(downloads_dir, exist_ok=True)

            # Optional: Clean up old files
            for file in glob.glob(f"{downloads_dir}/*"):
                os.remove(file)

            # Format selection
            format_map = {
                "Video only": "bv[ext=mp4]/bv",
                "Audio only": "ba[ext=m4a]/ba",
                "Merged (Audio + Video)": "bv*+ba/best"
            }

            ydl_opts = {
                'format': format_map[download_type],
                'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
                'quiet': True
            }

            if download_type == "Merged (Audio + Video)":
                ydl_opts.update({
                    'ffmpeg_location': './ffmpeg',
                    'merge_output_format': 'mp4'
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                # Guess MIME type
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

                st.success("Download complete!")

                with open(filename, "rb") as f:
                    file_bytes = f.read()

                # Playback (only if video format)
                if mime_type.startswith("video"):
                    st.video(file_bytes)

                # Download button
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
