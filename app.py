from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    playbooks = ["update-packages.yml", "update-pihole.yml", "update-truenas-charts.yml"]
    return render_template('index.html', playbooks=playbooks)


@app.route('/run-playbook', methods=['POST'])
def run_playbook():
    playbook_name = request.json.get('playbook')

    # Run the Ansible playbook directly
    output = subprocess.check_output(["ansible-playbook", "-i", "/etc/inventory/inventory.ini", playbook_name])

    return jsonify({"output": output.decode("utf-8")})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
