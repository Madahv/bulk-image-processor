import streamlit as st
from PIL import Image
import io
import zipfile
import os
import re

st.set_page_config(layout="wide")

def clean_filename(name):
    return re.sub(r'[\/*?<>|":]', "_", name)

st.title("🖼️ Bulk Image Processor with Resize, Quality & ZIP Download")

with st.sidebar:
    st.header("⚙️ Global Settings")
    jpeg_quality = st.slider("Image Quality (%)", 10, 100, 80)
    resize_width_input = st.text_input("Resize Width (optional)", "")
    resize_height_input = st.text_input("Resize Height (optional)", "")

col_upload, col_download = st.columns([3, 1])

with col_upload:
    uploaded_files = st.file_uploader(
        "Upload Images (drag & drop supported)",
        type=["jpg", "jpeg", "png", "heic"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown("<p style='font-size:14px;'>Upload Images (drag & drop supported)</p>", unsafe_allow_html=True)

processed_images = []

if uploaded_files:
    with col_download:
        st.markdown("### 🗖️ Download All")

    for index, uploaded_file in enumerate(uploaded_files):
        safe_name = clean_filename(uploaded_file.name).lower()
        base_name, ext = os.path.splitext(safe_name)
        default_name = f"{base_name}_fd.jpg"

        image = Image.open(uploaded_file)
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        resize_width = int(resize_width_input) if resize_width_input.strip().isdigit() else image.width
        resize_height = int(resize_height_input) if resize_height_input.strip().isdigit() else image.height
        image = image.resize((resize_width, resize_height))

        default_clean_name = os.path.splitext(default_name)[0]

        # Create two columns: left for image, right for controls
        img_col, control_col = st.columns([3, 1])

        with img_col:
            st.image(image, caption=f"Preview: {safe_name}", use_column_width=False, width=250)

        with control_col:
            custom_name_input = st.text_input(
                f"Custom output filename for Image {index + 1}",
                value=default_clean_name,
                key=f"custom_name_{index}"
            )
            user_output_name = clean_filename(custom_name_input) + ".jpg"

            st.markdown(f"<p style='font-size:16px;margin-bottom:4px;'>Download: <b>{user_output_name}</b></p>", unsafe_allow_html=True)

            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG', quality=jpeg_quality)
            img_bytes.seek(0)

            st.download_button(
                label="⬇️ Download",
                data=img_bytes,
                file_name=user_output_name,
                mime="image/jpeg"
            )

        processed_images.append((user_output_name, image, img_bytes))

    if len(processed_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for filename, img, _ in processed_images:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="JPEG", quality=jpeg_quality)
                zip_file.writestr(filename, img_byte_arr.getvalue())

        zip_buffer.seek(0)
        with col_download:
            st.download_button(
                label="⬇️ Download All as ZIP",
                data=zip_buffer,
                file_name="processed_images.zip",
                mime="application/zip"
            )
