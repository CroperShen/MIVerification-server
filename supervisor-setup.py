import os
import common as mm
def write_supervisor_conf(aimdir = "/etc/supervisor/conf.d/MIVerification-server.conf"):
    app_file_path = mm.get_abs_path("app.py")
    templateFile = "template/MIVerification-server.conf"

    content = ""
    with open(templateFile, 'r') as template_file:
        content = template_file.read()
        content = content.replace("{APP_FILE_PATH}", app_file_path)
    with open(aimdir, 'w') as conf_file:
        conf_file.write(content)
    print(f"Supervisor configuration written to {aimdir}")

def restart_supervisor():
    os.system("supervisorctl reread")
    os.system("supervisorctl update")
    os.system("supervisorctl restart MIVerification-server")
    print("Supervisor service restarted")

if __name__ == "__main__":
    write_supervisor_conf()
    restart_supervisor()
