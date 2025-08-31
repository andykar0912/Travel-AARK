#%%writefile app.py

import streamlit
from google import genai
import json
import pydantic
import requests
import urllib.parse
from streamlit_js_eval import get_geolocation
import datetime

class Holiday(pydantic.BaseModel):
    holiday_start_date: str
    holiday_end_date: str
    reason: str

def loadHolidays():
  print("loadHolidays()")

  current_city = streamlit.session_state["current_city_name"]
  current_country = streamlit.session_state["current_country_name"]
  current_location = f"{current_city} ({current_country})"
  
  genAIClient = streamlit.session_state["genAIClient"]
  month_slider = streamlit.session_state["month_slider"]

  current_date=datetime.date.today()
  
  last_date=current_date+datetime.timedelta(days=30*month_slider)
  print(f"Current date: {current_date}")
  print(f"Date after {month_slider} months: {last_date}")
  
  location_holiday_query=f"Between {current_date} and {last_date}"
  location_holiday_query=f"{location_holiday_query} list the first weekend of the period"
  location_holiday_query=f"{location_holiday_query} and long weekends and vacations in {current_location}"
  print(f"loadHolidays() -> GenAI Query: {location_holiday_query}")

  location_holiday_response = genAIClient.models.generate_content(
    model="gemini-2.5-flash",
    contents=location_holiday_query,
    config={
  	  "response_mime_type": "application/json",
      "response_schema": list[Holiday]
    }
  )
    
  holidays_list = json.loads(location_holiday_response.text)
  print(f"loadHolidays() -> List next Holidays (in {month_slider} months) response: {holidays_list}")

  streamlit.session_state["holidays_list"]=holidays_list

def loadHolidaySlider():
  current_city = streamlit.session_state["current_city_name"]
  current_country = streamlit.session_state["current_country_name"]
  current_location = f"{current_city} ({current_country})"
  
  genAIClient = streamlit.session_state["genAIClient"]

  streamlit.subheader(f"Check upcoming Holidays in {current_location}")  

  month_slider=streamlit.slider("Choose number of months",
    min_value=2,
    max_value=12,
    value=6,
    on_change=loadHolidays)
  
  streamlit.session_state["month_slider"] = month_slider
  
  if "holidays_list" not in streamlit.session_state:
    loadHolidays()

  streamlit.write(f"Following are vacations in the next {month_slider} months:")
  for holiday_entry in streamlit.session_state["holidays_list"]:
    streamlit.success(f"{holiday_entry['reason']}: from {holiday_entry['holiday_start_date']} to {holiday_entry['holiday_end_date']}")

def loadTravelDatesFrame():
  with streamlit.session_state["datesFrame"]:
    

    print("loadTravelDatesFrame()")
  
    streamlit.subheader("Dates")

    streamlit.session_state["startDate"] = streamlit.date_input("Start Date: ")
    streamlit.session_state["endDate"] = streamlit.date_input("End Date: ")
   
    number_of_days=streamlit.session_state["endDate"]-streamlit.session_state["startDate"]
    streamlit.success(f"Number of Days: {number_of_days}")
    streamlit.session_state["number_of_days"] = number_of_days

def loadPassengersFrame():
  with streamlit.session_state["passengersFrame"]:
    print("loadPassengersFrame()")

    streamlit.subheader("Passengers")

    streamlit.session_state["adults"]=streamlit.text_input("No. of adults: ")
    streamlit.session_state["seniors"]=streamlit.text_input("No. of seniors (>60 years): ")
    streamlit.session_state["children"]=streamlit.text_input("No. of children: ")

def loadCostsFrame():
  with streamlit.session_state["costsFrame"]:
    print("loadCostsFrame()")

    streamlit.subheader("Expenses")

    travelCosts = streamlit.radio("Travel Costs: ", ["Budget", "Standard", "Luxury"])
    streamlit.success(f"Travel Costs: {travelCosts}")
    streamlit.session_state["travelCosts"] = travelCosts


def getCurrentLocation():
  print ("getCurrentLocation() - Get Precise Client Location")

  loc = get_geolocation()

  if loc:
    print("Location data:", loc)
    print(f"Latitude: {loc['coords']['latitude']}")
    print(f"Longitude: {loc['coords']['longitude']}")

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

        print(f"getCurrentLocation() -> Current city: {current_city_name}, {current_country_name}")
        streamlit.session_state["current_city_name"] = current_city_name
        streamlit.session_state["current_country_name"] = current_country_name
        
      else:
        print("getCurrentLocation() -> No address found for the current location.")
    else:
      print("getCurrentLocation() -> Failed to get detailed location:", detailed_location_response.status_code)
  else:
    print("getCurrentLocation() -> Failed to get current location using get_geolocation().")
    streamlit.info("Click 'Allow' in your browser to share location.")


def loadTravelDetailsFrame():
  print("loadTravelDetailsFrame()")
  streamlit.header("Travel Dates and Passenger Details")

  streamlit.session_state["datesFrame"], streamlit.session_state["passengersFrame"], streamlit.session_state["costsFrame"] = streamlit.columns(3)

  # getCurrentLocation()
  loadTravelDatesFrame()
  loadPassengersFrame()
  loadCostsFrame()

  loadHolidaySlider()


class City(pydantic.BaseModel):
    rank: str
    city: str
    country: str
    interests: list[str]

def loadTop10Cities():
  print("loadTop10Cities()")
  # global destination, start_date, end_date, destinationColumn1
  destination = streamlit.session_state["destination"]
  start_date = streamlit.session_state["startDate"]
  end_date = streamlit.session_state["endDate"]
  # destinationColumn1 = streamlit.session_state["destinationColumn1"]

  genAIClient = streamlit.session_state["genAIClient"]

  travel_interests_str=" and ".join(streamlit.session_state["travel_interests"])

  if destination:
    top10cities_query=f"List the top 10 cities for tourism in {destination}"
    top10cities_query=f"{top10cities_query} for {travel_interests_str}"
    top10cities_query=f"{top10cities_query} during the period between {start_date} and {end_date}"
    print(f"loadTop10Cities() -> GenAI Query: {top10cities_query}")

    top10cities_response = genAIClient.models.generate_content(
      model="gemini-2.5-flash",
      contents=top10cities_query,
      config={
    	  "response_mime_type": "application/json",
        "response_schema": list[City]
      }
    )
    
    top10cities = json.loads(top10cities_response.text)
    print(f"loadTop10Cities() -> Top 10 cities response: {top10cities}")

    streamlit.session_state["top10cities"]=top10cities

    # with destinationColumn1:
    #   selected_cities=streamlit.multiselect("Select Cities: ", top10cities)

def loadDestinationColumn1():
  # global top10cities
  print("loadDestinationColumn1()")

  destination=streamlit.text_input("Destination (city / country / region): ")

  if streamlit.button("Load Cities to Visit"):
    streamlit.session_state["destination"]=destination
    loadTop10Cities()
    if "destination_description" in streamlit.session_state:
      del streamlit.session_state["destination_description"]

  if "top10cities" in streamlit.session_state:
    top10cities_list=[]
    for city_entry in streamlit.session_state["top10cities"]:
      top10cities_list.append(f"{city_entry['rank']}. {city_entry['city']}, {city_entry['country']}")
    streamlit.session_state["selected_cities"]=streamlit.multiselect("Top Cities to visit: ", top10cities_list)


def loadCurrentLocationMap():
  print("loadCurrentLocationMap()")
  # global current_city_name, current_country_name
  current_city_name = streamlit.session_state["current_city_name"]
  current_country_name = streamlit.session_state["current_country_name"]
  google_maps_api_key=streamlit.session_state["google_maps_api_key"]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  current_location=urllib.parse.quote_plus(f"{current_city_name},{current_country_name}")  # URL encode the current location

  map_marker = f"markers={current_location}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print("loadCurrentLocationMap() -> Google Maps API URL for current location:", google_maps_api_url)

  mapImageFile=open('current_location_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("loadCurrentLocationMap() -> Map for Current location generated successfully!")
  else:
    print("loadCurrentLocationMap() -> Failed to generate map for current location:", map_response.status_code)


def loadDestinationMap():
  print("loadDestinationMap()")
  # global destination

  google_maps_api_key = streamlit.session_state["google_maps_api_key"]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  urle_destination=urllib.parse.quote_plus(streamlit.session_state["destination"])  # URL encode the destination

  # map_marker = f"markers=color:blue%7Clabel:{map_destination}%7C{map_destination}"
  map_marker = f"markers={urle_destination}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print(f"loadDestinationMap() -> Google Maps API URL for destination: {google_maps_api_url}")

  mapImageFile=open('destination_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("loadDestinationMap() -> Map for Destination generated successfully!")
  else:
    print("loadDestinationMap() -> Failed to generate map for Destination:", map_response.status_code)

def loadMapSelectedCities():
  print("loadMapSelectedCities()")
  # global top10cities, destination

  google_maps_api_key = streamlit.session_state["google_maps_api_key"]
  
  streamlit.session_state["selected_cities_list"]=[]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  map_markers=[]

  for city_entry in streamlit.session_state["selected_cities"]:
    city_entry_num = city_entry.split('.')[0]
    city_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['city']
    country_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['country']

    streamlit.session_state["selected_cities_list"].append({'rank': city_entry_num, 'city': city_name, 'country': country_name})

    map_markers.append(f"markers=color:blue%7Clabel:{city_entry_num}%7C{urllib.parse.quote_plus(city_name)}%2C{urllib.parse.quote_plus(country_name)}")

  map_markers_str= '&'.join(map_markers)
  print("loadMapSelectedCities() -> Map markers:", map_markers_str)
     
  google_maps_api_url= f"{google_maps_api_url}{map_markers_str}&size=1000x500&key={google_maps_api_key}"
  # print("Google Maps API URL:", google_maps_api_url)
  mapImageFile=open('selected_cities_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("loadMapSelectedCities() -> Map generated successfully!")
  else:
    print("loadMapSelectedCities() -> Failed to generate map:", map_response.status_code)


def loadAddCityList():
  # global destination, start_date, end_date, destinationColumn1
  print("loadAddCityList()")

  genAIClient = streamlit.session_state["genAIClient"]

  if streamlit.session_state["search_city"]:
    search_city=streamlit.session_state["search_city"]
    destination=streamlit.session_state["destination"]
    search_city_query=f"Find cities with the name {search_city} near {destination}"
    print(f"loadAddCityList() -> GenAI Search Query: {search_city_query}")

    search_city_response = genAIClient.models.generate_content(
      model="gemini-2.5-flash",
      contents=search_city_query,
      config={
    	  "response_mime_type": "application/json",
        "response_schema": list[City]
      }
    )
    
    search_cities = json.loads(search_city_response.text)
    print(f"loadAddCityList() -> Search cities response: {search_cities}")
    streamlit.session_state["search_cities"] = search_cities

def addCityToList():
  print("addCityToList()")

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
    streamlit.session_state["selected_cities"].append(f"{new_city_rank}. {search_city_entry['city']}, {search_city_entry['country']}")

def loadDestinationColumn2():
  print("loadDestinationColumn2()")

  streamlit.session_state["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])
  streamlit.session_state["search_city"]=streamlit.text_input("Search additional cities: ")

  if streamlit.button("Search city"):
    loadAddCityList()

  if "search_cities" in streamlit.session_state:
    search_cities_list=[]
    for city_entry in streamlit.session_state["search_cities"]:
      search_cities_list.append(f"{city_entry['rank']}. {city_entry['city']}, {city_entry['country']}")
    streamlit.session_state["selected_search_cities"]=streamlit.multiselect("Select Cities to add: ", search_cities_list)

    if streamlit.button("Add Selected City to List"):
      addCityToList()

  if "selected_cities" in streamlit.session_state and streamlit.session_state["selected_cities"] != []:
    describeSelectedCities()
  elif "top10cities" in streamlit.session_state or "destination" in streamlit.session_state:
    describeDestination()
  else:
    print("loadDestinationColumn2() -> No description of current location")


def describeDestination():
  print("describeDestination()")

  genAIClient = streamlit.session_state["genAIClient"]
  destination=streamlit.session_state["destination"]

  if "destination_description" not in streamlit.session_state:
    describe_destination_query=f"Describe places to visit and things to do in {destination} with respect to tourism under 5 sentences"
    print(f"GenAI Describe City Query: {describe_destination_query}")

    describe_destination_response = genAIClient.models.generate_content(
      model="gemini-2.5-flash",
      contents=describe_destination_query
    )
    
    print(f"describeDestination() -> Describe ({destination}): {describe_destination_response.text}")
    streamlit.session_state["destination_description"] = describe_destination_response.text

  destination_desc=streamlit.session_state["destination_description"]
  streamlit.success(f"{destination} - {destination_desc}")


def describeSelectedCities():
  print("describeSelectedCities()")

  genAIClient = streamlit.session_state["genAIClient"]
  selected_cities=streamlit.session_state["selected_cities"]

  for city_entry in selected_cities:
    city_entry_num = city_entry.split('.')[0]
    city_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['city']
    country_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['country']

    if 'city_description' not in streamlit.session_state["top10cities"][int(city_entry_num)-1]:
    
      describe_city_query=f"Describe places to visit and things to do in {city_name},{country_name} with respect to tourism under 5 sentences"
      print(f"describeSelectedCities() -> GenAI Describe City Query: {describe_city_query}")

      describe_city_response = genAIClient.models.generate_content(
        model="gemini-2.5-flash",
        contents=describe_city_query
      )
    
      print(f"describeSelectedCities() -> Describe ({city_name},{country_name}): {describe_city_response.text}")
      streamlit.session_state["top10cities"][int(city_entry_num)-1]['city_description'] = describe_city_response.text

    city_description = streamlit.session_state["top10cities"][int(city_entry_num)-1]['city_description']
    streamlit.success(f"{city_entry_num}. {city_name},{country_name} - {city_description}")

def loadDestinationDetailsFrame():
  print("loadDestinationDetailsFrame()")
  streamlit.header("Destination Details")

  streamlit.session_state["destinationColumn1"], streamlit.session_state["destinationColumn2"], streamlit.session_state["mapColumn"] = streamlit.columns(3)

  with streamlit.session_state["destinationColumn1"]:
    loadDestinationColumn1()

  with streamlit.session_state["destinationColumn2"]:
    loadDestinationColumn2()

  with streamlit.session_state["mapColumn"]:
    if "selected_cities" in streamlit.session_state and streamlit.session_state["selected_cities"] != []:
      loadMapSelectedCities()
      streamlit.image("selected_cities_map.png")
    
    elif "top10cities" in streamlit.session_state or "destination" in streamlit.session_state:
      loadDestinationMap()
      streamlit.image("destination_map.png")
    
    else:
      loadCurrentLocationMap()
      streamlit.image("current_location_map.png")
  

  # with destinationFrame:
  #  globals()["destination"]=streamlit.text_input("Destination (city / country / region): ")
  #
  # with interestsFrame:
  #  globals()["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])

streamlit.title("AITinerary")
streamlit.set_page_config(page_title="AITinerary", layout="wide")

@streamlit.dialog("Enter Keys")
def enter_keys():
  gemini_api_key = streamlit.text_input ("Gemini API Key", type="password")
  google_maps_api_key = streamlit.text_input ("Google Maps API Key", type="password")
  if streamlit.button("Submit"):
    streamlit.session_state["gemini_api_key"] = gemini_api_key
    streamlit.session_state["google_maps_api_key"] = google_maps_api_key
    streamlit.session_state["genAIClient"] = genai.Client(api_key=gemini_api_key)
    streamlit.rerun()

if "gemini_api_key" not in streamlit.session_state or "google_maps_api_key" not in streamlit.session_state:
  enter_keys()
else:
  getCurrentLocation()
  current_city=streamlit.session_state["current_city_name"]
  current_country=streamlit.session_state["current_country_name"]
  current_location=f"{current_city}, {current_country}"
  streamlit.subheader(f"Current Location: {current_location}")

  streamlit.session_state["travelDetails"], streamlit.session_state["destinationDetails"], streamlit.session_state["detailedTravelPlan"] = streamlit.tabs(["Travel Details", "Destination Details", "Detailed Travel Plan"])
  with streamlit.session_state["travelDetails"]:
    loadTravelDetailsFrame()
  with streamlit.session_state["destinationDetails"]:
    loadDestinationDetailsFrame()