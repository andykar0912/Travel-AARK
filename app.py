#%%writefile app.py

import streamlit
import google
import json
import pydantic

#from langchain_openai.chat_models import ChatOpenAI

with streamlit.sidebar:
  globals()["gemini_api_key"] = streamlit.text_input ("Gemini API Key", type="password")
  globals()["google_maps_api_key"] = streamlit.text_input ("Google Maps API Key", type="password")

  globals()["genAIClient"] = google.genai.Client(api_key=gemini_api_key)

def loadTravelDatesFrame():
  with datesFrame:
    streamlit.subheader("Dates")

    globals()["startDate"] = streamlit.date_input("Start Date: ")
    globals()["endDate"] = streamlit.date_input("End Date: ")

    globals()["number_of_days"]=endDate-startDate
    streamlit.success(f"Number of Days: {number_of_days}")

def loadPassengersFrame():
  with passengersFrame:
    streamlit.subheader("Passengers")

    globals()["adults"]=streamlit.text_input("No. of adults: ")
    globals()["seniors"]=streamlit.text_input("No. of seniors (>60 years): ")
    globals()["children"]=streamlit.text_input("No. of children: ")

def loadCostsFrame():
  with costsFrame:
    streamlit.subheader("Expenses")

    globals()["travelCosts"] = streamlit.radio("Travel Costs: ", ["Budget", "Standard", "Luxury"])
    streamlit.success(f"Travel Costs: {travelCosts}")

def loadTravelDetailsFrame():
  streamlit.header("Travel Details")

  globals()["datesFrame"], globals()["passengersFrame"], globals()["costsFrame"] = streamlit.columns(3)

  loadTravelDatesFrame()
  loadPassengersFrame()
  loadCostsFrame()

class City(pydantic.BaseModel):
    rank: str
    city: str
    country: str
    interests: list[str]

def loadTop10Cities():
  global destination, travel_interests, start_date, end_date

  if destination:
    top10cities_query=f"List the top 10 cities for tourism in {destination}"
    # top10cities_query=f"{top10cities_query} for interests in {travel_interests}"
    # top10cities_query=f"{top10cities_query} during the period between {start_date} and {end_date}"

    top10cities_response = genAIClient.models.generate_content(
      model="gemini-2.5-flash",
      contents=top10cities_query,
      config={
    	  "response_mime_type": "application/json",
        "response_schema": list[City]
      }
    )
    
    globals()["top10cities"] = json.loads(top10cities_response.text)
    print("Top 10 cities response:", top10cities)

def loadDestinationColumn1():
  global top10cities

  globals()["destination"]=streamlit.text_input("Destination (city / country / region): ")

  # if streamlit.button("Load Cities to Visit"):
  #   streamlit.session_state["destination"]=destination

  streamlit.button("Load Cities to Visit", on_click=loadTop10Cities)

  if "destination" in streamlit.session_state:
    selected_cities=streamlit.multiselect("Select Cities: ", top10cities)

def loadDestinationColumn2():
  streamlit.image("world_map.png")

def loadDestinationDetailsFrame():
  streamlit.header("Destination Details")

  globals()["destinationColumn1"], globals()["destinationColumn2"] = streamlit.columns(2)

  with destinationColumn1:
    loadDestinationColumn1()

  with destinationColumn2:
    loadDestinationColumn2()

  # with destinationFrame:
  #  globals()["destination"]=streamlit.text_input("Destination (city / country / region): ")
  #
  # with interestsFrame:
  #  globals()["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])

streamlit.title("AITinerary")
loadTravelDetailsFrame()
loadDestinationDetailsFrame()