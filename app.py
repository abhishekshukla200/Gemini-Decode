from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Set Streamlit page config
st.set_page_config(
    page_title="GeminiDecode: Multilanguage Document Extraction by Gemini Pro",
    page_icon="🤖",
    layout="centered"
)

# Load environment variables and Gemini API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Header and description
st.header("GeminiDecode: Multilanguage Document Extraction by Gemini Pro")
text = (
    "Utilizing Gemini Pro AI, this project effortlessly extracts vital information "
    "from diverse multilingual documents, transcending language barriers with "
    "precision and efficiency for enhanced productivity and decision-making."
)
styled_text = f"<span style='font-family:serif;'>{text}</span>"
st.markdown(styled_text, unsafe_allow_html=True)

# Gemini Vision function
def get_gimini_response(system_prompt, image, user_prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([
        system_prompt,
        image,
        user_prompt
    ])
    return response.text


# Upload image
st.divider()
upload_files = st.file_uploader("Choose an image of the document:", type=["jpg", "jpeg", "png"])

# Handle image
image_parts = None
if upload_files is not None:
    image = Image.open(upload_files)
    st.image(image, caption="Uploaded Document", use_container_width=True)

    # ✅ Upload format supported by Gemini
    image_parts = {
        "mime_type": upload_files.type,
        "data": upload_files.getvalue()
    }
else:
    st.info("Please upload an image to begin")

# User query
user_question = st.text_input("What do you want to know?", placeholder='e.g., Explain the complete document in brief')

# Submit
submit = st.button("Submit")

if submit:
    if upload_files is None:
        st.warning("Please upload an image first.")
    elif not user_question.strip():
        st.warning("Please enter a question about the document.")
    else:
        with st.spinner("Analyzing document with Gemini..."):
            response = get_gimini_response(
                "You are an expert document analyst. Analyze this image and answer the question accordingly.",
                image_parts,
                user_question
            )
        st.subheader("The response is:")
        st.write(response)

