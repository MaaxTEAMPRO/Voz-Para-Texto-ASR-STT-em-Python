# Voz-Para-Texto-ASR-STT-em-Python


🎤 TRANSCRITOR DE ÁUDIO PARA TEXTO
=====================================

📋 INSTRUÇÕES RÁPIDAS:
----------------------

1. 📥 BAIXAR/SALVAR:
   - Salve o arquivo Python como "transcritor.py" ou outro nome ".py"
   - Coloque na pasta que você quiser

2. 🚀 EXECUTAR:
   - Abra o terminal/prompt na pasta do arquivo
   - Digite: python transcritor.py
   - Aguarde a instalação automática das dependências

3. 🌐 USAR:
   - Abra seu navegador
   - Vá para: http://localhost:8080
   - Pronto! Interface funcionando

📁 ESTRUTURA DOS ARQUIVOS:
-------------------------
📂 Sua pasta/
├── 📄 transcritor.py (arquivo principal)

├── 📂 main/
    └── 📂 uploads/ (arquivos salvos aqui)

✨ FUNCIONALIDADES:
------------------

🎙️ Gravar áudio direto no navegador

📤 Upload de arquivos de áudio (MP3, WAV, M4A...)

✏️ Editar texto transcrito

💾 Salvar como arquivo TXT

📋 Copiar texto

🗑️ Limpar texto

🔧 INSTALAÇÃO AUTOMÁTICA:
------------------------
O programa instala automaticamente:
- Flask (servidor web)
- SpeechRecognition (reconhecimento de voz)
- PyAudio (gravação de áudio)
- Pydub (conversão de áudio)


⚠️ PROBLEMAS COMUNS:
-------------------

❌ Erro do PyAudio:
Windows: pip install pipwin && pipwin install pyaudio
Ubuntu: sudo apt-get install portaudio19-dev python3-pyaudio  
Mac: brew install portaudio && pip install pyaudio

❌ Microfone não funciona:
- Permita acesso ao microfone no navegador
- Teste em Chrome/Edge (melhor compatibilidade)

❌ Transcrição ruim:
- Fale claramente e pausadamente
- Evite ruído de fundo
- Use fones de ouvido com microfone

🆘 SUPORTE:
-----------
- Verifique sua conexão com internet (usa Google Speech API)
- Teste com arquivos pequenos primeiro
- Mantenha o terminal aberto enquanto usa

✅ TESTADO EM:
--------------
- Windows 10/11
- macOS
- Ubuntu/Linux
- Chrome, Firefox, Edge

🎯 DICAS DE USO:
----------------
📝 Para melhor transcrição:
- Fale em ritmo normal (nem muito rápido, nem muito devagar)
- Pause entre frases
- Evite gírias muito específicas
- Use pontuação natural na fala ("ponto", "vírgula")

🎙️ Para gravação:
- Microfone próximo da boca (15-20cm)
- Ambiente silencioso
- Evite eco (quartos com tapetes/cortinas são melhores)

💾 Arquivos salvos:
- Ficam em main/uploads/
- Nome automático com data/hora
- Formato: transcricao_AAAAMMDD_HHMMSS.txt

⌨️ ATALHOS DO TECLADO:
---------------------
Ctrl+S = Salvar arquivo
Ctrl+C = Copiar texto (quando não estiver editando)

🔄 VERSÕES SUPORTADAS:
----------------------
Python 3.6+ (recomendado Python 3.8+)

📞 CONTATO/AJUDA:
-----------------
Se tiver problemas, verifique:
1. Python instalado corretamente
2. Conexão com internet funcionando
3. Permissões do microfone no navegador
4. Antivírus não bloqueando o programa

💡 MELHORIAS FUTURAS:
--------------------
- Suporte offline
- Mais idiomas
- Reconhecimento de múltiplas vozes
- Export para Word/PDF

=====================================

Criado com ❤️ para facilitar sua vida!

=====================================
