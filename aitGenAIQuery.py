import pydantic
import json
import streamlit
import enum


class Holiday(pydantic.BaseModel):
    holiday_start_date: str
    holiday_end_date: str
    reason: str

class HolidayList(pydantic.BaseModel):
    holiday_list: list[Holiday]


class City(pydantic.BaseModel):
    rank: str
    city: str
    country: str
    interests: list[str]

class CityList(pydantic.BaseModel):
    city_list: list[City]


class transportation(str, enum.Enum):
    BUS = "Bus"
    TRAIN = "Train"
    FLIGHT = "Flight"
    CAR = "Car"
    FERRY = "Ferry"

class TravelPlan(pydantic.BaseModel):
    travel_date: str
    start_city: str
    start_country: str
    end_city: str
    end_country: str
    transport_mode: transportation
    transport_number: str
    transport_company: str
    transport_cost: str
    start_time: str
    end_time: str
    travel_time: str
    daytrip_or_nightstay: str

class TravelPlanList(pydantic.BaseModel):
    travel_plan_list: list[TravelPlan]

class DestNameList(pydantic.BaseModel):
    dest_name_list: list[str]

################################################ NEW ########################################################


class JourneyLeg(pydantic.BaseModel):
    start_location: str
    end_location: str
    transport_mode: str
    transport_operator: str
    transport_number: str
    start_date: str
    start_time: str
    end_date: str
    end_time: str
    travel_time: str


class OnwardJourney(pydantic.BaseModel):
    travel_date: str
    start_city: str
    start_country: str
    end_city: str
    end_country: str
    journey_legs: list[JourneyLeg]


class VisitAttraction(pydantic.BaseModel):
    tourist_attraction: str
    start_location: str
    end_location: str
    transport_mode: str
    transport_operator: str
    transport_number: str
    start_time: str
    end_time: str
    travel_time: str
    tour_operator: str
    tour_activities: list[str]
    tour_time: str

class Daytrip(pydantic.BaseModel):
    tour_date: str
    daytrip_tours: list[VisitAttraction]

class LocalTravelPlan(pydantic.BaseModel):
    onward_journey: OnwardJourney
    daytrips: list[Daytrip]

class DetailedTravelPlan(pydantic.BaseModel):
    detailed_travel_plan: list[LocalTravelPlan]



################################################ NEW ########################################################


def executeGeminiQuery():
    if streamlit.session_state["response_format"] is None:
        gemini_config_response = None
    else:
        gemini_config_response = {
            "response_mime_type": "application/json",
            "response_schema": streamlit.session_state["response_format"]
        }

    genAIClient = streamlit.session_state["genAIClient"]
    gemini_query_response = genAIClient.models.generate_content(
        model="gemini-2.5-flash",
        contents=streamlit.session_state["genAIQuery"],
        config=gemini_config_response
    )

    if streamlit.session_state["response_format"] is None:
        streamlit.session_state["genAIQueryOutput"] = gemini_query_response.text
    else:
        gemini_query_response_json = json.loads(gemini_query_response.text)
        return_attribute = streamlit.session_state["return_attribute"]
        streamlit.session_state["genAIQueryOutput"] = gemini_query_response_json[return_attribute]



def executeOpenAIQuery():
    print("aitGenAIQuery.py -> executeOpenAIQuery()")

    genAIClient = streamlit.session_state["genAIClient"]

    if streamlit.session_state["response_format"] is None:
        openai_query_response = genAIClient.responses.parse(
            model="gpt-5",
            input=streamlit.session_state["genAIQuery"]
        )
    else:
        openai_query_response = genAIClient.responses.parse(
            model="gpt-5",
            input=streamlit.session_state["genAIQuery"],
            text_format=streamlit.session_state["response_format"]
        )

    openai_query_response_json = json.loads(openai_query_response.model_dump_json(indent=2))

    if streamlit.session_state["response_format"] is None:
        streamlit.session_state["genAIQueryOutput"] = openai_query_response_json["output"][1]["content"][0]["text"]
    else:
        return_attribute = streamlit.session_state["return_attribute"]
        streamlit.session_state["genAIQueryOutput"] = openai_query_response_json["output"][1]["content"][0]["parsed"][return_attribute]


def executeGenAIQuery():
    print("aitGenAIQuery.py -> executeGenAIQuery()")

    if streamlit.session_state["return_type"] is None:
        streamlit.session_state["response_format"] = None
    else:
        if streamlit.session_state["return_type"] == "TravelPlanList":
            streamlit.session_state["response_format"] = TravelPlanList
            streamlit.session_state["return_attribute"] = "travel_plan_list"
        elif streamlit.session_state["return_type"] == "CityList":
            streamlit.session_state["response_format"] = CityList
            streamlit.session_state["return_attribute"] = "city_list"
        elif streamlit.session_state["return_type"] == "HolidayList":
            streamlit.session_state["response_format"] = HolidayList
            streamlit.session_state["return_attribute"] = "holiday_list"
        elif streamlit.session_state["return_type"] == "DestNameList":
            streamlit.session_state["response_format"] = DestNameList
            streamlit.session_state["return_attribute"] = "dest_name_list"
        elif streamlit.session_state["return_type"] == "DetailedTravelPlan":
            streamlit.session_state["response_format"] = DetailedTravelPlan
            streamlit.session_state["return_attribute"] = "detailed_travel_plan"

    if streamlit.session_state["genai_client"] == "Gemini":
        print("aitGenAIQuery.py -> executeGenAIQuery() -> Executing GenAI Query in Gemini")
        executeGeminiQuery()
    elif streamlit.session_state["genai_client"] == "GPT-5":
        print("aitGenAIQuery.py -> executeGenAIQuery() -> Executing GenAI Query in OpenAI")
        executeOpenAIQuery()