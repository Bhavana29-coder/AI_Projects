

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv
import json
import re
import logging

#Configure logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_llm():
    try:
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise

def generate_tutoring_response(subject,level,question,learning_style,background,language):
    """
    Docstring for generate_tutoring_response
    
    :param subject: Description
    :param level: Description
    :param question: Description
    :param learning_style: Description
    :param background: Description
    :param language: Description
    genertates a tutoring response based on the provided parameters.
    """
    try:
        #get llmm instances
        llm = get_llm()
        #create prompt
        prompt = _create_tutoring_prompt(subject,level,question,learning_style,background,language)

        #generate response with error handling
        logger.info(f"Generating tutoring response for subject: {subject}, level: {level}")
        response = llm([HumanMessage(content=prompt)])

        #Post-process the response based on learning style
        formatted_response = _format_tutoring_response(response.content, learning_style)
        return formatted_response
    
    except Exception as e:
        logger.error(f"Error generating tutoring response: {str(e)}")
        raise Exception(f"Failed to generate tutoring response: {str(e)}")
    
def _create_tutoring_prompt (subject,level,question,learning_style,background,language):
    prompt = f"""
    You are an expert tutor specialized in {subject} for {level} students. 
    Your task is to provide a detailed and easy-to-understand explanation for the following question:

    Question: {question}

    Consider the student's learning style: {learning_style}, and their background knowledge: {background}. 
    Provide the response in {language}.

    Ensure your explanation is clear, concise, and includes examples where appropriate.
    """
    return prompt

def _format_tutoring_response(content,learning_style):
    """
    Formats the tutoring response based on the learning style.
    
    :param content: The raw content from the LLM.
    :param learning_style: The learning style of the student.
    :return: Formatted response.
    """
    try:
        if learning_style=="Visual":
            return content+"\n\n*Note:Visualize the concepts with diagrams and charts for better understanding.*"
        elif learning_style=="Hands-on":
            return content+"\n\n*Note:Try to implement the concepts through practical exercises and experiments.*"
        else:
            return content
        


    except Exception as e:
        logger.error(f"Error formatting tutoring response: {str(e)}")
        raise Exception(f"Failed to format tutoring response: {str(e)}")
def _create_quiz_prompt(subject,level,num_questions):
    """quiz generator"""
    prompt = f"""
    You are an expert quiz generator specialized in {subject} for {level} students. 
    Your task is to create a quiz with {num_questions} questions covering key concepts in {subject}. 
    Ensure the questions vary in difficulty and format (multiple choice, true/false, short answer).

    Provide the quiz in the following JSON format:
    {{
        "quiz": [
            {{
                "question": "Question text",
                "type": "multiple_choice/true_false/short_answer",
                "options": ["option1", "option2", ...], # Only for multiple choice
                "answer": "correct answer"
            }},
            ...
        ]
    }}
    instructions: Ensure clarity and relevance to the {level} curriculum.

    """
    return prompt

def _create_fallback_quiz(subject,num_questions):
 """helper function to cretae a fallback quiz if parsing fails"""
 logger.warning(f"Creating fallback quiz for subject: {subject} with {num_questions} questions.")
 return [
     {
         "question":f"sample{subject}question#{i+1}",
         "options":["Option A","Option B","Option C","Option D"],
         "answer":"Option A",
         "type":"multiple_choice",
         "explanation":"This is a fallback explanation."

     }
     for i in range(num_questions)
 ]



def _validate_quiz_data(quiz_data):
    """helper function to validate quiz data structure"""
    if not isinstance(quiz_data, list):
        raise ValueError("Quiz data should be a list of questions.")
    for question in quiz_data:
        if not isinstance (question, dict):
            raise ValueError("Each question should be a dictionary.")
        if not all (key in question for key in ["question","type","answer"]):
            raise ValueError("Each question must contain 'question', 'type', and 'answer' keys.")
    return True 

def _parse_quiz_response(response_content,subject,num_questions):
    """helper function to parse quiz response from LLM"""
    try:
        json_match = re.search(r'json\s*(\[[\s\S]*?\])\s*',  response_content)
        if json_match:
            #extract json from code block
            quiz_json = json_match.group(1)
        else:
            #try to find raw json array
            json_match=re.search(r'\[\s*\{.*\}\s*\]',response_content,re.DOTALL)
            if json_match:
                quiz_json=json_match.group(0)
            else:
                quiz_json=response_content
    
        #parse the json
        quiz_data = json.loads(quiz_json)
        _validate_quiz_data(quiz_data)
    

    # ensure we have the requested number of num_questions
        if len(quiz_data)>num_questions:
         quiz_data=quiz_data[:num_questions]

    #add explanations field if missing
        for question in quiz_data:
          if "explanation" not in question:
            question["explanation"]=f"The correct answer is {question['answer']}."
        return quiz_data
     
    except (json.JSONDecodeError,ValueError) as e:
      logger.error(f"Error parsing quiz response: {str(e)}")
    return _create_fallback_quiz(subject,num_questions)

def generate_quiz(subject,level,num_questions=5, reveal_answer=True):
    """
    Generates a quiz based on the provided parameters.
    
    :param subject: The subject of the quiz.
    :param level: The educational level of the quiz.
    :param num_questions: Number of questions in the quiz.
    :param reveal_answer: Whether to include answers in the output.
    :return: A list of quiz questions with answers if specified.
    """
    try:
        llm = get_llm()
        prompt = _create_quiz_prompt(subject,level,num_questions)
        
        #generate response
        logger.info(f"Generating quiz for subject: {subject}, level: {level}, questions: {num_questions}")

        response = llm([HumanMessage(content=prompt)])
        
        #parse the response
        quiz_data = _parse_quiz_response(response.content,subject,num_questions)
        
        # format the quiz with hidden answer if required 
        # if reveal_answer:
        #     formatted_quiz = _format_quiz_with_reveal(quiz_data)
        
        #     return {
        #       "quiz_data":quiz_data,
        #     "formatted_quiz": formatted_quiz
        # }
        # else:
        #     return{
        #      "quiz_data":quiz_data
        #      }
        return {
            "quiz": quiz_data
        }

    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise Exception(f"Failed to generate quiz: {str(e)}")

def _format_quiz_with_reveal(quiz_data):
    """
   format quiz data into html with hidden answer that can be revealed on click.

   Args:
    quiz_data (list): List of quiz questions with answers.
Returns: str: Formatted HTML string.
"""
    html="""
<!DOCTYPE html>
<html>
<head>
    <style>
        .answer {display:none; color:blue; margin-top:5px;}
        .question {margin-bottom:15px;}
        .reveal-btn {margin-left:10px; cursor:pointer; color:green;}
    </style>
    <script>
        function revealAnswer(id) {
            var answer = document.getElementById(id);
            if (answer.style.display === "none") {
                answer.style.display = "block";
            } else {
                answer.style.display = "none";
            }
        }
        .quiz-container {font-family: Arial, sans-serif; margin: 20px;}
        .question{font-weight: bold;}
        .corrected-answer {color: green; font-style: italic;}
        .option:hover {background-color: #f0f0f0;}
        .reveal-btn:hover {background-color:#2196f3; text-decoration: underline;}
        .answer {font-size: 14px;}
        .explanation {font-size: 13px; color: gray; margin-top: 3px;}
        .selevted-correct{background-color: #d4edda;}
    </script>
</head>
<body>
"""
    option_letters=['A','B','C','D']
    for i, question in enumerate(quiz_data, 1):
#    option_letters=['A','B','C','D']
      corrected_index=question["options"].index(question["correct_answer"]) if "options" in question else 0
      html +=f"""
<div class="question" id="question-{i}">
   <h3>Question {i}: {question['question']}</h3>
   <p>{question["question"]}</p>
   <div class="options">
   """
      for j,option in enumerate(question.get("options",[])): 
        option_class="option"
        if j==corrected_index:
         option_class+=" selected-correct"
        html+=f'<div class="{option_class}">{option_letters[j]}. {option}</div>'
    html +=f"""
   </div>
   <button class="reveal-btn" onclick="revealAnswer('answer-{i}')">Reveal Answer</button>
   <div class="answer" id="answer-{i}">
         <p class="corrected-answer">Correct Answer: {question['correct_answer']}</p>
         <p class="explanation">Explanation: {question.get('explanation','No explanation provided.')}</p>
    </div>
</div>
"""
    html+=("</div></body></html>")

    return html



def export_quiz_to_html(quiz_data,file_path="quiz.html"):
    """
    Exports the quiz data to an HTML file.
    
    :param quiz_data: The quiz data to export.
    :param file_path: The file path to save the HTML file.
    """
    try:
        formatted_html = _format_quiz_with_reveal(quiz_data)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_html)
        logger.info(f"Quiz exported successfully to {file_path}")
    except Exception as e:
        logger.error(f"Error exporting quiz to HTML: {str(e)}")
        raise Exception(f"Failed to export quiz to HTML: {str(e)}")