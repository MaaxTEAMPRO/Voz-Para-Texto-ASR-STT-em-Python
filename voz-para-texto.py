import sys
import subprocess
import os
import importlib.util

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    dependencies = {
        'flask': 'Flask==2.3.3',
        'speech_recognition': 'SpeechRecognition==3.10.0',
        'pyaudio': 'pyaudio==0.2.11',
        'pydub': 'pydub==0.25.1'
    }
    
    missing_packages = []
    
    print("🔍 Verificando dependências...")
    
    for module_name, package_name in dependencies.items():
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"📦 Encontradas {len(missing_packages)} dependências em falta:")
        for package in missing_packages:
            print(f"   - {package}")
        
        response = input("\n❓ Deseja instalar automaticamente? (s/n): ").lower().strip()
        
        if response in ['s', 'sim', 'y', 'yes']:
            print("\n⏳ Instalando dependências...")
            failed_packages = []
             
            for package in missing_packages:
                print(f"   Instalando {package}...")
                if install_package(package):
                    print(f"   ✅ {package} instalado com sucesso!")
                else:
                    print(f"  ❌ Erro ao instalar {package}")
                    failed_packages.append(package)
            
            if failed_packages:
                print(f"\n⚠️  Alguns pacotes falharam na instalação:")
                for package in failed_packages:
                    print(f"   - {package}")
                
                if 'pyaudio' in str(failed_packages):
                    print("❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌")
                    print(" ")
                    print("\n💡 Para resolver o erro do PyAudio:")
                    print(" ")
                    print("   Windows: pip install pipwin && pipwin install pyaudio")
                    print(" ")
                    print("   Mac:     brew install portaudio && pip install pyaudio")
                    print(" ")
                    print("   Ubuntu:  sudo apt-get install portaudio19-dev python3-pyaudio")
                
                input("\nPressione Enter após resolver os problemas...")
            else:
                print("\n🎉 Todas as dependências foram instaladas com sucesso!")
        else:
            print("\n❌ Instalação cancelada. Instale manualmente:")
            for package in missing_packages:
                print(f"   pip install {package}")
            sys.exit(1)
    else:
        print("✅ Todas as dependências estão disponíveis!")

check_and_install_dependencies()

try:
    from flask import Flask, render_template_string, request, jsonify, send_file
    import speech_recognition as sr
    import datetime
    from werkzeug.utils import secure_filename
    import tempfile
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("💡 Tente executar o script novamente ou instale manualmente as dependências.")
    sys.exit(1)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'main/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

os.makedirs('main', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

recognizer = sr.Recognizer()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcritor de Áudio v1.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 40px;
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .section {
            margin-bottom: 30px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .section h3 {
            color: #444;
            margin-bottom: 20px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .record-section {
            text-align: center;
        }
        
        .record-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
        }
        
        .record-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        }
        
        .record-btn:active {
            transform: translateY(0);
        }
        
        .record-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .upload-section {
            text-align: center;
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 30px;
            transition: all 0.3s ease;
        }
        
        .upload-section:hover {
            border-color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }
        
        .file-input {
            margin: 15px 0;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: white;
            width: 100%;
            max-width: 400px;
        }
        
        .btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 10px;
            cursor: pointer;
            margin: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn.danger {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            box-shadow: 0 3px 10px rgba(244, 67, 54, 0.3);
        }
        
        .btn.danger:hover {
            box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
        }
        
        .text-area {
            width: 100%;
            min-height: 250px;
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            resize: vertical;
            transition: border-color 0.3s ease;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .text-area:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .status {
            margin: 15px 0;
            padding: 15px 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            animation: fadeIn 0.3s ease;
        }
        
        .status.success {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: linear-gradient(135deg, #d1ecf1, #bee5eb);
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .hidden {
            display: none;
        }
        
        .controls {
            text-align: center;
            margin-top: 20px;
        }
        
        .pulse {
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .recording-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }
        
        .recording-dot {
            width: 10px;
            height: 10px;
            background: #ff0000;
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Transcritor de Áudio v1.0</h1>
        
        <!-- Seção de Gravação -->
        <div class="section record-section">
            <h3>🎙️ Gravação de Áudio</h3>
            <p style="margin-bottom: 20px; color: #666;">Clique no botão abaixo para gravar sua voz diretamente</p>
            <button id="recordBtn" class="record-btn">🎤 Iniciar Gravação</button>
            <button id="stopBtn" class="record-btn hidden pulse">
                <span class="recording-indicator">
                    <span class="recording-dot"></span>
                    ⏹️ Parar Gravação
                </span>
            </button>
            <div id="recordStatus" class="status hidden"></div>
        </div>
        
        <!-- Seção de Upload -->
        <div class="section upload-section">
            <h3>📤 Upload de Arquivo</h3>
            <p style="margin-bottom: 20px; color: #666;">Ou faça upload de um arquivo de áudio (WAV, MP3, M4A, etc.)</p>
            <input type="file" id="audioFile" class="file-input" accept="audio/*">
            <br>
            <button id="uploadBtn" class="btn">📤 Transcrever Arquivo</button>
        </div>
        
        <div id="status" class="status hidden"></div>
        
        <!-- Área de Texto -->
        <div class="section">
            <h3>📝 Texto Transcrito</h3>
            <textarea id="transcriptText" class="text-area" placeholder="O texto transcrito aparecerá aqui... Você pode editar após a transcrição."></textarea>
            <div class="controls">
                <button id="saveBtn" class="btn">💾 Salvar como TXT</button>
                <button id="clearBtn" class="btn danger">🗑️ Limpar Texto</button>
                <button id="copyBtn" class="btn" style="background: linear-gradient(135deg, #2196F3, #1976D2);">📋 Copiar Texto</button>
            </div>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const recordStatus = document.getElementById('recordStatus');
        const uploadBtn = document.getElementById('uploadBtn');
        const audioFile = document.getElementById('audioFile');
        const status = document.getElementById('status');
        const transcriptText = document.getElementById('transcriptText');
        const saveBtn = document.getElementById('saveBtn');
        const clearBtn = document.getElementById('clearBtn');
        const copyBtn = document.getElementById('copyBtn');
        
        // Event listeners
        recordBtn.addEventListener('click', startRecording);
        stopBtn.addEventListener('click', stopRecording);
        uploadBtn.addEventListener('click', uploadAudio);
        saveBtn.addEventListener('click', saveText);
        clearBtn.addEventListener('click', clearText);
        copyBtn.addEventListener('click', copyText);
        
        function showStatus(message, type = 'info') {
            status.textContent = message;
            status.className = `status ${type}`;
            status.classList.remove('hidden');
            setTimeout(() => {
                if (type === 'success') {
                    status.classList.add('hidden');
                }
            }, 3000);
        }
        
        function showRecordStatus(message, type = 'info') {
            recordStatus.textContent = message;
            recordStatus.className = `status ${type}`;
            recordStatus.classList.remove('hidden');
        }
        
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });
                
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    uploadAudioBlob(audioBlob, 'gravacao.webm');
                };
                
                mediaRecorder.start(1000); // Chunk a cada segundo
                
                recordBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                showRecordStatus('🔴 Gravando... Fale agora!', 'error');
                
            } catch (error) {
                showRecordStatus('❌ Erro ao acessar microfone: ' + error.message, 'error');
                console.error('Erro no microfone:', error);
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                
                recordBtn.classList.remove('hidden');
                stopBtn.classList.add('hidden');
                showRecordStatus('⏳ Processando gravação...', 'info');
            }
        }
        
        function uploadAudio() {
            const file = audioFile.files[0];
            if (!file) {
                showStatus('❌ Por favor, selecione um arquivo de áudio', 'error');
                return;
            }
            
            if (file.size > 16 * 1024 * 1024) {
                showStatus('❌ Arquivo muito grande! Máximo 16MB', 'error');
                return;
            }
            
            uploadAudioBlob(file, file.name);
        }
        
        function uploadAudioBlob(audioBlob, filename) {
            const formData = new FormData();
            formData.append('audio', audioBlob, filename);
            
            showStatus('🔄 Transcrevendo áudio... Aguarde um momento.', 'info');
            
            // Desabilitar botões durante o processamento
            uploadBtn.disabled = true;
            recordBtn.disabled = true;
            
            fetch('/transcribe', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showStatus('❌ Erro: ' + data.error, 'error');
                } else {
                    transcriptText.value = data.text;
                    showStatus('✅ Transcrição concluída com sucesso!', 'success');
                }
            })
            .catch(error => {
                showStatus('❌ Erro na transcrição: ' + error.message, 'error');
                console.error('Erro:', error);
            })
            .finally(() => {
                // Reabilitar botões
                uploadBtn.disabled = false;
                recordBtn.disabled = false;
                recordStatus.classList.add('hidden');
            });
        }
        
        function saveText() {
            const text = transcriptText.value.trim();
            if (!text) {
                showStatus('❌ Não há texto para salvar', 'error');
                return;
            }
            
            showStatus('💾 Salvando arquivo...', 'info');
            
            fetch('/save_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showStatus('❌ Erro ao salvar: ' + data.error, 'error');
                } else {
                    showStatus('✅ Arquivo salvo! Download iniciado.', 'success');
                    // Criar link de download
                    const link = document.createElement('a');
                    link.href = `/download/${data.filename}`;
                    link.download = data.filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            })
            .catch(error => {
                showStatus('❌ Erro ao salvar: ' + error.message, 'error');
            });
        }
        
        function clearText() {
            if (transcriptText.value.trim() && !confirm('Tem certeza que deseja limpar o texto?')) {
                return;
            }
            transcriptText.value = '';
            status.classList.add('hidden');
            recordStatus.classList.add('hidden');
            showStatus('🗑️ Texto limpo!', 'info');
        }
        
        function copyText() {
            const text = transcriptText.value.trim();
            if (!text) {
                showStatus('❌ Não há texto para copiar', 'error');
                return;
            }
            
            navigator.clipboard.writeText(text).then(() => {
                showStatus('📋 Texto copiado para a área de transferência!', 'success');
            }).catch(err => {
                showStatus('❌ Erro ao copiar texto', 'error');
                console.error('Erro ao copiar:', err);
            });
        }
        
        // Atalhos do teclado
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 's':
                        e.preventDefault();
                        saveText();
                        break;
                    case 'c':
                        if (document.activeElement === transcriptText) {
                            return; // Permitir cópia normal
                        }
                        e.preventDefault();
                        copyText();
                        break;
                }
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'Nenhum arquivo de áudio encontrado'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        filename = secure_filename(audio_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(temp_path)
        
        try:
            with sr.AudioFile(temp_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                
        except Exception as audio_error:
            try:
                from pydub import AudioSegment
                from pydub.silence import split_on_silence
                
                audio = AudioSegment.from_file(temp_path)
                wav_path = temp_path + '.wav'
                audio.export(wav_path, format="wav")
                
                with sr.AudioFile(wav_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
                    
            except Exception as convert_error:
                os.remove(temp_path)
                return jsonify({'error': f'Formato de áudio não suportado: {convert_error}'}), 400

        try:
            text = recognizer.recognize_google(audio_data, language='pt-BR')
            if not text.strip():
                text = "Áudio muito baixo ou sem fala detectada"
        except sr.UnknownValueError:
            text = "Não foi possível entender o áudio. Tente falar mais claramente ou verificar a qualidade do áudio."
        except sr.RequestError as e:
            text = f"Erro no serviço de reconhecimento: {e}. Verifique sua conexão com a internet."
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({'text': text})
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/save_text', methods=['POST'])
def save_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Texto vazio'}), 400
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcricao_{timestamp}.txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Transcrição de Áudio\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write(text)
            f.write(f"\n\n{'='*50}\n")
            f.write(f"Arquivo gerado automaticamente pelo Transcritor de Áudio\n")
        
        return jsonify({'message': 'Arquivo salvo com sucesso', 'filename': filename})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({'error': f'Erro no download: {str(e)}'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎤 TRANSCRITOR DE ÁUDIO PARA TEXTO V1.0")
    print("="*60)
    print("✅ Todas as dependências verificadas!")
    print(" ")
    print("📁 Arquivos serão salvos em: main/uploads/")
    print(" ")
    print("🌐 Servidor iniciando...")
    print(" ")
    print("⚠️  Mantenha este terminal aberto!")
    print(" ")
    print("🛑 Pressione Ctrl+C para parar o servidor")
    print(" ")
    print("🔗 Acesse em seu navegador: http://localhost:8080")
    print("="*60 + "\n")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        input("Pressione Enter para sair...")