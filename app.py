import requests
import streamlit as st
import uuid 
import random
from streamlit.components.v1 import html


#page configuration
st.set_page_config(
    page_title="AI Tutor",layout="wide")

#app title
st.title("AI-Powered Tutor & Quiz App")

with st.sidebar:
    st.header("Learning preferences")
    subject=st.selectbox("Select Subject",["Mathematics","Science","History","Computer Science","Physics","Chemistry","Biology","Programming"])
    level=st.selectbox("Select Level",["Beginner","Intermediate","Advanced"])
    learning_style=st.selectbox("Select Learning Style",["Visual","Auditory","Kinesthetic","Text-based","Hands-on"])
    language=st.selectbox("Select Language",["English","Spanish","French","German","Chinese","Japanese"])
    background_knowledge=st.selectbox("Select Background Knowledge",["None","Basic","Intermediate","Advanced"])


    API_ENDPOINT="http://127.0.0.1:8000"


tab1,tab2=st.tabs(["Ask a Question","Take a Quiz"])
 
with tab1:
    st.header("Ask a Question")
    question=st.text_area("what would you like to learn today?",
         placeholder=  "Example: Can you explain the concept of variables in algebra?")
    
    if st.button("Get Explanation"):
        with st.spinner("Generating personlized explanation..."):
            try:
                response=requests.post(f"{API_ENDPOINT}/tutor",
                    json={
                         "subject":subject,
                        "topic":subject,
                        "level":level,
                        "question":question,
                        "learning_style":learning_style,
                        "background":background_knowledge,
                         "language":language
                  }).json()
                st.success("Here is your explanation:")
                st.markdown(response["response"],
                                unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error getting explanation: {str(e)}")
                st.info(f"Make sure the backend is running at {API_ENDPOINT}.")

st.markdown("---")
st.markdown("Powered by AI-Your Personal Learning Assistant")



with tab2:
    st.header("Test Your Knowledge with a Quiz")
    
    col1,col2=st.columns([2,1])

    with col1:
          num_questions=st.slider("Number of Questions",min_value=1,max_value=10,value=5)

    with col2:
          quiz_button=st.button("Generate Quiz",use_container_width=True)

          if quiz_button:
                with st.spinner("Generating quiz..."):
                    try:
                        response=requests.post(f"{API_ENDPOINT}/quiz",
                             json={
                                    "subject":subject,
                                     "topic":subject,
                                    "level":level,
                                    "language":language,
                                    "num_questions":num_questions
                             }).json()
                     
                        st.success("Here is your quiz:")
                         

                        # if "formatted_quiz" in response and response["formatted_quiz"]:
                        #   html(response["formatted_quiz"], height=300)
                         
                        for i,q in enumerate(response["quiz"]):
                                with st.expander(f"Question {i+1}:{q['question']}",expanded=True):
                                        # session_id=str(uuid.uuid4())
                                        selected=st.radio("Select your answer",
                                                          options=q["options"],
                                        # key=f"q_{session_id}"
                                        key=f"q_{i}"


                                        )

                                        if st.button("Check Answer",key=f"check_{i}"):
                                                if selected==q["answer"]:
                                                    st.success(f"Correct!{q.get('explanation','')}")
                                                else:
                                                    st.error(f"Incorrect. The correct answer is: {q['answer']}")
                    except Exception as e:
                            st.error(f"Error generating quiz: {str(e)}")
                            st.info(f"Make sure the backend is running at {API_ENDPOINT}.")

st.markdown("---")
st.markdown("Powered by AI")

       