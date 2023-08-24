import datetime
import json
import asyncio
from typing import Optional, List, Dict
from langchain.tools import StructuredTool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent


def get_flight_info(
    airline: str, flight_number: str, flight_date: str, direction: str
) -> str:
    """
    Gets full and accurate flight info from an external API whenever flight information is required

    Parameters:
    airline (_str_): Airline code of the airline (e.g. AA for American Airlines, etc..)
    flight_number (_str_): Flight number. (e.g. 1643, 6122, etc..)
    flight_date (_str_): Flight date in the format YYYY/MM/DD (e.g. 2023/08/10)
    direction (_str_): Either 'departing' or 'arriving'
    """
    print(
        f"airline: {airline}, flight_number: {flight_number}, flight_date: {flight_date}, direction: {direction}"
    )

    # here goes the API functionality. For now, let's assume this is the API's response, and what will be returned
    scheduledFlights = [
        {
            "carrierFsCode": f"{airline}",
            "flightNumber": f"{flight_number}",
            "departureAirportFsCode": "TPA",
            "arrivalAirportFsCode": "LGA",
            "departureTime": "2023-08-10T19:10:00.000",
            "arrivalTime": "2023-08-10T21:59:00.000",
            "stops": 0,
            "arrivalTerminal": "C",
            "flightEquipmentIataCode": "319",
            "isCodeshare": False,
            "isWetlease": False,
            "serviceType": "J",
            "serviceClasses": ["J", "Y"],
            "trafficRestrictions": [],
            "codeshares": [],
            "referenceCode": "2434-4815981--",
        },
        {
            "carrierFsCode": f"{airline}",
            "flightNumber": f"{flight_number}",
            "departureAirportFsCode": "LGA",
            "arrivalAirportFsCode": "TPA",
            "departureTime": "2023-08-10T15:01:00.000",
            "arrivalTime": "2023-08-10T18:10:00.000",
            "stops": 0,
            "departureTerminal": "C",
            "flightEquipmentIataCode": "319",
            "isCodeshare": False,
            "isWetlease": False,
            "serviceType": "J",
            "serviceClasses": ["J", "Y"],
            "trafficRestrictions": [],
            "codeshares": [
                {
                    "carrierFsCode": "WS",
                    "flightNumber": "6604",
                    "serviceType": "J",
                    "serviceClasses": ["R", "J", "Y"],
                    "trafficRestrictions": ["G"],
                    "referenceCode": 4252237,
                }
            ],
            "referenceCode": "2434-3970270--",
        },
    ]

    # if everything works smoothly, let's assume it did, return scheduledFlights
    return scheduledFlights


def create_reservation(
    pax_last_name: str,
    pax_first_name: str,
    booked_last_name: str,
    booked_first_name: str,
    booked_email: str,
    agent: str,
    flights: list,
    pax_cell: Optional[str] = None,
    travelers: Optional[int] = None,
    additional_travelers: Optional[List[Dict[str, str]]] = None,
    luggage: Optional[int] = None,
    booked_number: Optional[str] = None,
):
    """
    API for creating reservations in the reservation system.

    Parameters:
    **pax_last_name** (_str_): Last name of the passenger
    **pax_first_name** (_str_): First name of the passenger
    **booked_last_name** (_str_): Last name of the person booking the reservation
    **booked_first_name** (_str_): First name of the person booking the reservation
    **booked_email** (_str_): Email of the person booking the reservation
    **agent** (_str_): Name of the agent booking the reservation
    **flights** (_list_): List of flights. Each flight is a dictionary with the following keys: service_type ("ARR" for Arrivals, "DEP" for Departures, "CONN" for Connections), service_date, airline, flight_number, airport, time, airline_reference, departure_airport
    **pax_cell** (_str_, optional): Cell phone of the passenger
    **travelers** (_int_, optional): Number of travelers
    **additional_travelers** (_list_, optional): List of additional travelers. Each traveler is a dictionary with the following keys: "name"
    **luggage** (_int_, optional): Number of luggage
    **booked_number** (_str_, optional): Booking number of the reservation
    """
    try:
        # Validate mandatory parameters in flights

        print("\nentered create_reservation\n")

        # validating that all info in flights array is present
        for flight in flights:
            if not all(
                key in flight
                for key in [
                    "service_type",
                    "service_date",
                    "airline",
                    "flight_number",
                    "airport",
                ]
            ):
                raise ValueError(f"Missing mandatory parameters in flight: {flight}")

        #
        reservation = {
            "pax_last_name": pax_last_name,
            "pax_first_name": pax_first_name,
            "booked_last_name": booked_last_name,
            "booked_first_name": booked_first_name,
            "booked_email": booked_email,
            "agent": agent,
            "flights": flights,
            "pax_cell": pax_cell,
            "travelers": travelers,
            "additional_travelers": additional_travelers,
            "luggage": luggage,
            "booked_number": booked_number,
        }

        print("saving reservation")
        # save reservation dictionary in a json file
        with open("reservation.json", "w") as fp:
            json.dump(reservation, fp)

        return f"Reservation created for passenger {pax_first_name} {pax_last_name}."
    except Exception as e:
        print("\nException occurred creating reservation\n")
        print(str(e))
        return "Reservation couldn't be created. Someone from the team will get in touch with the passenger"


def function_to_deliver(email_subject: str, email_body: str):
    todays_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    openai_key = ""

    # this is where you'll declare the agent
    agents_instructions = f"""
	• You are a customer representative called Ruth and you work for CompanyA.
	• In every communication to customers, you will sign messages with "Ruth".
	• You will process requests if and only if requests are New Reservation Requests. If not, you will not process them.
    • (TODAY'S DATE AND TIME: {todays_date})
    """

    # THIS IS WHERE YOU WILL FILL IN THE AGENT CREATION WITH ITS TOOLS.
    # I SUGGEST DECLARING THE TOOLS LIKE SO:
    get_flights_info_tool = StructuredTool.from_function(get_flight_info)
    create_reservation_tool = StructuredTool.from_function(create_reservation)
    tools = [get_flights_info_tool, create_reservation_tool]

    command = f"""
    Given the sample email request in above, the expectation is for the agent to:
    • Call the get_flights_info twice, once for each flight
    • Call the create_reservation with the information from the email request and the information from the get_flights_info calls
    • Only response 'Thanks, Ruth' simply.
    """
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key="",
    )
    agent_chain = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    response = agent_chain.run(input=email_body + command)
    print(response)  # Chatbot Response


# SAMPLE EMAIL REQUEST
email_subject = "new bookings TPA"
email_body = """Dear team,
Please book new VIP services at TPA airport:
1 pax:
Dr. Emma Guttman

Arrival:
Date: Aug 26th
Flight: DL1636

Departure:
Date: Aug 27th
Flight: DL1118 at 15:25

Airline booking refence / record locator : HOFRNI

Please confirm.
Thanks,
Avishug

Booked By Info:
Name: Sample Name
Last Name: Sample Last Name
Email: booker@domains.com
Agent: Sample Name Sample Last Name
"""

# sample invoking the function that instantiates the agent.
function_to_deliver(email_subject, email_body)
