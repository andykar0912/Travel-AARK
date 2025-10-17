#%%writefile app.py

import streamlit
import json
import requests

from streamlit_js_eval import get_geolocation
from google import genai
from openai import OpenAI

import aitTravelDetailsFrame
import aitDestinationFrame
import aitTravelPlanFrame


def getCurrentLocation():
  print ("aitinerary.py -> getCurrentLocation() - Get Precise Client Location")

  loc = get_geolocation()

  if loc:
    print("aitinerary.py -> Location data:", loc)
    print(f"aitinerary.py -> Latitude: {loc['coords']['latitude']}")
    print(f"aitinerary.py -> Longitude: {loc['coords']['longitude']}")

    google_maps_api_key = streamlit.session_state["google_maps_api_key"]

    # use the latitude and longitude to get the detailed location
    google_maps_api_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={loc['coords']['latitude']},{loc['coords']['longitude']}&key={google_maps_api_key}&result_type=political%7Clocality"
    detailed_location_response= requests.get(google_maps_api_url)
    if detailed_location_response.status_code == 200:
      detailed_current_location = json.loads(detailed_location_response.text)
      if detailed_current_location:
        # print("Detailed Current location:", json.dumps(detailed_current_location,indent=2))

        # using the detailed location, find the city (usually "types": ["locality","political"]) and the country (usually "types": ["country","political"])
        for address_component in detailed_current_location['results'][0]['address_components']:
          if "locality" in address_component['types'] and "political" in address_component['types']:
            current_city_name = address_component['long_name']
          elif "country" in address_component['types'] and "political" in address_component['types']:
            current_country_name = address_component['long_name']

        print(f"aitinerary.py -> getCurrentLocation() -> Current city: {current_city_name}, {current_country_name}")
        streamlit.session_state["current_city_name"] = current_city_name
        streamlit.session_state["current_country_name"] = current_country_name
        
      else:
        print("aitinerary.py -> getCurrentLocation() -> No address found for the current location.")
    else:
      print("aitinerary.py -> getCurrentLocation() -> Failed to get detailed location:", detailed_location_response.status_code)
  else:
    print("aitinerary.py -> getCurrentLocation() -> Failed to get current location using get_geolocation().")
    streamlit.info("Click 'Allow' in your browser to share location.")


streamlit.title("AITinerary")
streamlit.set_page_config(page_title="AITinerary", layout="wide")


def chooseGenaiClient():  
  print("aitinerary.py -> chooseGenaiClient()")
  genai_client = streamlit.radio(
    label="GenAI Clients available:",
    options=["Gemini", "GPT-5"],
    captions=["Google", "OpenAI"],
    index=None
  )

  if genai_client is not None:
    print(f"aitinerary.py -> chooseGenaiClient() -> GenAI Client chosen is: {genai_client}")
    streamlit.session_state["genai_client"] = genai_client

    streamlit.rerun()


def enterKeys():
  print("aitinerary.py -> enterKeys()")
  if streamlit.session_state["genai_client"] == "Gemini":
    genai_api_key = streamlit.text_input ("Gemini API Key", type="password")
  elif streamlit.session_state["genai_client"] == "GPT-5":
    genai_api_key = streamlit.text_input ("OpenAI API Key", type="password")

  google_maps_api_key = streamlit.text_input ("Google Maps API Key", type="password")
  if streamlit.button("Submit"):
    streamlit.session_state["genai_api_key"] = genai_api_key
    streamlit.session_state["google_maps_api_key"] = google_maps_api_key

    if streamlit.session_state["genai_client"] == "Gemini":
      streamlit.session_state["genAIClient"] = genai.Client(api_key=genai_api_key)
    elif streamlit.session_state["genai_client"] == "GPT-5":
      streamlit.session_state["genAIClient"] = OpenAI(api_key=genai_api_key)

    streamlit.rerun()


@streamlit.dialog("Initialize GenAI Client")
def initializeGenAIClient():
  print("aitinerary.py -> initializeGenAIClient()")
  if "genai_client" not in streamlit.session_state:
    chooseGenaiClient()
  elif "genai_api_key" not in streamlit.session_state or "google_maps_api_key" not in streamlit.session_state:
    enterKeys()


if "genai_api_key" not in streamlit.session_state or "google_maps_api_key" not in streamlit.session_state:
  initializeGenAIClient()
else:
  getCurrentLocation()
  current_city=streamlit.session_state["current_city_name"]
  current_country=streamlit.session_state["current_country_name"]
  current_location=f"{current_city}, {current_country}"
  streamlit.subheader(f"Current Location: {current_location}")

  streamlit.session_state["travelDetails"], streamlit.session_state["destinationDetails"], streamlit.session_state["detailedTravelPlan"] = streamlit.tabs(["Travel Details", "Destination Details", "Detailed Travel Plan"])
  with streamlit.session_state["travelDetails"]:
    aitTravelDetailsFrame.loadTravelDetailsFrame()
  with streamlit.session_state["destinationDetails"]:
    aitDestinationFrame.loadDestinationDetailsFrame()
  with streamlit.session_state["detailedTravelPlan"]:
    aitTravelPlanFrame.loadDetailedTravelPlanFrame()
