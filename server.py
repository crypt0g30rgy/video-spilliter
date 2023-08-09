from flask import Flask, render_template, request, send_file
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from werkzeug.utils import secure_filename  # Import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def split_video(video_path, output_folder):
    video_clip = VideoFileClip(video_path)
    duration = video_clip.duration
    parts = int(duration // 30)
    remaining_part_duration = duration % 30

    if remaining_part_duration > 0:
        parts += 1

    split_paths = []

    for i in range(parts):
        start_time = i * 30
        end_time = min((i + 1) * 30, duration)
        subclip = video_clip.subclip(start_time, end_time)
        split_path = os.path.join(output_folder, f'part_{i+1}.mp4')
        split_paths.append(split_path)
        subclip.write_videofile(split_path, codec='libx264')

    video_clip.close()
    return split_paths

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            split_paths = split_video(file_path, app.config['OUTPUT_FOLDER'])

            return render_template('download.html', split_paths=split_paths)

    return render_template('upload.html')


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    full_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(full_path, as_attachment=True)

@app.route('/download', methods=['GET'])
def download_page():
    split_paths = [
        os.path.basename(path) for path in os.listdir(app.config['OUTPUT_FOLDER'])
    ]
    return render_template('download.html', split_paths=split_paths)

if __name__ == '__main__':
    app.run(debug=True)