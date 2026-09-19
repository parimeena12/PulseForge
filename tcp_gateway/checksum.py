def calculate_checksum(data):
    total = sum(data.encode("utf-8"))
    return total%256

