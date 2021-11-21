from flask import Flask, render_template, request, jsonify
import json
import yaml

from ssh_query import SSHQuery

app = Flask(__name__)



config = yaml.safe_load(open('config/config.yaml'))
query = SSHQuery(path_to_key=config['credentials']['path_to_ssh_key'],
                 username=config['credentials']['username'],
                 path_to_server_conf=config['settings']['path_to_server_config'],
                 proc_timeout=config['settings']['process_timeout'])


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pass
    else:
        return render_template('index.html') 


@app.route('/get-gpus')
def get_gpus():
    server_list = query.query_gpus()
    response = jsonify(server_list)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get-processes')
def get_processes():
    processes_list = query.query_processes()
    response = jsonify(processes_list)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/get-users')
def get_users():
    users_list = query.query_users()
    response = jsonify(users_list)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(debug=True, port=config['settings']['port'])
