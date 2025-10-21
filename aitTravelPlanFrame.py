import streamlit
import urllib.parse
import requests
import json

import aitGenAIQuery


def selectTravelPlanEntry():
  print("aitTravelPlanFrame.py -> selectTravelPlanEntry()")

  streamlit.session_state["show_map_entry"] = "Travel Plan Entry"


def selectJourneyLegEntry():
  print("aitTravelPlanFrame.py -> selectJourneyLegEntry()")

  streamlit.session_state["show_map_entry"] = "Journey Leg Entry"


def selectDaytripEntry():
  print("aitTravelPlanFrame.py -> selectDaytripEntry()")

  streamlit.session_state["show_map_entry"] = "Daytrip Entry"


def loadTravelPlanTable():
  print("aitTravelPlanFrame.py -> loadTravelPlanTable()")

  streamlit.markdown("***Travel Plan***")

  df_column_config = {
      "travel_date": streamlit.column_config.DateColumn("Travel Date"),
      "start_city": "Start City",
      "start_country": "Start Country",
      "end_city": "End City",
      "end_country": "End Country"
    }
  df_column_order = ["travel_date", "start_city", "start_country", "end_city", "end_country"]

  travel_plan = []
  for entries in streamlit.session_state["detailed_travel_itinerary"]:
    onward_journey_entry = entries["onward_journey"]
    travel_plan.append(onward_journey_entry)

  print(f"aitTravelPlanFrame.py -> loadTravelPlanTable() -> Travel Plan: {travel_plan}")

  streamlit.session_state["df_tp_select_event"] = streamlit.dataframe(
    travel_plan,
    column_config=df_column_config,
    column_order=df_column_order,
    hide_index=True,
    on_select = selectTravelPlanEntry,
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
    
    streamlit.session_state["return_type"] = "DetailedTravelPlan"
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


def loadJourneyLegs():
  if streamlit.session_state["df_tp_select_event"].selection["rows"] != []:
    print("aitTravelPlanFrame.py -> loadJourneyLegs()")

    selected_row_index = streamlit.session_state["df_tp_select_event"].selection["rows"][0]
    onward_journey_legs = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["onward_journey"]["journey_legs"]
    print(f"aitTravelPlanFrame.py -> loadJourneyLegs() -> Onward Journey Legs: {onward_journey_legs}")

    from_city = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["onward_journey"]["start_city"]
    from_country = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["onward_journey"]["start_country"]

    to_city = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["onward_journey"]["end_city"]
    to_country = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["onward_journey"]["end_country"]

    streamlit.markdown(f"***{from_city}, {from_country} -> {to_city}, {to_country}***")

    df_column_config = {
        "start_location": "Start Location",
        "end_location": "End Location",
        "transport_mode": "Transport Mode",
        "transport_operator": "Transport Operator",
        "transport_number": "Transport Number",
        "start_date": streamlit.column_config.DateColumn("Departure Date"),
        "start_time": streamlit.column_config.TimeColumn("Departure Time"),
        "end_date": streamlit.column_config.DateColumn("Arrival Date"),
        "end_time": streamlit.column_config.TimeColumn("Arrival Time"),
        "travel_time": "Total Travel Time"
      }
    df_column_order = ["start_location", "end_location", "transport_mode", "transport_operator", "transport_number", "start_date", "start_time", "end_date", "end_time", "travel_time"]

    streamlit.session_state["df_jl_select_event"] = streamlit.dataframe(
      onward_journey_legs,
      column_config=df_column_config,
      column_order=df_column_order,
      hide_index=True,
      on_select = selectJourneyLegEntry,
      selection_mode="single-row"
    )

def loadDaytrips():
  if streamlit.session_state["df_tp_select_event"].selection["rows"] != []:
    print("aitTravelPlanFrame.py -> loadDaytrips()")

    selected_row_index = streamlit.session_state["df_tp_select_event"].selection["rows"][0]
    daytrip_city = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]['onward_journey']['end_city']
    daytrip_country = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]['onward_journey']['end_country']

    if streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["daytrips"] != []:
      print(f"aitTravelPlanFrame.py -> loadDaytrips() -> Load Daytrips in {daytrip_city}, {daytrip_country}")
      streamlit.markdown(f"***Daytrips in {daytrip_city}, {daytrip_country}***")

      # daytrips = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["daytrips"]
      # location_daytrips = streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["daytrips"]

      streamlit.session_state["daytrips"] = []
      for daytrip_entry in streamlit.session_state["detailed_travel_itinerary"][selected_row_index]["daytrips"]:
        tour_date = daytrip_entry["tour_date"]
        tour_city = f"{daytrip_city}, {daytrip_country}"
        for daytrip_tours_entry in daytrip_entry["daytrip_tours"]:
          new_daytrip_entry = {
            "tour_city": tour_city,
            "tour_date": tour_date,
            "tourist_attraction": daytrip_tours_entry["tourist_attraction"],
            "start_location": daytrip_tours_entry["start_location"],
            "end_location": daytrip_tours_entry["end_location"],
            "transport_mode": daytrip_tours_entry["transport_mode"],
            "transport_operator": daytrip_tours_entry["transport_operator"],
            "transport_number": daytrip_tours_entry["transport_number"],
            "start_time": daytrip_tours_entry["start_time"],
            "end_time": daytrip_tours_entry["end_time"],
            "travel_time": daytrip_tours_entry["travel_time"],
            "tour_operator": daytrip_tours_entry["tour_operator"],
            "tour_activities": daytrip_tours_entry["tour_activities"],
            "tour_time": daytrip_tours_entry["tour_time"]
          }
          streamlit.session_state["daytrips"].append(new_daytrip_entry)


      df_column_config = {
          "tour_city": "City",
          "tour_date": streamlit.column_config.DateColumn("Tour Date"),
          "tourist_attraction": "Tourist Attraction",
          "start_location": "Start From",
          "end_location": "Go to",
          "transport_mode": "Transport Mode",
          "transport_operator": "Transport Operator",
          "transport_number": "Transport Number",
          "start_time": streamlit.column_config.TimeColumn("Departure Time"),
          "end_time": streamlit.column_config.TimeColumn("Arrival Time"),
          "travel_time": "Travel Time",
          "tour_operator": "Tour Operator",
          "tour_activities": "Tour Activities",
          "tour_time": "Total Tour time"
        }
      df_column_order = ["tour_city", "tour_date", "tourist_attraction", "start_location", "end_location", "transport_mode", "transport_operator", "transport_number", "start_time", "end_time", "travel_time", "tour_operator", "tour_activities", "tour_time"]

      streamlit.session_state["df_dt_select_event"] = streamlit.dataframe(
        streamlit.session_state["daytrips"],
        column_config=df_column_config,
        column_order=df_column_order,
        hide_index=True,
        on_select = selectDaytripEntry,
        selection_mode="single-row"
      )
    else:
      print(f"aitTravelPlanFrame.py -> loadDaytrips() -> No Daytrips in {daytrip_city}, {daytrip_country}")
      del streamlit.session_state["df_dt_select_event"]


def loadTravelPlanTableFrame():
  with streamlit.session_state["travelPlanTableFrame"]:
    print("aitTravelPlanFrame.py -> loadTravelPlanTableFrame()")

    loadTravelPlanTable()
    # loadTravelPlanChange()

    loadJourneyLegs()



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
    detailed_travel_itinerary_query=f"Create a Detailed travel plan for {selected_cities_list} with least costs"
  elif streamlit.session_state["travelCosts"] == "Standard":
    detailed_travel_itinerary_query=f"Create a Detailed travel plan for {selected_cities_list} with reasonable costs and travel time"
  elif streamlit.session_state["travelCosts"] == "Luxury":
    detailed_travel_itinerary_query=f"Create a Detailed travel plan for {selected_cities_list} with best travel time and comfort"

  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} starting on {start_date} at {current_city}, {current_country}"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} ending on {end_date} at {current_city}, {current_country}"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} travelling with {adult_count} adults, {children_count} children and {senior_count} seniors"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} with journey legs being part of the onward journey"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} include the hotel name as per the budget"
  detailed_travel_itinerary_query=f"{detailed_travel_itinerary_query} include travelling to the hotel as a journey leg within onward journey"

  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan() -> GenAI Query for Detailed Travel Plan: ", detailed_travel_itinerary_query)
  
  streamlit.session_state["return_type"] = "DetailedTravelPlan"
  streamlit.session_state["genAIQuery"] = detailed_travel_itinerary_query

  aitGenAIQuery.executeGenAIQuery()

  detailed_travel_itinerary = streamlit.session_state["genAIQueryOutput"]
  print("aitTravelPlanFrame.py -> generateDetailedTravelPlan() -> Detailed Travel Itinerary response:", json.dumps(detailed_travel_itinerary, indent=2))
  streamlit.session_state["detailed_travel_itinerary"] = detailed_travel_itinerary


def loadTravelMap():
  print("aitTravelPlanFrame.py -> loadTravelMap()")

  if "show_map_entry" in streamlit.session_state:

    if streamlit.session_state["show_map_entry"] == "Daytrip Entry":
      print("aitTravelPlanFrame.py -> loadTravelMap() -> for Daytrip Select Event")
      selected_row_index_dt = streamlit.session_state["df_dt_select_event"].selection["rows"][0]

      from_location = streamlit.session_state["daytrips"][selected_row_index_dt]["start_location"]
      to_location = streamlit.session_state["daytrips"][selected_row_index_dt]["end_location"]

      print(f"aitTravelPlanFrame.py -> loadTravelMap() -> Selected Row in Daytrip Table from: {from_location} to {to_location}")

    elif streamlit.session_state["show_map_entry"] == "Journey Leg Entry":
      print("aitTravelPlanFrame.py -> loadTravelMap() -> for Journey Leg Select Event")
      selected_row_index_tp = streamlit.session_state["df_tp_select_event"].selection["rows"][0]
      selected_row_index = streamlit.session_state["df_jl_select_event"].selection["rows"][0]

      from_location = f"{streamlit.session_state['detailed_travel_itinerary'][selected_row_index_tp]['onward_journey']['journey_legs'][selected_row_index]['start_location']}"
      to_location = f"{streamlit.session_state['detailed_travel_itinerary'][selected_row_index_tp]['onward_journey']['journey_legs'][selected_row_index]['end_location']}"

      print(f"aitTravelPlanFrame.py -> loadTravelMap() -> Selected Row in Onward Journey Table from: {from_location} to {to_location}")

    elif streamlit.session_state["show_map_entry"] == "Travel Plan Entry":
      print("aitTravelPlanFrame.py -> loadTravelMap() -> for Travel Plan Select Event")
      selected_row_index = streamlit.session_state["df_tp_select_event"].selection["rows"][0]

      from_location = f"{streamlit.session_state['detailed_travel_itinerary'][selected_row_index]['onward_journey']['start_city']}, {streamlit.session_state['detailed_travel_itinerary'][selected_row_index]['onward_journey']['start_country']}"
      to_location = f"{streamlit.session_state['detailed_travel_itinerary'][selected_row_index]['onward_journey']['end_city']}, {streamlit.session_state['detailed_travel_itinerary'][selected_row_index]['onward_journey']['end_country']}"

      print(f"aitTravelPlanFrame.py -> loadTravelMap() -> Selected Row in Travel Plan table: {from_location} -> {to_location}")

    urlencoded_from_location=urllib.parse.quote_plus(f"{from_location}")
    urlencoded_to_location=urllib.parse.quote_plus(f"{to_location}")

    map_markers_str= f"markers=color:red%7Clabel:A%7C{urlencoded_from_location}&markers=color:red%7Clabel:B%7C{urlencoded_to_location}"
    map_path_str= f"path=color:blue%7Cweight:5%7C{urlencoded_from_location}%7C{urlencoded_to_location}"

    google_maps_api_key = streamlit.session_state["google_maps_api_key"]
    google_maps_api_url = f"https://maps.googleapis.com/maps/api/staticmap?{map_markers_str}&{map_path_str}&size=600x600&key={google_maps_api_key}"

    print(f"aitTravelPlanFrame.py -> loadTravelMap() -> Google Maps API URL for travel from {from_location} to {to_location}:", google_maps_api_url)

    mapImageFile=open('travel_day_map.png', 'wb')
    map_response=requests.get(google_maps_api_url)
    if map_response.status_code == 200:
      mapImageFile.write(map_response.content)
      mapImageFile.close()
      print("aitTravelPlanFrame.py -> loadTravelMap() -> Map for Current location generated successfully!")
    else:
      print("aitTravelPlanFrame.py -> loadTravelMap() -> Failed to generate map for current location:", map_response.status_code)

    streamlit.image("travel_day_map.png")

  else:
    print("aitTravelPlanFrame.py -> loadTravelMap() -> No entry from Travel Plan Table selected yet")



def loadTravelMapframe():
  with streamlit.session_state["travelMapFrame"]:
    print("aitTravelPlanFrame.py -> loadTravelMapframe()")
    loadTravelMap()



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
    loadDaytrips()

    loadTravelMapframe()

  print("aitTravelPlanFrame.py -> loadDetailedTravelPlanFrame() -> Re-Initialize show_map_entry")
  if "show_map_entry" in streamlit.session_state:
    del streamlit.session_state["show_map_entry"]
