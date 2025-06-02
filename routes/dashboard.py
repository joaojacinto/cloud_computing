from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.cloud import get_images, delete_image_from_cloud

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    images, page, total_pages = get_images(request)
    return render_template(
        "dashboard.html",
        images=images,
        page=page,
        total_pages=total_pages
    )

@dashboard_bp.route("/delete_image", methods=["POST"])
def delete_image():
    filename = request.form.get("filename")
    msg = delete_image_from_cloud(filename)
    flash(msg)
    return redirect(url_for("dashboard.dashboard"))
