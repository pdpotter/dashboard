from statistics import mode
from flask import Flask, render_template, request, url_for

import json

from itsdangerous import exc

# from SPARQLWrapper import SPARQLWrapper, JSON
# import ssl

app = Flask(__name__)


def read_json(file_name):
    '''
    open and read json file
    '''
    with open(file_name) as config_form:
        data = json.load(config_form)
        return data


def update_json(file_name, json_read):
    '''
    update and dump json file
    '''
    with open(file_name, 'w') as config_update:
        json.dump(json_read, config_update)


def access_data_sources(pilot_name, file_name):
    '''
    this function access a specific pilot data in the config file based on its name
    '''
    for source, details in read_json(file_name)['data_sources'].items():
        if pilot_name == source:
            return details

# access the welcome page


@app.route("/")
def welcome():
    return render_template('index.html')

# access any pilot page


@app.route("/pilot/<string:pilot_name>")
def pilot(pilot_name):
    '''
    opens the config file, checks if pilot_name is inside data_sources and returns its page with the data(details)
    to be displayed.
    '''
    details = access_data_sources(pilot_name, 'config.json')
    if details:
        return render_template('pilot.html', details=details)
    else:
        return render_template('page-404.html')


@app.route("/setup", methods=['POST', 'GET'])
def setup():
    c = read_json('config.json')
    if request.method == 'GET':
        template_data = []
        for item in c['templates']:
            template_data.append(c['templates'][item])
        return render_template('setup.html', template_data=template_data)
    elif request.method == 'POST':
        try:
            # get data
            form_data = request.form
            template_mode = form_data['template_mode']
            pilot_title = form_data['title']
            pilot_endpoint = form_data['sparql_endpoint']
            # create new pilot instance
            new_pilot = {}
            new_pilot['sparql_endpoint'] = pilot_endpoint
            new_pilot['template_mode'] = template_mode
            new_pilot['title'] = pilot_title
            # add to config file
            clean_title = pilot_title.lower().replace(" ", "_")
            c['data_sources'][clean_title] = new_pilot
            update_json('config.json', c)
            details = access_data_sources(clean_title, 'config.json')
            print(details)
            # the correct template opens based on the name
            return render_template(template_mode+'.html', details=details)
        except:
            return 'did not save to database'
    else:
        return 'something went wrong, try again'


# def write_to_database(data):
#     with open('database.json', 'w') as database:
#         json.dump(data, database)

@app.route("/send_data", methods=['POST', 'GET'])
def send_data():
    with open('config.json') as config_form:
        c = json.load(config_form)
    if request.method == 'POST':
        try:
            # get data
            form_data = request.form
            print(form_data)
            pilot_title = form_data['title']
            pilot_subtitle = form_data['subtitle']
            pilot_curator = form_data['curator']
            pilot_description = form_data['description']
            # get existent pilot instance

            for source, details in c['data_sources'].items():
                if details['title'] == pilot_title:
                    details['subtitle'] = pilot_subtitle
                    details['curator'] = pilot_curator
                    details['description'] = pilot_description
                    with open('config.json', 'w') as config_update:
                        json.dump(c, config_update)
            return 'Success!'
        except:
            return 'Something went wrong'
