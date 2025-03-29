import cv2
import face_recognition
import numpy as np
import DAO
import threading
from flask import Flask, render_template, jsonify

app = Flask(__name__)


lista_presenca = set()
lock = threading.Lock()
frame_lock = threading.Lock()
frame_disponivel = threading.Event()
frame_atual = None

rostos_cadastrados = DAO.buscar_todas_pessoas()

codificacoes_cadastradas = []
nomes_cadastrados = []

for _, nome, img in rostos_cadastrados:
    np_arr = np.frombuffer(img, np.uint8)
    imagem = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

    encodings = face_recognition.face_encodings(imagem_rgb)
    if encodings:
        codificacoes_cadastradas.append(encodings[0])
        nomes_cadastrados.append(nome)

webCam = cv2.VideoCapture(0)

def comparar_rosto(cod_rosto, banco_encodings, resultados, lock):
    distancias = face_recognition.face_distance(banco_encodings, cod_rosto)
    melhor_match = np.argmin(distancias) if len(distancias) > 0 else None

    if melhor_match is not None and resultados[melhor_match]:
        nome = nomes_cadastrados[melhor_match]
        with lock:
            if nome not in lista_presenca:
                lista_presenca.add(nome)
                print(f"Presença registrada: {nome}")
def produtor():
    global frame_atual
    while True:
        verificador, frame = webCam.read()
        if not verificador:
            break

        with frame_lock:
            frame_atual = frame

        frame_disponivel.set()
        frame_disponivel.wait()

        locais_rostos = face_recognition.face_locations(frame)
        codificacoes_rostos = face_recognition.face_encodings(frame, locais_rostos)

        if codificacoes_rostos:
            threads = []

            for cod_rosto, local_rosto in zip(codificacoes_rostos, locais_rostos):
                thread = threading.Thread(target=comparar_rosto, args=(cod_rosto, codificacoes_cadastradas, face_recognition.compare_faces(codificacoes_cadastradas, cod_rosto), lock))
                threads.append(thread)
                thread.start()

                top, right, bottom, left = local_rosto
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                distancias = face_recognition.face_distance(codificacoes_cadastradas, cod_rosto)
                melhor_match = np.argmin(distancias) if len(distancias) > 0 else None
                if melhor_match is not None:
                    nome = nomes_cadastrados[melhor_match]
                    cv2.putText(frame, nome, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            for thread in threads:
                thread.join()

        cv2.imshow("Reconhecimento Facial", frame)
        cv2.waitKey(1)

        frame_disponivel.clear()

    webCam.release()
    cv2.destroyAllWindows()

app.run(debug=True, use_reloader=False)

