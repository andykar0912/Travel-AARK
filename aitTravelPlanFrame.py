import streamlit
import urllib.parse
import requests

import aitGenAIQuery


def loadTravelPlanTable():
  print("aitTravelPlanFrame.py -> loadTravelPlanTable()")

  df_column_config = {
      "travel_date": streamlit.column_config.DateColumn("Travel Date"),
      "start_city": "Start City",
      "start_country": "Start Country",
      "end_city": "End City",
      "end_country": "End Country",
      "daytrip_or_nightstay": "Daytrip / Nightstay"
    }
  df_column_order = ["travel_date", "start_city", "start_country", "end_city", "end_country", "daytrip_or_nightstay"]

  streamlit.session_state["df_select_event"] = streamlit.dataframe(
    streamlit.session_state["detailed_travel_itinerary"],
    column_config=df_column_config,
    column_order=df_column_order,
    hide_index=True,
    on_select = "rerun",
    selection_mode="single-row"
  )


def loadTravelPlanChange():
  print("aitTravelPlanFrame.py -> loadTravelPlanChange()")

  travel_itinerary_change = streamlit.text_input("Please specify any changes you want to make to the Itinerary above (if any):")
  if streamlit.button("Update Itinerary") and travel_itinerary_change is not None:
    detailed_travel_itinerary = streamlit.session_state["detailed_travel_itinerary"]

    update_travel_itinerary_query=f"Update the travel itinerary {detailed_travel_itinerary} as per the request:"
    update_travel_itinerary_query=f"{update_travel_itinerary_query} {travel_itinerary_change}"

    print("aitTravelPlanFrame.py -> loadTravelPlanChange() -> GenAI Query for Changing Detailed Travel Plan: ", update_travel_itinerary_query)  
    
    streamlit.session_state["return_type"] = "TravelPlanList"
    streamlit.session_state["genAIQuery"] = update_travel_itinerary_query

    aitGenAIQuery.executeGenAIQuery()

    detailed_travel_itinerary = streamlit.session_state["genAIQueryOutput"]
    print("aitTravelPlanFrame.py -> loadTravelPlanChange() -> Updated Detailed Travel Itinerary response:", detailed_travel_itinerary)

    streamlit.session_state["previous_detailed_travel_itinerary"] = streamlit.session_state["detailed_travel_itinerary"]
    streamlit.session_state["detailed_travel_itinerary"] = detailed_travel_itinerary

    streamlit.rerun()

  if streamlit.button("Revert Itinerary"):
    streamlit.session_state["detailed_travel_itinerary"] = streamlit.session_state["previous_detailed_travel_itinerary"]
    streamlit.rerun()



def loadTravelPlanTableFrame():
  with streamlit.session_state["travelPlanTableFrame"]:
    print("aitTravelPlanFrame.py -> loadTravelPlanTableFrame()")

    loadTravelPlanTable()
    loadTravelPlanChange()



def generateDetailedTravelPlan():
  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan()")

  start_date=streamlit.session_state["startDate"]
  end_date=streamlit.session_state["endDate"]
  selected_cities_list=streamlit.session_state["selected_cities"]
  current_city=streamlit.session_state["current_city_name"]
  current_country=streamlit.session_state["current_country_name"]
  adult_count=streamlit.session_state["adults"]
  senior_count=streamlit.session_state["seniors"]
  children_count=streamlit.session_state["children"]

  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan() -> Selected cities for travel plan: ", selected_cities_list)

  if streamlit.session_state["travelCosts"] == "Budget":
    detailed_travel_itinerary_query=f"Create a travel plan for {selected_cities_list} with least costs"
  elif streamlit.session_state["travelCosts"] == "Standard":
    detailed_travel_itinerary_query=f"Create a travel plan for {selected_cities_list} with reasonable costs and travel time"
  elif streamlit.session_state["travelCosts"] == "Luxury":
    detailed_travel_itinerary_query=f"Create a travel plan for {selected_cities_list} with best travel time and comfort"

  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} starting on {start_date} at {current_city}, {current_country}"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} ending on {end_date} at {current_city}, {current_country}"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} travelling with {adult_count} adults, {children_count} children and {senior_count} seniors"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} add recommendation for Daytrip or Nightstay for each city"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} and for nightstay cities, include the recommended number of nightstays"

  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan() -> GenAI Query for Detailed Travel Plan: ", detailed_travel_itinerary_query)
  
  streamlit.session_state["return_type"] = "TravelPlanList"
  streamlit.session_state["genAIQuery"] = detailed_travel_itinerary_query

  aitGenAIQuery.executeGenAIQuery()

  detailed_travel_itinerary = streamlit.session_state["genAIQueryOutput"]
  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan() -> Detailed Travel Itinerary response:", detailed_travel_itinerary)
  streamlit.session_state["detailed_travel_itinerary"] = detailed_travel_itinerary



def loadTravelMap():
  if streamlit.session_state["df_select_event"].selection["rows"] != []:
    print("aitTravelPlanFrame.py -> loadTravelMap()")

    selected_row_index = streamlit.session_state["df_select_event"].selection["rows"][0]
    selected_row = []
    selected_row.append(streamlit.session_state["detailed_travel_itinerary"][selected_row_index])
    print("aitTravelPlanFrame.py -> loadTravelMap() -> Selected Row: ", selected_row)

    start_city = f"{selected_row[0]['start_city']}, {selected_row[0]['start_country']}"
    end_city = f"{selected_row[0]['end_city']}, {selected_row[0]['end_country']}"
    urlencoded_start_city=urllib.parse.quote_plus(f"{start_city}")
    urlencoded_end_city=urllib.parse.quote_plus(f"{end_city}")

    map_markers_str= f"markers=color:red%7Clabel:A%7C{urlencoded_start_city}&markers=color:red%7Clabel:B%7C{urlencoded_end_city}"
    map_path_str= f"path=color:blue%7Cweight:5%7C{urlencoded_start_city}%7C{urlencoded_end_city}"

    google_maps_api_key = streamlit.session_state["google_maps_api_key"]
    google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?{map_markers_str}&{map_path_str}&size=600x600&key={google_maps_api_key}"

    print(f"aitTravelPlanFrame.py -> loadTravelMap() -> Google Maps API URL for travel day {selected_row_index}:", google_maps_api_url)

    mapImageFile=open('travel_day_map.png', 'wb')
    map_response=requests.get(google_maps_api_url)
    if map_response.status_code == 200:
      mapImageFile.write(map_response.content)
      mapImageFile.close()
      print("aitTravelPlanFrame.py -> loadTravelMap() -> Map for Current location generated successfully!")
    else:
      print("aitTravelPlanFrame.py -> loadTravelMap() -> Failed to generate map for current location:", map_response.status_code)

    streamlit.image("travel_day_map.png")



def loadTravelMapframe():
  with streamlit.session_state["travelMapFrame"]:
    print("aitTravelPlanFrame.py -> loadTravelMapframe()")
    loadTravelMap()


def loadTravelCostFrame():
  if streamlit.session_state["df_select_event"].selection["rows"] != []:
    print("aitTravelPlanFrame.py -> loadTravelCostFrame()")

    selected_row_index = streamlit.session_state["df_select_event"].selection["rows"][0]
    selected_row = []
    selected_row.append(streamlit.session_state["detailed_travel_itinerary"][selected_row_index])
    print("aitTravelPlanFrame.py -> loadTravelCostFrame() -> Selected Row: ", selected_row)

    df_column_config = {
      "transport_mode": "Mode of Transport",
      "transport_company": "Tranport Provider Company",
      "transport_number": "Transport Number",
      "transport_cost": "Transport Cost",
      "start_time": "Time of Departure",
      "end_time": "Time of Arrival",
      "travel_time": "Travel Duration"
    }
    df_column_order = ["transport_mode", "transport_company", "transport_number", "transport_cost", "start_time", "end_time", "travel_time"]

    streamlit.session_state["df_travel_cost_event"] = streamlit.dataframe(
      selected_row,
      column_config=df_column_config,
      column_order=df_column_order,
      hide_index=True,
      on_select = "rerun",
      selection_mode="single-row"
    )


def loadDetailedTravelPlanFrame():
  print("aitTravelPlanFrame.py -> loadDetailedTravelPlanFrame()")

  if streamlit.button("Load Detailed Travel Plan"):
    if "selected_cities" not in streamlit.session_state or streamlit.session_state["selected_cities"] == []:
      print("aitTravelPlanFrame.py -> loadDetailedTravelPlanFrame() -> Selected Cities List empty")
    elif streamlit.session_state["startDate"] == streamlit.session_state["endDate"]:
      print("aitTravelPlanFrame.py -> loadDetailedTravelPlanFrame() -> Start date and End date for holiday can't be the same")
    else:
      print("aitTravelPlanFrame.py -> loadDetailedTravelPlanFrame() -> Generating Detailed Travel Plan")
      generateDetailedTravelPlan()

  if "detailed_travel_itinerary" in streamlit.session_state:
    streamlit.session_state["travelPlanTableFrame"], streamlit.session_state["travelMapFrame"] = streamlit.columns(2)

    loadTravelPlanTableFrame()
    loadTravelMapframe()

    loadTravelCostFrame()
    