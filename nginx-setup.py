import os
import common as mm
import getpass

def check_permissions(file_path = "/etc/nginx/sites-enabled/"):
    try:
        with open(os.path.join(file_path, 'test_permission'), 'w') as test_file:
            test_file.write("permission test")
        os.remove(os.path.join(file_path, 'test_permission'))
        return True
    except PermissionError:
        print(f"Permission denied for writing to {file_path}. Please run the script with appropriate permissions.")
        return False


def write_nginx_conf(aimdir = "/etc/nginx/sites-enabled/"):
    cert_path = mm.get_abs_path("cert.pem")
    key_path = mm.get_abs_path("privkey.pem")
    app_static_path = mm.get_abs_path("static")

    key_content = mm.get_secret_key()
    if key_content is None or key_content.strip() == "":
        if not os.path.exists(key_path):
            print("私钥文件不存在，无法继续")
            return
        else:
            print(f"私钥文件已存在于 {key_path}，继续使用该文件")
    else:
        with open(key_path, 'w') as key_file:
            key_file.write(key_content)
        os.chmod(key_path, 0o600)
        print(f"私钥已写入到 {key_path}")
    

    templateFile = "template/nginx.conf"
    content = ""
    with open(templateFile, 'r') as template_file:
        content = template_file.read()
        content = content.replace("{NGINX_CERT_PATH}", cert_path)
        content = content.replace("{NGINX_CERT_KEY_PATH}", key_path)
        content = content.replace("{APP_STATIC_PATH}", app_static_path)
    
    with open(os.path.join(aimdir, 'MIVerification-server.conf'), 'w') as conf_file:
        conf_file.write(content)

def restart_nginx():
    os.system("sudo nginx -t")
    os.system("sudo systemctl restart nginx")
    print("Nginx service restarted")

    

if __name__ == "__main__":
    if not check_permissions():
        exit(1)
    write_nginx_conf()
    restart_nginx()
