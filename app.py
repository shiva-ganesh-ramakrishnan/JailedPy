from flask import Flask, request, jsonify, Response
import subprocess
import json
import os

app = Flask(__name__)

@app.route("/health", methods=['GET', 'POST'])
def health_check():
    return Response("App is running on port 8080"), 200


@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    
    if not data or 'script' not in data:
        return jsonify({'error': 'Missing "script" in request body'}), 400
    
    script = data['script']

    if 'def main' not in script:
        return jsonify({'error': 'No main() function found'}), 400

    with open('/app/tmp.py', 'w') as tmp:
        script_path = '/app/tmp.py'
        tmp.write(script)
        tmp.write("\nif __name__ == '__main__':\n")
        tmp.write("    import json\n")
        tmp.write("    result = main()\n")
        tmp.write("    print('__RESULT__:' + json.dumps(result))\n")

    os.chmod(script_path, 0o777)

    try:
        completed = subprocess.run(
            [
                "python3", script_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )



    except subprocess.TimeoutExpired:
        os.remove(script_path)
        return jsonify({'error': 'Script execution timed out'}), 500

    stdout = completed.stdout
    stderr = completed.stderr
    os.remove(script_path)
    if completed.returncode != 0:
        print(stdout, flush=True)
        print(stderr, flush=True)
        return jsonify({'error': 'Execution error', 'stderr': stderr}), 500

    result_line = next((line for line in stdout.splitlines() if line.startswith('__RESULT__:')), None)
    if result_line =='__RESULT__:null':
        return jsonify({'error': 'main() must return a JSON serializable object'}), 400

    try:
        result = json.loads(result_line.replace('__RESULT__:', ''))
    except json.JSONDecodeError:
        return jsonify({'error': 'main() return value is not valid JSON'}), 400

    cleaned_stdout = '\n'.join(line for line in stdout.splitlines() if not line.startswith('__RESULT__:'))

    return jsonify({'result': result, 'stdout': cleaned_stdout})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



