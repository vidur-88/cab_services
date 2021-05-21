How to Run:
-------
- Install python3
- create virtual env: `virtualenv --no-site-packages ENV`
- Activate virtual env: `source ENV/bin/activate`
- Install requirements: `pip install requirements.txt`
- run application: `python3 api.py`

Now you can connect the server: http://127.0.0.1:5000/

APIs:
----
server-name = http://127.0.0.1:5000

- City:
    - /add_city (POST) - For adding city
        - params: `{"name": "Pune", "state_name": "Maharashtra"}`
        - Response: `{
    "city_id": 2,
    "message": "city added successfully"
}`
    - /cities (GET) - For getting all cities
        - Response: `[
    {
        "city_id": 1,
        "name": "Mumbai"
    },
    {
        "city_id": 2,
        "name": "Pune"
    }
]`
- Cab:
    - /cab_register (POST) - for registering new cab to portal
        - params: `{"company_name": "Ford",
                    "model_name": "Figo",
                    "city_id": 2,
                    "type": "HatchBack",
                    "driver_name": "xyz",
                    "rc_number": "MH14CC1234"}`
       
        - response: `"message": "cab registered successfully, id: 2"
}`
    - /cab_list (GET) - All idle cab for
        - params: `{"city_id": 2}` 
        - Response:  `[{"cab_id": 1, 
            "company_name": "Ford", 
            "model_name": "Figo", 
            "rc_number": "MH03CC1234",
        "state": "IDLE",
        "type": "HatchBack"
    },
    {
        "cab_id": 2,
        "company_name": "Ford",
        "model_name": "Figo",
        "rc_number": "MH14CC1234",
        "state": "IDLE",
        "type": "HatchBack"
    }]`
    - /cab_state_history (GET) - Get the cab idle state history in given duration
        - params: `{
                "cab_id": 1,
                "duration": ["2021-05-20 18:00:00", "2021-05-20 19:00:00"]
            }`
        - Response: `[
            {
                "cab_id": 1,
                "idle_seconds": 3555
            }
        ]`
        - cab_id in request param is optional if not given will give all cab list in given duration.
- Booking
    - /booking (POST) - Book the cab
        - params: `{
            "cab_id": 1,
            "start_city_id": 1,
            "end_city_id": 2,
            "client_id": 12
            }`
        - Response: `{
            "booking_id": 1,
            "message": "Booking successfully"
        }`
    - /end_trip (POST) - Ending the trip
        - Params: `{
            "booking_id": 1,
            "end_city_id": 2,
            "cab_id": 1
        }`
        - Response: `{
            "booking_id": 1,
            "message": "End trip, thanks!"
        }`