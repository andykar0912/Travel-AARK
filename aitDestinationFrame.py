import streamlit
import requests
import urllib.parse

import aitGenAIQuery

def loadTop10Cities():
  print("aitDestinationFrame.py -> loadTop10Cities()")
  # global destination, start_date, end_date, destinationColumn1
  destination = streamlit.session_state["destination"]
  start_date = streamlit.session_state["startDate"]
  end_date = streamlit.session_state["endDate"]
  # destinationColumn1 = streamlit.session_state["destinationColumn1"]

  travel_interests_str=" and ".join(streamlit.session_state["travel_interests"])

  if destination:
    top10cities_query=f"List the top 10 cities for tourism in and around {destination}"
    top10cities_query=f"{top10cities_query} for {travel_interests_str}"
    top10cities_query=f"{top10cities_query} during the period between {start_date} and {end_date}"
    print(f"aitDestinationFrame.py -> loadTop10Cities() -> GenAI Query: {top10cities_query}")

    streamlit.session_state["return_type"] = "CityList"
    streamlit.session_state["genAIQuery"] = top10cities_query

    aitGenAIQuery.executeGenAIQuery()
    top10cities = streamlit.session_state["genAIQueryOutput"]
    print(f"aitDestinationFrame.py -> loadTop10Cities() -> Top 10 cities response: {top10cities}")

    streamlit.session_state["top10cities"]=top10cities



def loadAddCityList():
  # global destination, start_date, end_date, destinationColumn1
  print("aitDestinationFrame.py -> loadAddCityList()")

  if streamlit.session_state["search_city"]:
    search_city=streamlit.session_state["search_city"]
    destination=streamlit.session_state["destination"]
    search_city_query=f"Find cities with the name {search_city} near {destination}"
    print(f"aitDestinationFrame.py -> loadAddCityList() -> GenAI Search Query: {search_city_query}")

    streamlit.session_state["return_type"] = "CityList"
    streamlit.session_state["genAIQuery"] = search_city_query

    aitGenAIQuery.executeGenAIQuery()
    search_cities = streamlit.session_state["genAIQueryOutput"]
    print(f"aitDestinationFrame.py -> loadAddCityList() -> Search cities response: {search_cities}")
    streamlit.session_state["search_cities"] = search_cities


def addCityToList():
  print("aitDestinationFrame.py -> addCityToList()")

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



def loadDestinationColumn1():
  # global top10cities
  print("aitDestinationFrame.py -> loadDestinationColumn1()")

  if "destination" in streamlit.session_state:
    destination=streamlit.text_input(
      label="Destination (city / country / region): ",
      value=streamlit.session_state["destination"]
    )
  else:
    destination=streamlit.text_input(label="Destination (city / country / region): ")

  streamlit.session_state["travel_interests"]=streamlit.multiselect("Choose interests: ", ["Kids", "Beach", "Skiing", "History", "Romance", "Party"])

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


def describeSelectedCities():
  print("aitDestinationFrame.py -> describeSelectedCities()")

  selected_cities=streamlit.session_state["selected_cities"]

  for city_entry in selected_cities:
    city_entry_num = city_entry.split('.')[0]
    city_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['city']
    country_name=streamlit.session_state["top10cities"][int(city_entry_num)-1]['country']

    if 'city_description' not in streamlit.session_state["top10cities"][int(city_entry_num)-1]:
    
      describe_city_query=f"Describe places to visit and things to do in {city_name},{country_name} with respect to tourism under 5 sentences"
      print(f"aitDestinationFrame.py -> describeSelectedCities() -> GenAI Describe City Query: {describe_city_query}")

      streamlit.session_state["return_type"] = None
      streamlit.session_state["genAIQuery"] = describe_city_query

      aitGenAIQuery.executeGenAIQuery()
      describe_city_response = streamlit.session_state["genAIQueryOutput"]
    
      print(f"aitDestinationFrame.py -> describeSelectedCities() -> Describe ({city_name},{country_name}): {describe_city_response}")
      streamlit.session_state["top10cities"][int(city_entry_num)-1]['city_description'] = describe_city_response

    city_description = streamlit.session_state["top10cities"][int(city_entry_num)-1]['city_description']
    streamlit.success(f"{city_entry_num}. {city_name},{country_name} - {city_description}")


def describeDestination():
  print("aitDestinationFrame.py -> describeDestination()")

  destination=streamlit.session_state["destination"]

  if "destination_description" not in streamlit.session_state:
    describe_destination_query=f"Describe places to visit and things to do in {destination} with respect to tourism under 5 sentences"
    print(f"aitDestinationFrame.py -> GenAI Describe City Query: {describe_destination_query}")

    streamlit.session_state["return_type"] = None
    streamlit.session_state["genAIQuery"] = describe_destination_query

    aitGenAIQuery.executeGenAIQuery()

    describe_destination_response = streamlit.session_state["genAIQueryOutput"]
    print(f"aitDestinationFrame.py -> describeDestination() -> Describe ({destination}): {describe_destination_response}")
    streamlit.session_state["destination_description"] = describe_destination_response

  destination_desc=streamlit.session_state["destination_description"]
  streamlit.success(f"{destination} - {destination_desc}")



def loadDestinationColumn2():
  print("aitDestinationFrame.py -> loadDestinationColumn2()")

  if streamlit.button("Load Top 10 Destination Recommendations"):
    current_city_name = streamlit.session_state["current_city_name"]
    current_country_name = streamlit.session_state["current_country_name"]
    current_city = f"{current_city_name}, {current_country_name}"

    start_date = streamlit.session_state["startDate"]
    end_date = streamlit.session_state["endDate"]

    top10destinations_query = f"List the top 10 destinations over the world"
    top10destinations_query = f"{top10destinations_query} recommended for tourists from {current_city}"
    top10destinations_query = f"{top10destinations_query} travelling during the period from {start_date} to {end_date}"
    top10destinations_query = f"{top10destinations_query} including names of region of the world"

    print("aitDestinationFrame.py -> loadDestinationColumn2() -> GenAI query for Top 10 recommended destination: ", top10destinations_query)

    streamlit.session_state["return_type"] = "DestNameList"
    streamlit.session_state["genAIQuery"] = top10destinations_query

    aitGenAIQuery.executeGenAIQuery()
    
    recommended_destinations = streamlit.session_state["genAIQueryOutput"]
    streamlit.session_state["recommended_destinations"] = recommended_destinations
    print(f"aitDestinationFrame.py -> loadDestinationColumn2() -> Top 10 recommended destinations response: {recommended_destinations}")

  if "recommended_destinations" in streamlit.session_state:
    streamlit.session_state["recommended_destination_selected"] = streamlit.selectbox(
      "Top 10 Recommended Destinations",
      streamlit.session_state["recommended_destinations"],
      index=None,
      placeholder="Recommended Destinations"
    )

    if "recommended_destination_selected" in streamlit.session_state and streamlit.session_state["recommended_destination_selected"] is not None:
      if streamlit.button("Choose Destination"):
        streamlit.session_state["destination"] = streamlit.session_state["recommended_destination_selected"]

  if "selected_cities" in streamlit.session_state and streamlit.session_state["selected_cities"] != []:
    describeSelectedCities()
  elif "top10cities" in streamlit.session_state or "destination" in streamlit.session_state:
    describeDestination()
  else:
    print("aitDestinationFrame.py -> loadDestinationColumn2() -> Print current location")
    current_city = streamlit.session_state["current_city_name"]
    current_country = streamlit.session_state["current_country_name"]
    current_location = f"{current_city} ({current_country})"
    streamlit.success(f"Current Location: {current_location}")


def loadMapSelectedCities():
  print("aitDestinationFrame.py -> loadMapSelectedCities()")
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
  print("aitDestinationFrame.py -> loadMapSelectedCities() -> Map markers:", map_markers_str)
     
  google_maps_api_url= f"{google_maps_api_url}{map_markers_str}&size=1000x500&key={google_maps_api_key}"
  # print("Google Maps API URL:", google_maps_api_url)
  mapImageFile=open('selected_cities_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("aitDestinationFrame.py -> loadMapSelectedCities() -> Map generated successfully!")
  else:
    print("aitDestinationFrame.py -> loadMapSelectedCities() -> Failed to generate map:", map_response.status_code)



def loadDestinationMap():
  print("aitDestinationFrame.py -> loadDestinationMap()")
  # global destination

  google_maps_api_key = streamlit.session_state["google_maps_api_key"]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  urle_destination=urllib.parse.quote_plus(streamlit.session_state["destination"])  # URL encode the destination

  # map_marker = f"markers=color:blue%7Clabel:{map_destination}%7C{map_destination}"
  map_marker = f"markers={urle_destination}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print(f"aitDestinationFrame.py -> loadDestinationMap() -> Google Maps API URL for destination: {google_maps_api_url}")

  mapImageFile=open('destination_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("aitDestinationFrame.py -> loadDestinationMap() -> Map for Destination generated successfully!")
  else:
    print("aitDestinationFrame.py -> loadDestinationMap() -> Failed to generate map for Destination:", map_response.status_code)



def loadCurrentLocationMap():
  print("aitDestinationFrame.py -> loadCurrentLocationMap()")
  # global current_city_name, current_country_name
  current_city_name = streamlit.session_state["current_city_name"]
  current_country_name = streamlit.session_state["current_country_name"]
  google_maps_api_key=streamlit.session_state["google_maps_api_key"]

  google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?"
  current_location=urllib.parse.quote_plus(f"{current_city_name},{current_country_name}")  # URL encode the current location

  map_marker = f"markers={current_location}"

  google_maps_api_url= f"{google_maps_api_url}{map_marker}&size=600x600&key={google_maps_api_key}"
  print("aitDestinationFrame.py -> loadCurrentLocationMap() -> Google Maps API URL for current location:", google_maps_api_url)

  mapImageFile=open('current_location_map.png', 'wb')
  map_response=requests.get(google_maps_api_url)

  if map_response.status_code == 200:
    mapImageFile.write(map_response.content)
    mapImageFile.close()
    print("aitDestinationFrame.py -> loadCurrentLocationMap() -> Map for Current location generated successfully!")
  else:
    print("aitDestinationFrame.py -> loadCurrentLocationMap() -> Failed to generate map for current location:", map_response.status_code)



def loadDestinationDetailsFrame():
  print("aitDestinationFrame.py -> loadDestinationDetailsFrame()")
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
