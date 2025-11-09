from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>🌾 AgroSmart App Live!</h1><p>Welcome to your deployed Flask app.</p>"
# Language dictionary
lang = {
    "en": {
        "home_title": "🌾 AgroSmart App Live!",
        "home_welcome": "Welcome to your deployed Flask app.",
        "farmer_form": "Farmer Data Form",
        "name": "Name",
        "state": "State",
        "lga": "LGA",
        "crop": "Crop",
        "submit": "Submit",
        "back_home": "Back Home",
        "dashboard": "Dashboard",
        "farmers_per_state": "Farmers per State",
        "add_farmer": "Add More Farmers"
    },
    "ha": {
        "home_title": "🌾 AgroSmart App Na Rayuwa!",
        "home_welcome": "Barka da zuwa AgroSmart App naka.",
        "farmer_form": "Fom ɗin Bayanai Na Manomi",
        "name": "Suna",
        "state": "Jihar",
        "lga": "Karamar Hukuma",
        "crop": "Amfanin gona",
        "submit": "Tura",
        "back_home": "Komawa Gida",
        "dashboard": "Dashboard",
        "farmers_per_state": "Manoma a kowace Jihar",
        "add_farmer": "Ƙara Manomi"
    },
    "yo": {
        "home_title": "🌾 AgroSmart App Live!",
        "home_welcome": "Kaabo si AgroSmart App rẹ.",
        "farmer_form": "Fọọmu Alaye Agbe",
        "name": "Orukọ",
        "state": "Ipinle",
        "lga": "Agbegbe",
        "crop": "Ọgbin",
        "submit": "Firanṣẹ",
        "back_home": "Pada si Ile",
        "dashboard": "Dashboard",
        "farmers_per_state": "Agbe ni Ipinle kọọkan",
        "add_farmer": "Fi Agbe kun"
    },
    "ig": {
        "home_title": "🌾 AgroSmart App Dị Ndụ!",
        "home_welcome": "Nnọọ na AgroSmart App gị.",
        "farmer_form": "Fọm Ozi Onye Ọlụ Ọrụ Ugbo",
        "name": "Aha",
        "state": "Steeti",
        "lga": "LGA",
        "crop": "Nri Ugbo",
        "submit": "Zipu",
        "back_home": "Laghachi Home",
        "dashboard": "Dashboard",
        "farmers_per_state": "Ụfọdụ Ndị Ọrụ Ugbo na Steeti",
        "add_farmer": "Tinye Onye Ọrụ Ugbo ọzọ"
    }
}
