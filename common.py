import os
def cur_dir():
    return os.path.dirname(os.path.abspath(__file__))

def get_abs_path(relative_path):
    d = cur_dir()
    return os.path.abspath(os.path.join(d, relative_path))

def get_secret_key(prompt="输入SSL私钥内容:"):
    import getpass
    lines = []
    print(prompt)
    while True:
        line = getpass.getpass()
        if line and line.strip() != "":
            lines.append(line)
        else:
            break
    return "\n".join(lines)
