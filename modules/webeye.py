import requests, reverse_geocode

session = requests.Session()
session.headers = {"User-Agent": "XU-Statistics/1.0.0"}
COUNTRY_IDS = ["GB", "IE"]

def is_uk(coords: tuple): # (LAT, LONG)
    try:
        geo = reverse_geocode.get(coords)
        if geo["country_code"] in COUNTRY_IDS: return [True, "Successfully pulled geo data", geo["city"], geo["county"]]
        return [False, f"Country was not {'/'.join(COUNTRY_IDS)}", None, None]
    except: return [False, "An error has occured.", "Error", "Error"]

def get_webeye(stat: str):
    if stat not in ["ATC", "Pilot_Inbound", "Pilot_Outbound", "Pilot_In_Airspace", "Pilot_VFR", "Network_Online"]: return [False, "An invalid statistic was requested."]

    if stat == "ATC":
        r = session.get("https://api.ivao.aero/v2/tracker/now/atc/summary")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        atc = []
        for controller in rjs:
            if ("atcPosition" in controller and controller["atcPosition"] != None and "airport" in controller["atcPosition"] \
            and controller["atcPosition"]["airport"]["countryId"] in COUNTRY_IDS) or ("subcenter" in controller and controller["subcenter"] != None \
            and controller["subcenter"]["longitude"] != None and controller["subcenter"]["latitude"] != None \
            and is_uk((controller["subcenter"]["latitude"],controller["subcenter"]["longitude"]))[0]):
                to_append = controller
                if "atcPosition" in to_append and to_append["atcPosition"] != None:
                    if "regionMap" in to_append["atcPosition"]: del to_append["atcPosition"]["regionMap"]
                    if "regionMapPolygon" in to_append["atcPosition"]: del to_append["atcPosition"]["regionMapPolygon"]
                atc.append(controller)
        return atc
    
    elif stat == "Pilot_Inbound":
        r = session.get("https://api.ivao.aero/v2/tracker/now/pilots/summary")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        pilot_inbound = []
        for pilot in rjs:
            if "flightPlan" in pilot and pilot["flightPlan"] != None and pilot["flightPlan"]["arrival"] != None \
            and pilot["flightPlan"]["arrival"]["countryId"] == "GB":
                pilot_inbound.append(pilot)
        return pilot_inbound
    
    elif stat == "Pilot_Outbound":
        r = session.get("https://api.ivao.aero/v2/tracker/now/pilots/summary")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        pilot_outbound = []
        for pilot in rjs:
            if "flightPlan" in pilot and pilot["flightPlan"] != None and pilot["flightPlan"]["departure"] != None \
            and pilot["flightPlan"]["departure"]["countryId"] == "GB":
                pilot_outbound.append(pilot)
        return pilot_outbound
    
    elif stat == "Pilot_In_Airspace":
        r = session.get("https://api.ivao.aero/v2/tracker/now/pilots/summary")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        pilot_in_airspace = []
        for pilot in rjs:
            if "lastTrack" in pilot and pilot["lastTrack"] != None and "latitude" in pilot["lastTrack"] \
            and pilot["lastTrack"]["latitude"] != None and pilot["lastTrack"]["longitude"] != None \
            and is_uk((pilot["lastTrack"]["latitude"], pilot["lastTrack"]["longitude"]))[0]:
                pilot_in_airspace.append(pilot)
        return pilot_in_airspace

    elif stat == "Pilot_VFR":
        r = session.get("https://api.ivao.aero/v2/tracker/whazzup")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        pilot_vfr = []
        if "clients" in rjs and "pilots" in rjs["clients"]:
            for pilot in rjs["clients"]["pilots"]:
                if "flightPlan" in pilot and pilot["flightPlan"] != None and pilot["flightPlan"]["level"] == "VFR" \
                and "lastTrack" in pilot and pilot["lastTrack"] != None \
                and is_uk((pilot["lastTrack"]["latitude"], pilot["lastTrack"]["longitude"]))[0]:
                    pilot_vfr.append(pilot)
        return pilot_vfr

    elif stat == "Network_Online":
        r = session.get("https://api.ivao.aero/v2/tracker/connections/total")

        if r.status_code != 200: return [False, "The API returned an invalid response."]
        try: rjs = r.json()
        except: return [False, "The API returned a non-json response."]

        return rjs[-1]
