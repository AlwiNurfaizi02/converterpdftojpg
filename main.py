import streamlit as st
import fitz
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

def render_pdf_to_jpg(pdf_bytes: bytes, dpi: int):
    """Generator yg mengembalikan (nomor_halaman, bytes_gambar_JPG)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    zoom = dpi / 72  # 72 dpi = 100 % zoom
    mat = fitz.Matrix(zoom, zoom)
    for page_number, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat)
        yield page_number, pix.tobytes("jpeg")  # langsung JPG


if uploaded_files:
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for uploaded_file in uploaded_files:
            pdf_name = os.path.splitext(uploaded_file.name)[0]
            st.markdown(f"### {uploaded_file.name}")
            try:
                pdf_bytes = uploaded_file.read()  # simpan sekali
                page_count = 0
                for page_num, jpg_bytes in render_pdf_to_jpg(pdf_bytes, dpi):
                    page_count += 1
                    # ➜ Simpan ke ZIP (folder = nama PDF)
                    img_filename = f"{pdf_name}/page_{page_num}.jpg"
                    zipf.writestr(img_filename, jpg_bytes)

                    # ➜ Preview di Streamlit
                    st.image(
                        jpg_bytes,
                        caption=f"{pdf_name} • Halaman {page_num}",
                        use_container_width=True,
                    )
                st.success(f"✅ {uploaded_file.name} selesai ({page_count} halaman).")
  
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
