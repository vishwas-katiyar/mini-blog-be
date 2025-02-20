from flask import Blueprint, request, jsonify, send_file
from models.blog import Blog, db
from middleware.auth_middleware import jwt_required_custom
import os
from werkzeug.utils import secure_filename
from middleware.goFile import upload_to_supabase
import uuid
blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/posts", methods=["POST"])
@jwt_required_custom
def create_post(user_id):
    
    if "blog_image" not in request.files:
        return jsonify({"error": "Blog image is required"}), 400

    file = request.files["blog_image"]
    
    # Validate file
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Generate a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"

    # Upload image to Supabase Storage
    file.filename = unique_filename  # Rename file before passing to Supabase
    image_url, error = upload_to_supabase(file)

    if error:
        return jsonify({"error": "Failed to upload image to Supabase", "details": str(error)}), 500

    # Get form data
    title = request.form.get("title")
    category_name = request.form.get("category_name")
    content = request.form.get("content")

    if not all([title, category_name, content]):
        return jsonify({"error": "Missing required fields"}), 400

    # Save post details with image URL
    post = Blog(
        title=title,
        blog_image=image_url,  # Store Supabase image URL
        category_name=category_name,
        content=content,
        author_id=user_id
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created successfully", "image_url": image_url}), 201

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@blog_bp.route("/posts", methods=["GET"])
def get_posts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    posts = Blog.query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = [{
        "id": post.id,
        "title": post.title,
        "blog_image": post.blog_image,
        "category_name": post.category_name,
        "content": post.content,
        "author": {
            "id": post.author.id,
            "name": post.author.name,
            "email": post.author.email
        } if post.author else None,
        "created_at": post.created_at
    } for post in posts.items]

    return jsonify({
        "posts": result,
        "total": posts.total,
        "pages": posts.pages,
        "current_page": posts.page
    }), 200


@blog_bp.route("/posts/<int:post_id>", methods=["GET"])
def get_post_by_id(post_id):
    post = Blog.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    result = {
        "id": post.id,
        "title": post.title,
        "blog_image": post.blog_image,
        "category_name": post.category_name,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at
    }
    return jsonify(result), 200

@blog_bp.route("/<path:image_path>", methods=["GET"])
def get_image(image_path):
    image_path = image_path.replace("\\", "/")
    full_path = os.path.normpath(image_path)

    if os.path.exists(full_path):
        return send_file(full_path, mimetype='image/jpeg')
    else:
        return {"error": "Image not found"}, 404
    
@blog_bp.route("/posts/<int:post_id>", methods=["PUT"])
@jwt_required_custom
def update_post(user_id, post_id):
    post = Blog.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    data = request.get_json()
    post.title = data.get("title", post.title)
    post.blog_image = data.get("blog_image", post.blog_image)
    post.category_name = data.get("category_name", post.category_name)
    post.content = data.get("content", post.content)
    
    db.session.commit()
    return jsonify({"message": "Post updated successfully"}), 200

@blog_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@jwt_required_custom
def delete_post(user_id, post_id):
    post = Blog.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"}), 200
