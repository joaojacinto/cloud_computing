import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from google.cloud import storage, vision, firestore
from google.api_core.exceptions import NotFound
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Muda para algo mais seguro em produção

# Variáveis de ambiente obrigatórias
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "analisadas")  # default

# Inicializar clientes Google Cloud só se possível
storage_client = vision_client = firestore_client = bucket = None
if GCS_BUCKET_NAME:
    storage_client = storage.Client()
    vision_client = vision.ImageAnnotatorClient()
    firestore_client = firestore.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
else:
    print("AVISO: A variável de ambiente GCS_BUCKET_NAME não está definida! A aplicação não irá funcionar.")

@app.route("/")
def home():
    if not GCS_BUCKET_NAME:
        return "Erro: A variável de ambiente GCS_BUCKET_NAME não está definida!", 500
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not GCS_BUCKET_NAME:
        return "Erro: A variável de ambiente GCS_BUCKET_NAME não está definida!", 500
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                file.save(temp_file.name)
                temp_path = temp_file.name

            # Upload para o Cloud Storage
            blob = bucket.blob(filename)
            blob.upload_from_filename(temp_path)

            # Cloud Vision API - labels
            with open(temp_path, "rb") as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            response = vision_client.label_detection(image=image)
            labels = [label.description for label in response.label_annotations]

            # Guardar resultados no Firestore
            doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document()
            doc_ref.set({
                "filename": filename,
                "labels": labels,
                "gcs_uri": f"gs://{GCS_BUCKET_NAME}/{filename}",
                "public_url": f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
            })

            # Apagar o ficheiro temporário
            os.remove(temp_path)

            flash("Upload and analysis successful!")
            return redirect(url_for("dashboard"))

    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    if not GCS_BUCKET_NAME:
        return "Erro: A variável de ambiente GCS_BUCKET_NAME não está definida!", 500
    images = []
    docs = firestore_client.collection(FIRESTORE_COLLECTION).stream()
    for doc in docs:
        data = doc.to_dict()
        blob = bucket.blob(data['filename'])
        try:
            blob.reload()
            images.append(data)
        except NotFound:
            continue
    return render_template("dashboard.html", imagens=images)


@app.route("/delete_image", methods=["POST"])
def delete_image():
    if not GCS_BUCKET_NAME:
        return "Erro: A variável de ambiente GCS_BUCKET_NAME não está definida!", 500
    filename = request.form.get("filename")
    if not filename:
        flash("Ficheiro não especificado.")
        return redirect(url_for("dashboard"))

    # Apagar do Storage
    blob = bucket.blob(filename)
    blob.delete()

    # Apagar do Firestore
    docs = firestore_client.collection(FIRESTORE_COLLECTION).where("filename", "==", filename).stream()
    for doc in docs:
        doc.reference.delete()

    flash(f"Imagem '{filename}' apagada com sucesso!")
    return redirect(url_for("dashboard"))

@app.route("/health")
def health():
    # Simples rota de health check para diagnóstico rápido
    return "ok", 200

if __name__ == "__main__":
    # Apenas para desenvolvimento local!
    app.run(host="0.0.0.0", port=8080, debug=True)
