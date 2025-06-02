from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.cloud import upload_image

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        result = upload_image(request)
        if result['success']:
            flash("Upload and analysis successful!")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash(result['error'])
            return redirect(request.url)
    return render_template("upload.html")
