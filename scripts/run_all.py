import subprocess
import time
import os

def run_script(script_path):
    process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    stderr = process.communicate()[1]
    if process.returncode != 0:
        print(f"Error running {script_path}: {stderr}")
        return False
    return True

def run_node_script(script_path):
    process = subprocess.Popen(['node', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    stderr = process.communicate()[1]
    if process.returncode != 0:
        print(f"Error running {script_path}: {stderr}")
        return False
    return True

def start_lm_studio_server():
    print("Starting LM Studio server...")
    server_process = subprocess.Popen(['lms', 'server', 'start'])
    time.sleep(30)  # Wait for the server to start properly
    return server_process

def stop_lm_studio_server(server_process):
    print("Stopping LM Studio server...")
    server_process.terminate()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    steps = [
        (os.path.join(base_dir, "generators/useCaseGenerator.py"), run_script),
        (os.path.join(base_dir, "generators/promptGenerator.py"), run_script),
        ("Start LM Studio Server", start_lm_studio_server),
        (os.path.join(base_dir, "generators/userStoryGenerator.js"), run_node_script),
        ("Stop LM Studio Server", stop_lm_studio_server),
        (os.path.join(base_dir, "generators/gPTRefrenceUserStoryGenerator.py"), run_script),
        (os.path.join(base_dir, "evaluators/gPTEvaluateUserStories.py"), run_script),
        (os.path.join(base_dir, "analytics/leaderboardGenerator.py"), run_script)
    ]

    server_process = None

    for step, function in steps:
        if step == "Start LM Studio Server":
            server_process = function()
            if not server_process:
                print("Failed to start LM Studio server.")
                break
        elif step == "Stop LM Studio Server":
            if server_process:
                function(server_process)
        else:
            if not function(step):
                print(f"Failed at step: {step}")
                break

    print("Process complete.")

if __name__ == "__main__":
    main()
