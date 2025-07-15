import streamlit as st
from pdf2image import convert_from_bytes
from io import BytesIO
from zipfile import ZipFile
import os

st.set_page_config(page_title="PDF JPG ", page_icon="")
st.title("konversi Banyak PDF ke JPG + Preview (maks. 10 PDF)")

MAX_FILES = 10

uploaded_files = st.file_uploader(
    "Unggah PDF (maks. 10 file sekaligus)",
    type=["pdf"],
    accept_multiple_files=True
)

dpi = st.number_input("Resolusi (DPI)", min_value=72, max_value=600, value=200)


if uploaded_files and len(uploaded_files) > MAX_FILES:
    st.error(f"Kamu mengunggah {len(uploaded_files)} file. Batasnya {MAX_FILES}. "
             "Hapus beberapa file lalu coba lagi.")
    st.stop() 


if uploaded_files:
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for uploaded_file in uploaded_files:
            pdf_name = os.path.splitext(uploaded_file.name)[0]
            st.markdown(f"### {uploaded_file.name}")

            try:
                images = convert_from_bytes(uploaded_file.read(), dpi=dpi)
                for i, img in enumerate(images, start=1):
                    
                    img_buffer = BytesIO()
                    img.save(img_buffer, format="JPEG", quality=95)
                    img_bytes = img_buffer.getvalue()

                    
                    img_filename = f"{pdf_name}/page_{i}.jpg"
                    zipf.writestr(img_filename, img_bytes)

                    
                    st.image(img_bytes,
                             caption=f"{pdf_name} • Halaman {i}",
                             use_container_width=True)

                st.success(f"{uploaded_file.name} dikonversi ({len(images)} halaman).")

            except Exception as e:
                st.error(f"Gagal mengonversi {uploaded_file.name}: {e}")

    st.markdown("---")
    st.download_button(
        "Unduh Semua Gambar (ZIP Terstruktur)",
        data=zip_buffer.getvalue(),
        file_name="pdf_to_jpg_output.zip",
        mime="application/zip"
    )
else:
    st.info("Silakan unggah hingga 10 file PDF untuk mulai konversi.")
