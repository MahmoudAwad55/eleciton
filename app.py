from flask import Flask, render_template, request
from prettytable import PrettyTable
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get ID number from the submitted form
        id_number = request.form.get('idNumber')
        data = get_data(id_number)
        table_html = display_table_html(data)
        return render_template('index.html', table_html=table_html)

    # Default ID number for initial page load
    nid = 0
    data = get_data(nid)
    table_html = display_table_html(data)
    return render_template('index.html', table_html=table_html)

def get_data(nid):
    url = "https://proxy.elections.eg/election?nid={}&location=1&external_referrer=https://www.elections.eg/&jsonp=jQuery370017300461000761902_1702146359150&_=1702146359151".format(nid)

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Extract the JSON data from the response content
        json_data = response.content.decode("utf-8").split("(", 1)[1].rsplit(")", 1)[0]

        if json_data:  # Check if the extracted JSON data is not empty
            data = json.loads(json_data)
            return data
        else:
            print("Extracted JSON data is empty")
            return None

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Request Exception:", err)

    return None

def find_description(data):
    if isinstance(data, dict):
        if 'description' in data:
            return data['description']
        for value in data.values():
            description = find_description(value)
            if description:
                return description
    elif isinstance(data, list):
        for item in data:
            description = find_description(item)
            if description:
                return description
    return None

def display_table_html(data):
    if data and 'voting_info' in data:
        table = PrettyTable()
        table.field_names = ["الحاله الانتخابيه", "اسم المدرسه", "رقم اللجنه", "رقم الكشف", "العنوان", "قسم", "المحافظه"]

        voting_info = data['voting_info']
        locations = voting_info.get('locations', [])

        # Fetch values from voting_info if available
        box_number = voting_info.get("box_number", "")
        citizen_number = voting_info.get("citizen_number", "")

        rejection_reason = data.get('rejection_reason', {})
        rejection_description = rejection_reason.get('description', '')

        for location in locations:
            name = location.get("name", "")
            unparsed_address = location.get("unparsed_address", "")
            police_district = location.get("police_district", "")
            governorate = location.get("governorate", "")

            # Fetch description from the 'rejection_description' field
            description = rejection_description or name

            table.add_row([description, name, box_number, citizen_number, unparsed_address, police_district, governorate])

        # Set the encoding to utf-8 before printing
        table_str = table.get_html_string()
        return table_str
    else:
        return "No data to display."

if __name__ == '__main__':
    app.run(debug=True)
