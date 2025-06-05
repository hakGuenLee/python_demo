import os
from flask import Flask, render_template, request, send_file, after_this_request
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=['POST'])
def convert():
    if 'file' not in request.files:
        return "파일이 업로드되지 않았습니다.", 400
    
    file = request.files['file']
    if file.filename == '':
        return "파일이 선택되지 않았습니다.", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(wav_path)
        
        mp3_filename = filename.rsplit('.', 1)[0] + '.mp3'
        mp3_path = os.path.join(app.config['CONVERTED_FOLDER'], mp3_filename)
        
        sound = AudioSegment.from_wav(wav_path)
        sound.export(mp3_path, format="mp3")

        # 메모리에 mp3 파일 읽기
        with open(mp3_path, 'rb') as f:
            mp3_data = BytesIO(f.read())

        # 파일 삭제는 지금 즉시 가능 (파일 핸들 닫힌 상태)
        os.remove(wav_path)
        os.remove(mp3_path)

        # 응답에 메모리 파일을 첨부해서 전송
        mp3_data.seek(0)
        return send_file(mp3_data, as_attachment=True, download_name=mp3_filename, mimetype='audio/mpeg')
    else:
        return "wav 파일만 업로드 가능합니다.", 400

if __name__ == "__main__":
    app.run(debug=True)
