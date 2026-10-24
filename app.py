import io
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import streamlit as st
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

st.set_page_config(page_title="LipiBridge Pro", layout="wide")
st.title("🌐 LipiBridge Pro: PDF Transliteration Platform")

uploaded_file = st.file_uploader("Apna PDF upload karo", type=["pdf"])

if uploaded_file is not None:
  st.info(
      "File process ho rahi hai... Text, OCR aur Tables extract ki ja rahi"
      " hain."
  )
  extracted_content = []

  try:
    with pdfplumber.open(uploaded_file) as pdf:
      for page_idx, page in enumerate(pdf.pages):
        page_text = page.extract_text()
        tables = page.extract_tables()

        # Text Transliteration
        if page_text and len(page_text.strip()) > 20:
          t_text = transliterate(
              page_text, sanscript.DEVANAGARI, sanscript.ITRANS
          )
          extracted_content.append(
              f"--- Page {page_idx + 1} (Text) ---\n{t_text}"
          )

        # Tables Transliteration
        if tables:
          for t_idx, table in enumerate(tables):
            t_table = []
            for row in table:
              t_row = [
                  transliterate(
                      str(cell) if cell else "",
                      sanscript.DEVANAGARI,
                      sanscript.ITRANS,
                  )
                  for cell in row
              ]
              t_table.append(" | ".join(t_row))
            extracted_content.append(
                f"\n[Table {t_idx + 1} on Page {page_idx + 1}]\n"
                + "\n".join(t_table)
                + "\n"
            )

        # Scanned / Photo PDF ke liye OCR Fallback
        if not page_text or len(page_text.strip()) < 10:
          doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
          pix = doc[page_idx].get_pixmap(dpi=300)
          img = Image.open(io.BytesIO(pix.tobytes("png")))

          ocr_text = pytesseract.image_to_string(img, lang="hin+eng")
          t_ocr = transliterate(ocr_text, sanscript.DEVANAGARI, sanscript.ITRANS)
          extracted_content.append(
              f"--- Page {page_idx + 1} (Scanned OCR) ---\n" + t_ocr
          )

    final_output = "\n\n".join(extracted_content)
    st.subheader("Result Output")
    st.text_area("Transliterated Text", final_output, height=400)

    st.download_button(
        "Download Text File",
        data=final_output,
        file_name="output.txt",
        mime="text/plain",
    )

  except Exception as e:
    st.error(f"Error aaya: {e}")
