import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash
from google.cloud import storage, vision, firestore
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
bucket_name = os.getenv("GCS_BUCKET_NAME")
collection_name = os.getenv("FIRESTORE_COLLECTION", "analisadas")

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client()

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["image"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                file.save(tmp.name)
                temp_path = tmp.name

            blob = storage_client.bucket(bucket_name).blob(file.filename)
            blob.upload_from_filename(temp_path)

            with open(temp_path, "rb") as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = vision_client.label_detection(image=image)
            labels = [label.description for label in response.label_annotations]

            db.collection(collection_name).add({
                "filename": file.filename,
                "url": f"https://storage.googleapis.com/{bucket_name}/{file.filename}",
                "labels": labels
            })

            flash("Upload and analysis successful!")
            return redirect(url_for("dashboard"))
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    imagens = []
    docs = db.collection(collection_name).stream()
    for doc in docs:
        data = doc.to_dict()
        imagens.append(data)
    return render_template("dashboard.html", imagens=imagens)

if __name__ == "__main__":
    app.run(debug=True)
