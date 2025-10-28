import os
def write_supervisor_conf(aimdir = "/etc/supervisor/conf.d/MIVerification-server.conf"):
    current_file_path = os.path.abspath(__file__)
    app_file_path = os.path.join(os.path.dirname(current_file_path), '..', 'src', 'app.py')
    app_file_path = os.path.abspath(app_file_path)

    supervisor_conf_content = f"""command=python3 {app_file_path}
directory=/root
autostart=true
autorestart=true
stderr_logfile=/var/log/file_server.err.log
stdout_logfile=/var/log/file_server.out.log
user=root
environment=PYTHONUNBUFFERED="1"
"""
    with open(aimdir, 'w') as conf_file:
        conf_file.write(supervisor_conf_content)
    print(f"Supervisor configuration written to {aimdir}")

if __name__ == "__main__":
    write_supervisor_conf()
