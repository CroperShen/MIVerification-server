import os
def write_supervisor_conf(aimdir = "/etc/supervisor/conf.d/MIVerification-server.conf"):
    current_file_path = os.path.abspath(__file__)
    app_file_path = os.path.join(os.path.dirname(current_file_path), 'app.py')
    app_file_path = os.path.abspath(app_file_path)

    templateFile = "template/MIVerification-server.conf"

    content = ""
    with open(templateFile, 'r') as template_file:
        content = template_file.read()
        content = content.replace("{APP_FILE_PATH}", app_file_path)
    with open(aimdir, 'w') as conf_file:
        conf_file.write(content)
    print(f"Supervisor configuration written to {aimdir}")

if __name__ == "__main__":
    write_supervisor_conf()
