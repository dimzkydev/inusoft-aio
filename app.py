import os
import re
import tempfile
import random
from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp

app = Flask(__name__)

# Konfigurasi yt-dlp
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'format': 'best',
}

def is_valid_tiktok_url(url):
    """Validasi URL TikTok"""
    tiktok_pattern = r'^(https?://)?(www\.)?(vm\.|vt\.|tiktok\.com/@.+/video/|tiktok\.com/t/).+'
    return re.match(tiktok_pattern, url) is not None

def download_video(url):
    """Mengunduh video TikTok dan mengembalikan informasi video"""
    temp_dir = tempfile.gettempdir()
    random_num = random.randint(10000, 99999)
    filename = f"tikvm-{random_num}.mp4"
    file_path = os.path.join(temp_dir, filename)
    
    opts = ydl_opts.copy()
    opts['outtmpl'] = file_path
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            return file_path
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms-of-service')
def tos_privacy():
    return render_template('tos-privacy.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'URL tidak boleh kosong'}), 400
    
    if not is_valid_tiktok_url(url):
        return jsonify({'error': 'URL TikTok tidak valid'}), 400
    
    file_path = download_video(url)
    
    if file_path and os.path.exists(file_path):
        # Kirim file sebagai response
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
            mimetype='video/mp4'
        )
    else:
        return jsonify({'error': 'Gagal mengunduh video'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)