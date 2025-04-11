import logging
from flask import Flask, render_template, request
from openai import OpenAI
from langdetect import detect


TOGETHER_API_KEY = "386dd95a2885fc3bb2d67dd7119713bb809a722844bac40e5dbbd0658f020752"

client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=TOGETHER_API_KEY
)


base_system_prompt = """
Ты — образовательный помощник "School helper" для студентов и школьников, который помогает разобраться в сложных темах, понять учебный материал и подготовиться к экзаменам.

Правила:
- Отвечай кратко и понятно, избегай сложных терминов.
- Если вопрос связан с определённой темой, приводи примеры и ссылки на авторитетные источники (например, образовательные порталы, Википедию).
- В конце ответа обязательно указывай ссылку на источник в формате: "ссылка на источник: *сайт*".
- Если информация отсутствует — уведомляй об этом.
- Отвечай на том же языке, на котором задан вопрос.
С уважением,  
Образовательный помощник
"""


app = Flask(__name__, template_folder=".")
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/taskbank')
def taskbank():
    tasks = [
        "1 квадрат",
        "2 квадрат",
        "3 квадрат"
    ]
    return render_template("taskbank.html", tasks=tasks)

@app.route('/consult', methods=['GET', 'POST'])
def consult():
    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question")
        logging.info(f"Получен вопрос: {question}")

        try:
            lang = detect(question)
            full_system_prompt = base_system_prompt + f"\n\n[Ответь на языке: {lang.upper()}]"
            
            completion = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": question}
                ]
            )
            answer = completion.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Ошибка при обращении к ИИ: {e}")
            answer = "Произошла ошибка при обращении к ИИ. Попробуйте позже."

    return render_template("consult.html", question=question, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
