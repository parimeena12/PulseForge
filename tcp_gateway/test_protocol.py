from protocol import build_packet, parse_packet
packet = build_packet("device-001",123,25.5,60.0,12.0,"ABC")

packet = packet.strip()

fields = parse_packet(packet)


print(fields)
print(len(fields))

print("\n Testing invalid protocol:")

bad_packet = "PF01|device-001|123|abc|60.0|12.0|ABC|999"

try:
    parse_packet(bad_packet)
    print("Packet completed")
except ValueError as error:
    print("Packet rejected:",error)
print("\n Testing empty device ID:")

bad_packet = "PF01|device-001|123|35.0|60.0|12.0|AB|999"

try:
    parse_packet(bad_packet)
    print("Packet complted")
except ValueError as error:
    print("Packet checksum:",error)

