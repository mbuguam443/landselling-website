from django.conf import settings
from django.http import HttpResponse, Http404
import os
from django.views import View

def serve_land_image(request, filename):
    """
    Serve images from the landImage directory
    """
    # Security: only allow image files with safe names
    if not filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise Http404("Invalid file type")
    
    # Prevent directory traversal attacks
    if '..' in filename or '/' in filename or '\\' in filename:
        raise Http404("Invalid file path")
    
    # Construct the file path
    land_image_dir = os.path.join(settings.BASE_DIR, 'landImage')
    file_path = os.path.join(land_image_dir, filename)
    
    # Check if file exists
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("Image not found")
    
    # Determine content type based on file extension
    content_type = 'image/jpeg'  # default
    if filename.endswith('.png'):
        content_type = 'image/png'
    elif filename.endswith('.gif'):
        content_type = 'image/gif'
    
    # Read and serve the file
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=content_type)
        return response