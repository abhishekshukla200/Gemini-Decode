import base64
import os

from dotenv import load_dotenv
from flask import Flask, render_template_string, request
import google.generativeai as genai


load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GeminiDecode</title>
    <style>
      :root {
        color-scheme: light;
        --ink: #17211d;
        --muted: #60716b;
        --surface: #fffaf1;
        --panel: #ffffff;
        --line: #d8dfd2;
        --accent: #0f766e;
        --accent-strong: #0b4f49;
        --warn: #a14516;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: Georgia, "Times New Roman", serif;
        color: var(--ink);
        background:
          linear-gradient(135deg, rgba(15, 118, 110, 0.14), transparent 34%),
          linear-gradient(315deg, rgba(161, 69, 22, 0.12), transparent 38%),
          var(--surface);
      }

      main {
        width: min(960px, calc(100% - 32px));
        margin: 0 auto;
        padding: 48px 0;
      }

      h1 {
        margin: 0;
        font-size: clamp(2rem, 5vw, 4rem);
        line-height: 1;
      }

      .intro {
        max-width: 760px;
        margin: 18px 0 28px;
        color: var(--muted);
        font-size: 1.1rem;
        line-height: 1.7;
      }

      .workspace {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(280px, 360px);
        gap: 20px;
        align-items: start;
      }

      form,
      .result {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.86);
        box-shadow: 0 20px 50px rgba(23, 33, 29, 0.08);
      }

      form {
        padding: 22px;
      }

      label {
        display: block;
        margin-bottom: 8px;
        font-weight: 700;
      }

      input,
      textarea,
      button {
        width: 100%;
        font: inherit;
      }

      input[type="file"],
      textarea {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: var(--panel);
      }

      input[type="file"] {
        padding: 12px;
      }

      textarea {
        min-height: 130px;
        margin-bottom: 18px;
        padding: 14px;
        resize: vertical;
      }

      button {
        border: 0;
        border-radius: 6px;
        padding: 14px 18px;
        color: #ffffff;
        background: var(--accent);
        cursor: pointer;
      }

      button:hover {
        background: var(--accent-strong);
      }

      .field {
        margin-bottom: 18px;
      }

      .result {
        overflow: hidden;
      }

      .result img {
        display: block;
        width: 100%;
        max-height: 320px;
        object-fit: contain;
        background: #f5f2ea;
        border-bottom: 1px solid var(--line);
      }

      .answer {
        padding: 20px;
        white-space: pre-wrap;
        line-height: 1.65;
      }

      .notice {
        color: var(--warn);
        font-weight: 700;
      }

      @media (max-width: 780px) {
        main {
          padding-top: 32px;
        }

        .workspace {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <main>
      <h1>GeminiDecode</h1>
      <p class="intro">
        Extract useful answers from multilingual document images with Gemini.
      </p>

      <section class="workspace">
        <form method="post" enctype="multipart/form-data">
          <div class="field">
            <label for="document">Document image</label>
            <input id="document" name="document" type="file" accept="image/png,image/jpeg" required>
          </div>

          <div class="field">
            <label for="question">Question</label>
            <textarea id="question" name="question" placeholder="Explain the complete document in brief" required>{{ question }}</textarea>
          </div>

          <button type="submit">Analyze document</button>
        </form>

        {% if error or answer %}
          <aside class="result">
            {% if image_data %}
              <img src="{{ image_data }}" alt="Uploaded document preview">
            {% endif %}
            <div class="answer {% if error %}notice{% endif %}">{{ error or answer }}</div>
          </aside>
        {% endif %}
      </section>
    </main>
  </body>
</html>
"""


def get_gemini_response(system_prompt, image, user_prompt):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured in Vercel environment variables.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content([system_prompt, image, user_prompt])
    return response.text


def format_gemini_error(exc):
    message = str(exc)
    lower_message = message.lower()

    if "api key was reported as leaked" in lower_message:
        return (
            "This Gemini API key has been blocked because Google detected it as leaked. "
            "Create a new key in Google AI Studio, add it to Vercel as GEMINI_API_KEY, "
            "remove the old leaked key, and redeploy."
        )

    if "api key not valid" in lower_message or "permission_denied" in lower_message:
        return (
            "The Gemini API key is invalid or does not have access. "
            "Check the GEMINI_API_KEY value in Vercel and redeploy."
        )

    return "Gemini could not process this request. Please check the API key, model, and quota."


@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    error = None
    image_data = None
    question = ""

    if request.method == "POST":
        uploaded_file = request.files.get("document")
        question = request.form.get("question", "").strip()

        if not uploaded_file or not uploaded_file.filename:
            error = "Please upload an image first."
        elif not question:
            error = "Please enter a question about the document."
        else:
            image_bytes = uploaded_file.read()
            image = {
                "mime_type": uploaded_file.mimetype,
                "data": image_bytes,
            }
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            image_data = f"data:{uploaded_file.mimetype};base64,{encoded_image}"

            try:
                answer = get_gemini_response(
                    "You are an expert document analyst. Analyze this image and answer the question accordingly.",
                    image,
                    question,
                )
            except Exception as exc:
                error = format_gemini_error(exc)

    return render_template_string(
        PAGE_TEMPLATE,
        answer=answer,
        error=error,
        image_data=image_data,
        question=question,
    )
