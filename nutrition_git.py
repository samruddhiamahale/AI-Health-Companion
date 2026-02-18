
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure the API key for Google Gemini
os.getenv("API_KEY") 
genai.configure(api_key=os.getenv("API_KEY"))

# Intitalize session state variables
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        'goals': 'Lose 10 pounds in 3 months\n Improve cardiovascular health\n Increase energy levels',
        'conditions': 'None',
        'routines': '30-minute walk 3 times a week\n Yoga on weekends',
        'preferences': 'Vegetarian\n Low carb',
        'restrictions': 'No dairy\n No nuts',
    }

# Function to get response from Google Gemini
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel('gemini-2.5-flash')

    content = [input_prompt]

    if image_data:
        content.append(image_data)
    
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"
# Function to process uploaded image and prepare it for Google Gemini input
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None

# app layout and UI
st.set_page_config(page_title="AI Health Companion", page_icon="🍎", layout="wide")
st.header("AI Health Companion")

#Sidebar for health profile input and management
with st.sidebar:
    st.subheader("Your Health Profile")

    health_goals = st.text_area("Health Goals", 
                            value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Medical Conditions",
                            value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Fitness Routines",
                            value=st.session_state.health_profile['routines'])
    food_preferences = st.text_area("Food Preferences",
                            value=st.session_state.health_profile['preferences'])
    dietary_restrictions = st.text_area("Dietary Restrictions",
                            value=st.session_state.health_profile['restrictions'])
    
    if st.button("Update Profile"):
        st.session_state.health_profile = {
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preferences,
            'restrictions': dietary_restrictions,
        }
        st.success("Health profile updated!")

# Main content area with 3 tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Meal Planning", "Food Analysis", "Health Insights"])

with tab1:
    st.subheader("Personalized Meal Planning")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Your Current Needs")
        user_input = st.text_area("Describe any specific requirements or questions you have about meal planning.",
                                  placeholder="E.g., 'I want to lose weight but maintain muscle mass. What should I eat?'")
        
    with col2:
        st.write("###Your Health Profile Summary")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalized Meal Plan"):
        if not any(st.session_state.health_profile.values()):
            st.warning("Please fill out your health profile in the sidebar to get personalized recommendations.")
        else:
            with st.spinner("Creating your personalized meal plan..."):
                # Construct the input prompt for Google Gemini
                prompt = f"""
                Create a personalized meal plan based on the following health profile:

                Health Goals: {st.session_state.health_profile['goals']}
                Medical Conditions: {st.session_state.health_profile['conditions']}
                Fitness Routines: {st.session_state.health_profile['routines']}
                Food Preferences: {st.session_state.health_profile['preferences']}
                Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                Additional requirements: {user_input if user_input else 'None provided.'}

                Provide:
                1. A 7-day meal plan with breakfast, lunch, dinner, and snacks.
                2. Nutritional breakdown for each meal (approximate calories, protein, carbs, fats, macros).
                3. Contextual explanations for why each meal is recommended based on the health profile.
                4. Shopping list for the week organized by category.
                5. Prepartion tips and time-saving strategies for the meals.

                Format the output clearly with headings and bullet points for easy readability. 
                """

                response = get_gemini_response(prompt)

                st.subheader("Your Personalized Meal Plan")
                st.markdown(response)

                #Add download option for meal plan
                st.download_button(
                    label="Download Meal Plan",
                    data=response,
                    file_name="personalized_meal_plan.txt",
                    mime="text/plain"
                )
with tab2:
    st.subheader("Food Analysis")
    
    uploaded_file = st.file_uploader("Upload an image of your meal for analysis", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Meal Image", use_column_width=True)

        if st.button("Analyze Meal"):
            with st.spinner("Analyzing your meal..."):
                image_data = input_image_setup(uploaded_file)

                prompt = f"""
                You are an expert nutritionist analyzing a meal based on an image.

                Provide detailed nutritional information about:
                1. Estimated calorie content
                2. Macronutrient breakdown (protein, carbs, fats)
                3. Potential health benefits
                4. Any concerns or red flags based on common dietary guidelines
                5. Suggestions portions sizes or modifications to make the meal healthier if needed

                If the food contains multiple components, try to identify them separately and provide insights for each.
                """

                response = get_gemini_response(prompt, image_data=image_data)
                st.subheader("Meal Analysis Results")
                st.markdown(response)

with tab3:
    st.subheader("Health Insights")
    
    health_query= st.text_input("Ask a health-related question or seek advice based on your profile",
                                placeholder="E.g., 'How can I improve my energy levels with diet?'")
    if st.button("Get Health Insights"):
        if not health_query:
            st.warning("Please enter a health-related question to get insights.")
        else:
            with st.spinner("Researching your questions..."):
                prompt = f"""
                You are a certiied nutritionist providing personalized health expert. 
                Provide detailed, science-backed insights about:
                {health_query}

                Consider the user's health profile:
                {st.session_state.health_profile}

                Include:
                1. Clear explanations of the science.
                2. Practical, actionable recommendations.
                3. Any relevant research or precautions based on the user's profile.
                4. Suggestions foods/ supplements if appropriate.
                5. References to studies or authoritative sources where applicable.

                Use simple language but maintain accuracy and depth in your explanations. 
                """
                
                response = get_gemini_response(prompt)
                st.subheader("Expert Health Insights")
                st.markdown(response)