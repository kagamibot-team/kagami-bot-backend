import socket


def get_ip():
    ips: list[str] = []
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith("127."):
            ips.append(ip)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    ips.append(s.getsockname()[0])
    s.close()
    return set(ips)
