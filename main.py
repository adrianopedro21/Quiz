import json
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "chave-secreta-para-session"

# 📁 Carrega perguntas do JSON
try:
    with open('perguntas.json', encoding='utf-8') as f:
        todas_perguntas = json.load(f)
    print("✅ Arquivo JSON carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar o arquivo JSON: {e}")
    todas_perguntas = []

# 🔀 Seleciona exatamente 10 perguntas por nível na ordem correta
def selecionar_perguntas():
    try:
        faceis = [p for p in todas_perguntas if p.get('nivel') == 'fácil']
        medias = [p for p in todas_perguntas if p.get('nivel') == 'médio']
        dificeis = [p for p in todas_perguntas if p.get('nivel') == 'difícil']

        selecionadas_faceis = random.sample(faceis, min(10, len(faceis)))
        selecionadas_medias = random.sample(medias, min(10, len(medias)))
        selecionadas_dificeis = random.sample(dificeis, min(10, len(dificeis)))

        perguntas_ordenadas = selecionadas_faceis + selecionadas_medias + selecionadas_dificeis
        print(f"📚 {len(perguntas_ordenadas)} perguntas selecionadas na ordem correta.")
        return perguntas_ordenadas
    except Exception as e:
        print(f"❌ Erro ao selecionar perguntas: {e}")
        return []

# 🔊 Página principal (main.html com música e iframe)
@app.route("/")
def main():
    return render_template("main.html")

# 🏠 Conteúdo da tela inicial (sem música)
@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "GET":
        session.pop("acertos", None)
        session.pop("total", None)

        perguntas = selecionar_perguntas()

        for p in perguntas:
            p.setdefault("pergunta", "Pergunta sem texto")
            p.setdefault("opcoes", ["Sem opções"])
            p.setdefault("resposta_correta", "")

        session["perguntas"] = perguntas
        return render_template("quiz.html", perguntas=perguntas)

    perguntas = session.get("perguntas", [])
    if not perguntas:
        print("⚠️ Nenhuma pergunta encontrada na sessão.")
        return redirect(url_for("index"))

    acertos = 0
    for i, pergunta in enumerate(perguntas):
        resposta_usuario = request.form.get(f"resposta-{i}", "").strip()
        resposta_correta = pergunta.get("resposta_correta", "").strip()

        print(f"📩 Pergunta {i+1}: resposta do usuário = '{resposta_usuario}', correta = '{resposta_correta}'")

        if resposta_usuario == resposta_correta:
            acertos += 1

    session["acertos"] = acertos
    session["total"] = len(perguntas)

    print(f"✅ Acertos: {acertos} de {len(perguntas)}")
    return redirect(url_for("resultado"))

@app.route("/resultado")
def resultado():
    acertos = session.get("acertos", 0)
    total = session.get("total", 0)
    percentual = (acertos / total) * 100 if total else 0

    if percentual == 100:
        feedback = "Parabéns! Você gabaritou! 🏆"
    elif percentual >= 70:
        feedback = "Muito bem! Você mandou bem! 👍"
    elif percentual >= 50:
        feedback = "Você foi bem, mas pode melhorar! 💪"
    else:
        feedback = "Vamos tentar de novo? Você consegue! 🙌"

    print(f"🎯 Resultado: {acertos}/{total} ({percentual:.1f}%) — {feedback}")
    return render_template("resultado.html", acertos=acertos, total=total, feedback=feedback)

@app.route("/registrar", methods=["POST"])
def registrar():
    nome = request.form.get("nome")
    acertos = int(request.form.get("acertos", 0))
    novo_registro = {"nome": nome, "acertos": acertos}

    try:
        with open("hall.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        dados = []

    dados.append(novo_registro)

    with open("hall.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

    return redirect(url_for("hall_da_fama"))

@app.route("/hall-da-fama")
def hall_da_fama():
    try:
        with open("hall.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        dados = []

    dados_ordenados = sorted(dados, key=lambda x: x["acertos"], reverse=True)
    return render_template("halldafama.html", registros=dados_ordenados)

@app.route("/musicplayer")
def musicplayer():
    return render_template("musicplayer.html")

@app.route("/player")
def player():
    return render_template("player.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
