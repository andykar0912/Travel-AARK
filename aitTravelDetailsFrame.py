import streamlit
import datetime

import aitGenAIQuery


def loadTravelDatesFrame():
  with streamlit.session_state["datesFrame"]:
    
    print("aitTravelDetailsFrame.py -> loadTravelDatesFrame()")
  
    streamlit.subheader("Dates")

    streamlit.session_state["startDate"] = streamlit.date_input("Start Date: ")
    streamlit.session_state["endDate"] = streamlit.date_input("End Date: ")
   
    number_of_days=streamlit.session_state["endDate"]-streamlit.session_state["startDate"]
    streamlit.success(f"Number of Days: {number_of_days}")
    streamlit.session_state["number_of_days"] = number_of_days


def loadPassengersFrame():
  with streamlit.session_state["passengersFrame"]:
    print("aitTravelDetailsFrame.py -> loadPassengersFrame()")

    streamlit.subheader("Passengers")

    streamlit.session_state["adults"]=streamlit.text_input("No. of adults: ")
    streamlit.session_state["seniors"]=streamlit.text_input("No. of seniors (>60 years): ")
    streamlit.session_state["children"]=streamlit.text_input("No. of children: ")



def loadCostsFrame():
  with streamlit.session_state["costsFrame"]:
    print("aitTravelDetailsFrame.py -> loadCostsFrame()")

    streamlit.subheader("Expenses")

    travelCosts = streamlit.radio("Travel Costs: ", ["Budget", "Standard", "Luxury"])
    streamlit.success(f"Travel Costs: {travelCosts}")
    streamlit.session_state["travelCosts"] = travelCosts


def loadHolidays():
  print("aitTravelDetailsFrame.py -> loadHolidays()")

  current_city = streamlit.session_state["current_city_name"]
  current_country = streamlit.session_state["current_country_name"]
  current_location = f"{current_city} ({current_country})"
  
  genAIClient = streamlit.session_state["genAIClient"]
  month_slider = streamlit.session_state["month_slider"]

  current_date=datetime.date.today()
  
  last_date=current_date+datetime.timedelta(days=30*month_slider)
  print(f"aitTravelDetailsFrame.py -> Current date: {current_date}")
  print(f"aitTravelDetailsFrame.py -> Date after {month_slider} months: {last_date}")
  
  location_holiday_query=f"Between {current_date} and {last_date}"
  location_holiday_query=f"{location_holiday_query} list the first weekend of the period"
  location_holiday_query=f"{location_holiday_query} and long weekends and vacations in {current_location}"
  print(f"aitTravelDetailsFrame.py -> loadHolidays() -> GenAI Query: {location_holiday_query}")

  streamlit.session_state["return_type"] = "HolidayList"
  streamlit.session_state["genAIQuery"] = location_holiday_query

  aitGenAIQuery.executeGenAIQuery()
  holidays_list = streamlit.session_state["genAIQueryOutput"]
  print(f"aitTravelDetailsFrame.py -> loadHolidays() -> List next Holidays (in {month_slider} months) response: {holidays_list}")
  streamlit.session_state["holidays_list"]=holidays_list



def loadHolidaySlider():
  print("aitTravelDetailsFrame.py -> loadHolidaySlider()")

  current_city = streamlit.session_state["current_city_name"]
  current_country = streamlit.session_state["current_country_name"]
  current_location = f"{current_city} ({current_country})"
  
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
    # streamlit.success(f"{holiday_entry['reason']}: from {holiday_entry['holiday_start_date']} to {holiday_entry['holiday_end_date']}")
    streamlit.success(f"{holiday_entry['holiday_start_date']} to {holiday_entry['holiday_end_date']}: {holiday_entry['reason']}")



def loadTravelDetailsFrame():
  print("aitTravelDetailsFrame.py -> loadTravelDetailsFrame()")
  streamlit.header("Travel Dates and Passenger Details")

  streamlit.session_state["datesFrame"], streamlit.session_state["passengersFrame"], streamlit.session_state["costsFrame"] = streamlit.columns(3)

  # getCurrentLocation()
  loadTravelDatesFrame()
  loadPassengersFrame()
  loadCostsFrame()

  loadHolidaySlider()

