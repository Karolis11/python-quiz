from flask import Flask, render_template, request, session, redirect, url_for
import gspread
from google.oauth2.service_account import Credentials
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

SERVICE_ACCOUNT_FILE = 'quiz-436010-6b96c91ffaa6.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)
SPREADSHEET_ID = '1MQmCQIdUVQgbMJYyVK8x9tW8_ztKmNytjEV4kgJ7SY4'  
sh = gc.open_by_key(SPREADSHEET_ID)
worksheet = sh.sheet1

@app.route('/')
def index():
    return render_template('index.html', title="Sveiki atvykę")

@app.route('/start', methods=['POST'])
def start():
    session['current_question'] = 0
    session['answers'] = []
    session['user_id'] = str(uuid.uuid4())  # Unique user ID
    return redirect(url_for('questions_route'))

# Define the questions
questions = [
    {
        'question': 'Ar dalyvaujate Mokytojų palaikymo ratuose (MPR)?',
        'options': [
            'Nedalyvauju MPR',
            'Dalyvauju MPR pirmi metai',
            'Dalyvauju MPR antri metai',
            'Dalyvauju MPR treti metai'
        ]
    },
    {
        'question': 'Mokykloje dirbate:',
        'options': [
            'Iki vienerių metų',
            'Nuo vienerių iki 5 metų',
            'Nuo 5 iki 15 metų',
            'Virš 15 metų'
        ]
    },
    {
        'question': 'Šiais metais turite:',
        'options': [
            '0,5 etato arba mažiau',
            '0,5 - 0,8 etato',
            '0,9 - 1,1 etato',
            '1,2 - 1,5 etato',
            'Daugiau kaip 1,5 etato'
        ]
    },
    {
        'question': 'Jūsų amžius:',
        'options': [
            'Iki 29',
            '30-39',
            '40-49',
            '50-59',
            '60 ir daugiau metų'
        ]
    }
]

@app.route('/questions', methods=['GET', 'POST'])
def questions_route():
    if 'current_question' not in session:
        return redirect(url_for('index'))

    current_question = session['current_question']

    if current_question >= len(questions):
        return redirect(url_for('psychological_wellbeing'))

    question_data = questions[current_question]

    if request.method == 'POST':
        selected_option = request.form.get('option')
        question_text = question_data['question']

        # Store the user's answer
        session['answers'].append({
            'question': question_text,
            'selected_option': selected_option
        })

        # Move to the next question
        session['current_question'] += 1
        return redirect(url_for('questions_route'))

    return render_template('questions.html', question=question_data, question_number=current_question + 1, total_questions=len(questions), title=f"Klausimas {current_question + 1}")

@app.route('/psychological_wellbeing', methods=['GET', 'POST'])
def psychological_wellbeing():
    questions = [
        'Esu patenkintas (-a) savo gyvenimu',
        'Mano gyvenimas pakankamai kryptingas',
        'Esu patenkintas (-a) savimi',
        'Jaučiuosi, kad galiu savarankiškai apsispręsti dėl man svarbių dalykų gyvenime',
        'Turiu tikslų savo gyvenime',
        'Man patinka mano darbo ir namų aplinka',
        'Mano gyvenimas yra prasmingas',
        'Man patinka veikla, kuria aš užsiimu',
        'Manau, kad turiu visas galimybes pasiekti savo užsibrėžtų tikslų',
        'Jaučiu, kad turiu galimybe nuolat tobulėti'
    ]
    
    options = [
        'Visiškai nesutinku',
        'Nesutinku',
        'Nei sutinku, nei nesutinku',
        'Sutinku',
        'Visiškai sutinku'
    ]

    if request.method == 'POST':
        answers = []
        for i in range(1, 11):
            answer = request.form.get(f'question_{i}')
            answers.append({
                'question': questions[i - 1],
                'selected_option': answer
            })

        session['psychological_wellbeing_answers'] = answers  # Store in session

        # Redirect to a thank you or results page after submission
        return redirect(url_for('work_feelings'))

    return render_template('psychological_wellbeing.html', questions=questions, options=options)


@app.route('/work_feelings', methods=['GET', 'POST'])
def work_feelings():
    questions = [
        'Jaučiu, kad savo darbe per daug dirbu',
        'Jaučiuosi nusivylęs savo darbu',
        'Jaučiuosi išvargęs (-usi), kai ryta atsikeliu ir turiu eiti į darbą',
        'Man lengva suprasti, mokinių poreikius bei jausmus',
        'Jaučiu, kad kai kuriuos mokinius vertinu, tarsi jie būtų bereikšmiai objektai',
        'Jaučiuosi išsekęs (-usi) darbo pabaigoje',
        'Labai efektyviai susitvarkau su mokinių problemomis',
        'Jaučiuosi „sudegęs (-usi)“ dėl savo darbo',
        'Jaučiu, kad teigiamai veikiu kitus žmones, nes jiems rūpi mano darbas',
        'Aš jaudinuosi, kad mokytojo darbas emociškai mane suvaržo',
        'Aš ėmiau daug šiurkščiau elgtis su žmonėmis, kai pasirinkau mokytojo darbą',
        'Jaučiuosi darbe labai energingas (-a)',
        'Jaučiuosi emociškai išsekęs (-usi) nuo darbo',
        'Nuolatinis darbas mokykloje sukelia man per didelę įtampą',
        'Man nesvarbu, kas nutinka kai kuriems mokiniams',
        'Darbas su žmonėmis visą dieną man tikras stresas ir įtampa',
        'Aš galiu lengvai sukurti lengvą atmosferą su mokiniais',
        'Jaučiuosi kupinas jėgų po darbo dienos su mokiniais',
        'Darbe įgyvendinu daug vertingų, prasmingų dalykų',
        'Jaučiuosi tarsi darbe būčiau pasiekęs (-usi) savo jėgų ir kantrybės ribas',
        'Emocines problemas darbe sprendžiu labai ramiai',
        'Jaučiu, kad mokiniai kaltina mane dėl savo pačių problemų'
    ]

    if 'categories' not in session:
        session['categories'] = {
            'Emocinis': [questions[i] for i in [0, 1, 2, 5, 7, 12, 13, 15, 19]],
            'Depersonalizacija': [questions[i] for i in [4, 9, 10, 14, 21]],
            'Asmeniniu': [questions[i] for i in [3, 6, 8, 11, 16, 17, 18, 20]]
        }
    
    options = [
        'Niekada', 
        'Keletą kartų per metus ar rečiau', 
        'Keletą kartų per mėnesį', 
        'Kartą per savaitę', 
        'Kasdien'
    ]

    option_scores = {
        'Niekada': 0,
        'Keletą kartų per metus ar rečiau': 1,
        'Keletą kartų per mėnesį': 2,
        'Kartą per savaitę': 3,
        'Kasdien': 4
    }

    if 'category_scores' not in session:
        session['category_scores'] = {
            'Emocinis': 0,
            'Depersonalizacija': 0,
            'Asmeniniu': 0
    }

    answers = []
    if request.method == 'POST':
        session['category_scores'] = {
            'Emocinis': 0,
            'Depersonalizacija': 0,
            'Asmeniniu': 0
        }

        for i in range(1, 23):  # There are 22 questions
            answer = request.form.get(f'question_{i}')
            answers.append({
                'question': questions[i - 1],
                'selected_option': answer
            })
            for category, category_questions in session['categories'].items():
                if questions[i - 1] in category_questions:
                    session['category_scores'][category] += option_scores[answer]
                    break

        session['work_feelings_answers'] = answers  # Store in session

        # Redirect to a thank you or results page after submission
        return redirect(url_for('email'))

    return render_template('work_feelings.html', questions=questions, options=options)


@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email = request.form.get('email')
        session['email'] = email
        subscription = request.form.get('subscribe')
        session['subscribe'] = subscription

        return redirect(url_for('thank_you'))

    return render_template('email.html', title="Įveskite savo el. paštą")


@app.route('/thank_you')
def thank_you():
    answers = session.get('answers', [])
    wellbeing_answers = session.get('psychological_wellbeing_answers', [])
    work_feelings_answers = session.get('work_feelings_answers', [])

    category_scores = session.get('category_scores', {
        'Emocinis': 0,
        'Depersonalizacija': 0,
        'Asmeniniu': 0
    })

    categories = session.get('categories', {
        'Emocinis': [],
        'Depersonalizacija': [],
        'Asmeniniu': []
    })

    # category_averages = {}
    # for category, score in category_scores.items():
    #     num_questions = len(categories[category])
    #     category_averages[category] = score / num_questions if num_questions > 0 else 0

    # Save answers to Google Spreadsheet
    save_answers_to_sheet(answers, wellbeing_answers, work_feelings_answers)

    return render_template('thank_you.html', title="Ačiū", scores=category_scores)

def save_answers_to_sheet(answers, wellbeing_answers, work_feelings_answers):
    # Check if the sheet is empty
    if len(worksheet.get_all_values()) == 0:
        # Add headers
        headers = ['Timestamp', 'User ID', 'Question', 'Selected Option']
        worksheet.append_row(headers)

    timestamp = datetime.utcnow().isoformat()
    user_id = session.get('user_id')

    row = [timestamp, user_id]
    # Append answers
    for answer in answers:
        row.extend([answer['selected_option']])

    # Append psychological wellbeing answers
    for wellbeing_answer in wellbeing_answers:
        row.extend([wellbeing_answer['selected_option']])

    # Append work feelings answers
    for work_feeling_answer in work_feelings_answers:
        row.extend([work_feeling_answer['selected_option']])

    # Append the optional email
    email = session.get('email')
    row.append(email if email else '-')

    subscribe = session.get('subscribe')
    row.append(subscribe if subscribe else '-')

    # Append the row to the worksheet
    worksheet.append_row(row)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
