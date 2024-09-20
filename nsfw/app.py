from fastapi import HTTPException
import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
visual_api_key = os.getenv('VISUAL_API')
audio_api_key = os.getenv('SPEECH_API')

# List of positive and negative classes
positive_classes = [
    "natural", "yes_overlay_text", "text", "knife_not_in_hand", "gun_not_in_hand",
    "hybrid", "yes_religious_icon", "animated", "general_suggestive", "yes_qr_code",
    "yes_child_present", "culinary_knife_not_in_hand", "yes_confederate", "yes_drawing"
]
negative_classes = [
    "gun_in_hand", "a_little_bloody", "very_bloody", "licking", "knife_in_hand",
    "yes_self_harm", "yes_nazi", "yes_smoking", "kissing", "animated_gun",
    "human_corpse", "yes_genitals", "yes_breast", "other_blood", "yes_middle_finger",
    "animal_genitalia_only", "yes_terrorist", "hanging", "yes_sex_toy", "yes_cleavage",
    "yes_female_underwear", "yes_bra", "yes_sexual_activity", "yes_fight", "noose",
    "yes_sportswear_bottoms", "medical_injectables", "yes_butt", "yes_kkk",
    "yes_alcohol", "yes_drinking_alcohol", "general_nsfw", "yes_male_shirtless",
    "yes_marijuana", "yes_male_nudity", "yes_pills", "yes_panties", "illicit_injectables",
    "yes_male_underwear", "animal_genitalia_and_human", "yes_bodysuit", "yes_negligee",
    "yes_gambling", "yes_emaciated_body", "yes_miniskirt", "culinary_knife_in_hand",
    "yes_female_swimwear", "yes_female_nudity", "yes_bulge", "yes_realistic_nsfw",
    "yes_sports_bra", "yes_animal_abuse", "animated_animal_genitalia", "animated_corpse",
    "animated_alcohol", "yes_sexual_intent", "yes_undressed"
]
threshold = 0.5

# Function to check video using Visual API
def check_video(url):
    visual_url = 'https://api.thehive.ai/api/v2/task/sync'
    headers = {
        "authorization": f"token {visual_api_key}",
        "accept": "application/json"
    }
    payload = {"url": url}
    response = requests.post(visual_url, headers=headers, json=payload)

    if response.status_code != 200:
        return None, f"Error: {response.status_code} - {response.text}"

    response_json = response.json()
    found_negative_case = False
    negative_cases = []

    # Check for negative cases
    for status in response_json.get('status', []):
        status_response = status.get('response', {})
        for output in status_response.get('output', []):
            time = output.get('time')
            for cls in output.get('classes', []):
                score = cls.get('score')
                label = cls.get('class')
                if label in negative_classes and score > threshold:
                    found_negative_case = True
                    negative_cases.append({
                        "time": time,
                        "class": label,
                        "score": score
                    })
    return found_negative_case, negative_cases

# Function to check audio using Speech API
def check_audio(url):
    audio_url = "https://api.thehive.ai/api/v2/task/sync"
    headers = {
        "accept": "application/json",
        "authorization": f"token {audio_api_key}"
    }
    payload = {"url": url}
    response = requests.post(audio_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        return None, f"Error: {response.status_code} - {response.text}"
    response_data = response.json()
    try:
        language = response_data['status'][0]['response']['language']
        if language == "UNSUPPORTED":
            return {
                "message": "Unsupported language, will not process further."
            }
    except (KeyError, IndexError) as e:
        raise HTTPException(status_code=500, detail="Invalid response format from Hive API.")
    response_data = response.json()
    try:
        classifications = response_data['status'][0]['response']['output'][0]['classifications']
        if not classifications:
            return "No classifications found"
    except (KeyError, IndexError):
        return "Invalid response format from Hive API"

    nsfw_text = ""
    for item in classifications:
        sentence = item['text']
        for classification in item['classes']:
            ns_class = classification['class']
            ns_score = classification['score']
            if ns_score != 0:
                nsfw_text += f"Sentence: {sentence} -> Reason: {ns_class} with score {ns_score}\n"
    return nsfw_text

# Streamlit UI
st.title("Video & Audio Safety Checker")


video_url = st.text_input("Enter the video URL:")

if st.button("Check"):
    if video_url:
        # Check Video for unsafe content
        st.write("Checking video for unsafe content...")
        found_negative_case, negative_cases = check_video(video_url)
        
        if found_negative_case:
            st.error("Video contains unsafe content!")
            st.write("Detected negative cases:")
            for case in negative_cases:
                st.write(f"Time: {case['time']}, Class: {case['class']}, Score: {case['score']}")
        else:
            st.success("Video appears safe!")
        
        # Regardless of the video check, proceed with checking audio
        st.write("Now checking audio for unsafe content...")
        nsfw_text = check_audio(video_url)
        
        if nsfw_text:
            st.error("NSFW content found in audio!")
            st.write(nsfw_text)
        else:
            st.success("Audio is safe!")
    else:
        st.error("Please enter a video URL.")