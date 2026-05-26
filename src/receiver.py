import socket
import struct
import argparse
import os

HEADER_SIZE = 8

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    folder = os.path.dirname(args.out)
    if folder:
        os.makedirs(folder, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", args.port))
    print("Receiver listening on port", args.port)

    output_file = open(args.out, "wb")
    packets_received = 0

    while True:
        raw, sender_addr = sock.recvfrom(1032)
        seq_num, length = struct.unpack("!II", raw[:HEADER_SIZE])
        payload = raw[HEADER_SIZE:HEADER_SIZE + length]

        if length == 0:
            print("Received END packet. Done.")
            break

        output_file.write(payload)
        packets_received += 1
        print(f"Received packet {seq_num} ({length} bytes)")

        ack = struct.pack("!I", seq_num)
        sock.sendto(ack, sender_addr)
        print(f"Sent ACK {seq_num}")

    output_file.close()
    sock.close()
    print(f"File saved to {args.out} ({packets_received} packets received)")

main()
