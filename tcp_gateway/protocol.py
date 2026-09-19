from checksum import calculate_checksum

def build_packet(device_id, timestamp, temperature, humidity, voltage, payload):
    data =(
         f"PF01|{device_id}|{timestamp}|"
         f"{temperature}|{humidity}|{voltage}|{payload}"
    )
    checksum = calculate_checksum(data)
    return f"{data}|{checksum}\n"

def parse_packet(packet):
    fields = packet.split("|")

    if  len(fields) != 8:
         raise ValueError("Invalid number of fields")

    if  fields[0] != "PF01":
         raise ValueError("Invalid protocol version")

    if not fields[1]:
        raise ValueError("Device ID cannot be empty")
    try:
       timestamp = int(fields[2])
    except ValueError:
       raise ValueError("Invalid timestamp")

    try:
        temperature = float(fields[3])
        humidity = float(fields[4])
        voltage = float(fields[5])
    except:
        raise ValueError("Invalid telemetry value")

    try:
        received_checksum = int(fields[7])
    except ValueError:
        raise ValueError("Invalid checksum")
    data ="|".join(fields[:7])
    calculated_checksum = calculate_checksum(data)
    if received_checksum != calculated_checksum:
       raise ValueError("Invalid checksum")

    return {
     "device_id":fields[1],
     "timestamp":timestamp,
     "temperature": temperature,
     "humidity": humidity,
     "voltage": voltage,
     "payload": fields[6],
     "checksum": received_checksum
}
