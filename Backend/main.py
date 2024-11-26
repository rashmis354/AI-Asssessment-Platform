import os
import json
from config.config import LOGS_PATH,code_review_prompt,code_review_user_prompt
# from modules.Utils.generate_log_file import logger
import getpass
import datetime
from modules.openai.azure_open_ai import make_request_json
from modules.openai.open_ai_helper_functions import create_openai_obj
# Create Log Folder
current_directory = os.getcwd()
try:
    if not os.path.isdir(current_directory + LOGS_PATH):
        os.makedirs(current_directory + LOGS_PATH)
except Exception as e:
    print("Log Folder Creation Failed-" + str(e))

# logger.info("<-----------------Service restarted----------------->")

# Sample data for assessments and practice tests
assessments = [
    {"name": "Python Coding Assessment", "date": datetime.date.today()},
    {"name": "React Frontend Assessment", "date": datetime.date.today() + datetime.timedelta(days=1)},
    {"name": "Java Backend Assessment", "date": datetime.date.today() + datetime.timedelta(days=2)},
]

practice_tests = {
    "Python": [
        {"question": "What is the output of print(2 ** 3)?", "options": ["6", "8", "9", "4"], "answer": "8"},
        {"question": "What keyword is used to define a function in Python?", "answer": "def"},
    ],
    "React": [
        {"question": "What is the main purpose of React?", "options": ["State Management", "Building UI", "Database", "Server-side rendering"], "answer": "Building UI"},
        {"question": "Which of the following is a lifecycle method in React?", "options": ["componentDidMount", "componentWillUpdate", "render", "All of the above"], "answer": "All of the above"},
    ]
}

def view_scheduled_assessments():
    print("\n******Scheduled Assesments******")
    today = datetime.date.today()
    for assessment in assessments:
        if assessment["date"] >= today:
            print(f"- {assessment['name']} (Date: {assessment['date']})") 
            
    for assessment in assessments:
        if assessment["date"] >= today:
            if assessment["date"] == today:
                print("\n*****Today's Assesments*****")
                print(f"- {assessment['name']} (Date: {assessment['date']})")
                while True:
                    print("1. Take Assesment")
                    print("2. Mock Test")
                    print("3. Back to Dashboard")
                    choice = input("Choose an option (1-3): ")
                    if choice == "1":
                        start_assessment(assessment)
                    elif choice == "2":
                        mock_assessments()
                    elif choice == "3":
                        print("Navigating back to the Dashboard...")
                        break
                    else:
                        print("Invalid choice. Please try again.")
                    


# def scheduled_assessments():
#     while True:
        
#         print("1. ")
#         print("2. Practice Tests")
#         print("3. Access Profile Settings")
#         print("4. System Check")
#         print("5. Exit")
        
#         choice = input("Choose an option (1-6): ")
        
#         if choice == "1":
#             view_scheduled_assessments()
#         # elif choice == "2":
#         #     mock_assessments()
#         elif choice == "2":
#             practice_tests_function()
#         elif choice == "3":
#             access_profile_settings()
#         elif choice == "4":
#             system_check()
#         elif choice == "5":
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please try again.")


def start_assessment(assessment):
    print(f"\nStarting Assessment: {assessment['name']}")
    score = 0
    # Example questions
    coding_question = "Write a function to reverse a string."
    mcq_question = "What is the output of 5 + 3 * 2?"
    mcq_options = ["11", "16", "8", "10"]

    # Initialize review flags
    coding_review = False
    mcq_review = False

    # Coding question
    print(f"\nCoding Question: {coding_question}")
    while True:
        choice = input("Enter 1 to skip, 2 to answer: ").strip()
        if choice == '1':
            coding_review = True
            coding_answer = "Skipped"
            break
        elif choice == '2':
            print("Enter your answer (code). Type 'END' on a new line when you are finished:")
            coding_answer_lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                coding_answer_lines.append(line)
            coding_answer = "\n".join(coding_answer_lines)
            msg_list = []
            system_prompt = code_review_prompt
            user_prompt = code_review_user_prompt.format(Question = coding_question,code_solution = coding_answer)
            sys_open_ai_obj = create_openai_obj("system",system_prompt)
            msg_list.append(sys_open_ai_obj)
            user_open_ai_obj = create_openai_obj("user",user_prompt)
            msg_list.append(user_open_ai_obj)
            coding_result = json.loads(make_request_json(msg_list))
            print(coding_result)
            score = score + coding_result.get("Total Score")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    # MCQ question
    print(f"\nMCQ Question: {mcq_question}")
    for idx, option in enumerate(mcq_options, start=1):
        print(f"{idx}. {option}")

    while True:
        choice = input("Enter 1 to skip, 2 to answer: ").strip()
        if choice == '1':
            mcq_review = True
            mcq_answer = "Skipped"
            break
        elif choice == '2':
            while True:
                mcq_answer = input("Choose the correct option (1-4): ")
                if mcq_answer.isdigit() and 1 <= int(mcq_answer) <= 4:
                    if int(mcq_answer) == 1:
                        score = score + 50
                    break
                else:
                    print("Invalid input. Please enter a number between 1 and 4.")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")
    
    # Submission
    print("\nAssessment submitted!")
    print(f"Coding Answer: {coding_answer} (Marked for review: {'Yes' if coding_review else 'No'})")
    if mcq_answer != "Skipped":
        print(f"MCQ Answer: {mcq_options[int(mcq_answer) - 1]} (Marked for review: {'Yes' if mcq_review else 'No'})")
    else:
        print(f"MCQ Answer: {mcq_answer} (Marked for review: {'Yes' if mcq_review else 'No'})")
    print("\n")
    print("******Total Assessment score*********")
    print(score)
    if score>=40:
        print("Passed!!!")
    else:
        print("Failed!!!")    

def mock_assessments():
    print("Starting Mock Assessment")
    # Example questions
    coding_question = "Write a function to reverse a string."
    mcq_question = "What is the output of 5 + 3 * 2?"
    mcq_options = ["11", "16", "8", "10"]
    
    # Initialize review flags
    coding_review = False
    mcq_review = False

    # Coding question
    print(f"\nCoding Question: {coding_question}")
    while True:
        choice = input("Enter 1 to skip, 2 to answer: ").strip()
        if choice == '1':
            coding_review = True
            coding_answer = "Skipped"
            break
        elif choice == '2':
            coding_answer = input("Your answer (code): ")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    # MCQ question
    print(f"\nMCQ Question: {mcq_question}")
    for idx, option in enumerate(mcq_options, start=1):
        print(f"{idx}. {option}")

    while True:
        choice = input("Enter 1 to skip, 2 to answer: ").strip()
        if choice == '1':
            mcq_review = True
            mcq_answer = "Skipped"
            break
        elif choice == '2':
            while True:
                mcq_answer = input("Choose the correct option (1-4): ")
                if mcq_answer.isdigit() and 1 <= int(mcq_answer) <= 4:
                    break
                else:
                    print("Invalid input. Please enter a number between 1 and 4.")
            break
        else:
            print("Invalid input. Please enter 1 or 2.")

    # Submission
    print("\nMock Assessment submitted!")
    print(f"Coding Answer: {coding_answer} (Marked for review: {'Yes' if coding_review else 'No'})")
    if mcq_answer != "Skipped":
        print(f"MCQ Answer: {mcq_options[int(mcq_answer) - 1]} (Marked for review: {'Yes' if mcq_review else 'No'})")
    else:
        print(f"MCQ Answer: {mcq_answer} (Marked for review: {'Yes' if mcq_review else 'No'})")


def practice_tests_function():
    print("\nAvailable Domains for Practice Tests:")
    for idx, domain in enumerate(practice_tests.keys(), start=1 ):
        print(f"{idx}. {domain}")
    
    domain_choice = int(input("Choose a domain (1-{}): ".format(len(practice_tests)))) - 1
    domain = list(practice_tests.keys())[domain_choice]
    
    print(f"\nStarting Practice Test in {domain}...")
    for question in practice_tests[domain]:
        print(f"Question: {question['question']}")
        if "options" in question:
            for idx, option in enumerate(question["options"], start=1):
                print(f"{idx}. {option}")
        answer = input("Your answer: ")
        print(f"Correct answer: {question['answer']}\n")

def access_profile_settings():
    print("\nAccessing Profile Settings...")
    # Here you could implement more functionalities for profile management
    print("Profile settings accessed.")

def system_check():
    print("\nSystem Check: All systems operational.")

def educator_dashboard():
    while True:
        print("\nEducator Dashboard")
        print("1. Manage Assessments")
        print("2. View Overall Assessment Activity")
        print("3. Create Assessment")
        print("4. Exit")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == "1":
            manage_assessments()
        elif choice == "2":
            view_overall_assessment_activity()
        elif choice == "3":
            create_assessment()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def manage_assessments():
    while True:
        print("\nManage Assessments")
        print("1. Live Proctoring")
        print("2. Assessment Details")
        print("3. Reports and Analytics")
        print("4. Back to Dashboard")
        
        choice = input("Choose an option (1-4): ")
        
        if choice == "1":
            print("Live Proctoring feature is under development.")
        elif choice == "2":
            print("*****Assessment Details*****")
            for assessment in assessments:
                print(f"- {assessment['name']} (Date: {assessment['date']})")
            
        elif choice == "3":
            print("Displaying Reports and Analytics...")
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

def view_overall_assessment_activity():
    print("Displaying Reports and Analytics...")

def create_assessment():
    while True:
        print("\nCreate Assessment")
        print("1. Question Upload")
        print("2. Proctoring Setup")
        print("3. Back to Dashboard")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "1":
            question_upload()
        elif choice == "2":
            print("Proctoring Setup feature is under development.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def question_upload():
    while True:
        print("\nQuestion Upload")
        print("1. Manual Upload")
        print("2. Document Upload")
        print("3. Back to Create Assessment")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "1":
            manual_upload()
        elif choice == "2":
            file_path = input("Enter the file path for document upload: ")
            print(f"Document uploaded from {file_path}.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def manual_upload():
    questions = []
    title = input("Enter the title of the Assessment: ")
    date = input("Enter the date (YYYY-MM-DD): ")

    while len(questions) < 3:
        print(f"\nEntering question {len(questions) + 1} (out of 3):")
        question_type = input("Enter the type of question (MCQ/Coding/Descriptive): ")
        question = input("Enter the question: ")
        
        options = None
        if question_type.lower() == "mcq":
            options = input("Enter the options separated by commas: ").split(',')
            options = [option.strip() for option in options]
        elif question_type.lower() == "coding":
            options = None  # No options for coding questions
        elif question_type.lower() == "descriptive":
            options = None  # No options for descriptive questions
        else:
            print("Invalid question type. Please enter MCQ, Coding, or Descriptive.")
            continue  # Skip to the next iteration if the type is invalid
        
        assessment = {
            "type": question_type,
            "question": question,
            "options": options
        }
        
        questions.append(assessment)
    assessments.extend(questions)
    print("Assessment created successfully")
    print("Assessment Title: ", title)
    print("Assessment Date: ", date)
    print("Questions:")
    for q in questions:
        print(f"- {q['question']} (Type: {q['type']})")

def candidate_dashboard():
    while True:
        print("\nCandidate Dashboard")
        print("1. View Scheduled Assessments")
        # print("2. Mock Assessment")
        print("2. Practice Tests")
        print("3. Access Profile Settings")
        print("4. System Check")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ")
        
        if choice == "1":
            view_scheduled_assessments()
        elif choice == "2":
            practice_tests_function()
        elif choice == "3":
            access_profile_settings()
        elif choice == "4":
            system_check()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

# Role-Based Login
def login():
    print("Welcome to AI Assessment Platform")
    # Get user input for role and password
    user_id = input("Enter user id: ").strip()
    if user_id == "1000055555":
        role  = "Candidate"
    elif user_id == "1000066666":
        role  = "Educator"
    elif user_id == "1000077777":
        role = "Admin"
    elif user_id == "1000088888":
        role = "Employee"
    else:
        print("Invalid User")
        return
    
    password = getpass.getpass("Enter your password: ")
    # Check if the password is correct
    if password == "user@123":
        # Check if the role is valid
        if role in ["Admin", "Candidate", "Educator", "Employee"]:
            print(f"Login successful!")
            print(f"Welcome, {role}.")
            if role == "Educator":
                educator_dashboard()
            else:
                candidate_dashboard()
        else:
            print("Invalid role. Please enter a valid role: Admin, Candidate, Educator, Employee.")
    else:
        print("Incorrect password. Please try again.")

login()