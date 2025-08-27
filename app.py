#%%writefile app.py

import streamlit
from google import genai
import json
import pydantic
import requests
import urllib.parse


#from langchain_openai.chat_models import ChatOpenAI

with streamlit.sidebar:
  globals()["gemini_api_key"] = streamlit.text_input ("Gemini API Key", type="password")
  globals()["google_maps_api_key"] = streamlit.text_input ("Google Maps API Key", type="password")

  globals()["genAIClient"] = genai.Client(api_key=gemini_api_key)

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
  global destination, start_date, end_date, destinationColumn1

  travel_interests_str=" and ".join(streamlit.session_state["travel_interests"])

  if destination:
    top10cities_query=f"List the top 10 cities for tourism in {destination}"
    top10cities_query=f"{top10cities_query} for {travel_interests_str}"
    # top10cities_query=f"{top10cities_query} during the period between {start_date} and {end_date}"
    print(f"GenAI Query: {top10cities_query}")

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

    streamlit.session_state["top10cities"]=top10cities

    # with destinationColumn1:
    #   selected_cities=streamlit.multiselect("Select Cities: ", top10cities)

def loadDestinationColumn1():
  # global top10cities

  globals()["destination"]=streamlit.text_input("Destination (city / country / region): ")

  if streamlit.button("Load Cities to Visit"):
    streamlit.session_state["destination"]=destination
    loadTop10Cities()

  # streamlit.button("Load Cities to Visit", on_click=loadTop10Cities)

  if "top10cities" in streamlit.session_state:
    top10cities_list=[]
    for city_entry in streamlit.session_state["top10cities"]:
      top10cities_list.append(f"{city_entry['rank']}. {city_entry['city']}, {city_entry['country']}")
    streamlit.session_state["selected_cities"]=streamlit.multiselect("Select Cities: ", top10cities_list)


def getCurrentLocation():
  global google_maps_api_key

  # get location in latitude and longitude format
  google_maps_api_url= f"https://www.googleapis.com/geolocation/v1/geolocate?key={google_maps_api_key}"
  location_response = requests.post(google_maps_api_url)

  if location_response.status_code == 200:
    # print("Location response:", location_response.text)
    current_location = json.loads(location_response.text)

    # use the latitude and longitude to get the detailed location
    google_maps_api_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={current_location['location']['lat']},{current_location['location']['lng']}&key={google_maps_api_key}&result_type=political%7Clocality"
    detailed_location_response= requests.get(google_maps_api_url)
    if detailed_location_response.status_code == 200:
      detailed_current_location = json.loads(detailed_location_response.text)
      if detailed_current_location:
        # print("Detailed Current location:", json.dumps(detailed_current_location,indent=2))

        # using the detailed location, find the city (usually "types": ["locality","political"]) and the country (usually "types": ["country","political"])
        for address_component in detailed_current_location['results'][0]['address_components']:
          if "locality" in address_component['types'] and "political" in address_component['types']:
            globals()["current_city_name"] = address_component['long_name']
          elif "country" in address_component['types'] and "political" in address_component['types']:
            globals()["current_country_name"] = address_component['long_name']

            print(f"Current city: {current_city_name}, {current_country_name}")
          else:
            print("No address found for the current location.")
      else:
        print("Failed to get detailed location:", detailed_location_response.status_code)
    else:
        print("Failed to get current location:", location_response.status_code)

def loadCurrentLocationMap():
  global current_city_name, current_country_name, google_maps_api_key

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  current_location=urllib.parse.quote_plus(f"{current_city_name},{current_country_name}")  # URL encode the current location

  map_marker = f"markers={current_location}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print("Google Maps API URL for current location:", google_maps_api_url)

  mapImageFile=open('current_location_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("Map for Current location generated successfully!")
  else:
    print("Failed to generate map for current location:", map_response.status_code)


def loadDestinationMap():
  global google_maps_api_key, destination

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  urle_destination=urllib.parse.quote_plus(streamlit.session_state["destination"])  # URL encode the destination

  # map_marker = f"markers=color:blue%7Clabel:{map_destination}%7C{map_destination}"
  map_marker = f"markers={urle_destination}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print("Google Maps API URL for destination:", google_maps_api_url)

  mapImageFile=open('destination_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("Map for Destination generated successfully!")
  else:
    print("Failed to generate map for Destination:", map_response.status_code)

def loadMapSelectedCities():
  global top10cities, google_maps_api_key, destination

  # cities_list = [citiesListBox.get(i) for i in citiesListBox.curselection()]
  globals()["selected_cities_list"]=[]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  map_markers=[]

  for city_entry in streamlit.session_state["selected_cities"]:
    city_entry_num = city_entry.split('.')[0]
    city_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['city']
    country_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['country']

    selected_cities_list.append({'rank': city_entry_num, 'city': city_name, 'country': country_name})

    map_markers.append(f"markers=color:blue%7Clabel:{city_entry_num}%7C{urllib.parse.quote_plus(city_name)}%2C{urllib.parse.quote_plus(country_name)}")

  map_markers_str= '&'.join(map_markers)
  print("Map markers:", map_markers_str)
     
  google_maps_api_url= f"{google_maps_api_url}{map_markers_str}&size=1000x500&key={google_maps_api_key}"
  # print("Google Maps API URL:", google_maps_api_url)
  mapImageFile=open('selected_cities_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("Map generated successfully!")
  else:
    print("Failed to generate map:", map_response.status_code)


def loadAddCityList():
  # global destination, start_date, end_date, destinationColumn1

  if streamlit.session_state["search_city"]:
    search_city=streamlit.session_state["search_city"]
    destination=streamlit.session_state["destination"]
    search_city_query=f"Find cities with the name {search_city} near {destination}"
    print(f"GenAI Search Query: {search_city_query}")

    search_city_response = genAIClient.models.generate_content(
      model="gemini-2.5-flash",
      contents=search_city_query,
      config={
    	  "response_mime_type": "application/json",
        "response_schema": list[City]
      }
    )
    
    globals()["search_cities"] = json.loads(search_city_response.text)
    print("Search cities response:", search_cities)

    streamlit.session_state["search_cities"]=search_cities

def addCityToList():
  for city_entry in streamlit.session_state["selected_search_cities"]:
    city_entry_num = city_entry.split('.')[0]
    search_city_entry=streamlit.session_state["search_cities"][int(city_entry_num)-1]
    
    # check if the city is already added to the top10cities list or not
    for t10city_entry in streamlit.session_state["top10cities"]:
      if t10city_entry['city'] == search_city_entry['city']:
        print(f"{t10city_entry} is already added to top10cities list...")
        return

    new_city_rank=len(streamlit.session_state["top10cities"])+1
    streamlit.session_state["top10cities"].append({'rank': new_city_rank, 'city': search_city_entry['city'], 'country': search_city_entry['country'], 'interests': search_city_entry['interests']})

def loadDestinationColumn2():
  streamlit.session_state["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])

  streamlit.session_state["search_city"]=streamlit.text_input("Add city to List: ")

  if streamlit.button("Search city"):
    loadAddCityList()

  if "search_cities" in streamlit.session_state:
    search_cities_list=[]
    for city_entry in streamlit.session_state["search_cities"]:
      search_cities_list.append(f"{city_entry['rank']}. {city_entry['city']}, {city_entry['country']}")
    streamlit.session_state["selected_search_cities"]=streamlit.multiselect("Select Cities: ", search_cities_list)

    if streamlit.button("Add Selected City to List"):
      addCityToList()

def loadDestinationDetailsFrame():
  streamlit.header("Destination Details")

  globals()["destinationColumn1"], globals()["destinationColumn2"] = streamlit.columns(2)

  with destinationColumn1:
    loadDestinationColumn1()

  with destinationColumn2:
    loadDestinationColumn2()

  if "selected_cities" in streamlit.session_state and streamlit.session_state["selected_cities"] != []:
    loadMapSelectedCities()
    streamlit.image("selected_cities_map.png")
  elif "top10cities" in streamlit.session_state:
    loadDestinationMap()
    streamlit.image("destination_map.png")
  elif "destination" in streamlit.session_state:
    loadDestinationMap()
    streamlit.image("destination_map.png")
  else:
    getCurrentLocation()
    loadCurrentLocationMap()
    streamlit.image("current_location_map.png")

  # with destinationFrame:
  #  globals()["destination"]=streamlit.text_input("Destination (city / country / region): ")
  #
  # with interestsFrame:
  #  globals()["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])

streamlit.title("AITinerary")
loadTravelDetailsFrame()
loadDestinationDetailsFrame()