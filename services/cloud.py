import os
from google.cloud import storage, vision, firestore
from google.api_core.exceptions import NotFound
from werkzeug.utils import secure_filename
import tempfile

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "analisadas")

storage_client = vision_client = firestore_client = bucket = None
if GCS_BUCKET_NAME:
    storage_client = storage.Client()
    vision_client = vision.ImageAnnotatorClient()
    firestore_client = firestore.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

def upload_image(request):
    if not GCS_BUCKET_NAME:
        return {"success": False, "error": "GCS_BUCKET_NAME missing"}
    if "file" not in request.files:
        return {"success": False, "error": "No file part"}
    file = request.files["file"]
    if file.filename == "":
        return {"success": False, "error": "No selected file"}
    if file:
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        blob = bucket.blob(filename)
        blob.upload_from_filename(temp_path)
        blob.reload()
        file_size = blob.size
        upload_time = blob.updated

        with open(temp_path, "rb") as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = vision_client.label_detection(image=image)
        labels = []
        for label in response.label_annotations:
            labels.append({
                "description": label.description,
                "score": label.score
            })

        doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document()
        doc_ref.set({
            "filename": filename,
            "labels": labels,
            "gcs_uri": f"gs://{GCS_BUCKET_NAME}/{filename}",
            "public_url": f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}",
            "size": file_size,
            "uploaded_at": upload_time.isoformat() if upload_time else None
        })

        os.remove(temp_path)
        return {"success": True}
    return {"success": False, "error": "Unknown error"}

def get_images(request):
    if not GCS_BUCKET_NAME:
        return [], 1, 1
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

    per_page = 3
    page = request.args.get('page', 1, type=int)
    total = len(images)
    images = sorted(images, key=lambda x: x.get("filename"))
    start = (page - 1) * per_page
    end = start + per_page
    paginated = images[start:end]
    total_pages = (total + per_page - 1) // per_page
    return paginated, page, total_pages

def delete_image_from_cloud(filename):
    if not GCS_BUCKET_NAME:
        return "Erro: GCS_BUCKET_NAME não definida!"
    if not filename:
        return "Ficheiro não especificado."
    blob = bucket.blob(filename)
    blob.delete()
    docs = firestore_client.collection(FIRESTORE_COLLECTION).where("filename", "==", filename).stream()
    for doc in docs:
        doc.reference.delete()
    return f"Imagem '{filename}' apagada com sucesso!"
