import socket
import struct
import argparse

CHUNK_SIZE = 1024

def make_packet(seq_num, data):
    header = struct.pack("!II", seq_num, len(data))
    return header + data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()

    with open(args.file, "rb") as f:
        file_data = f.read()

    print("File size:", len(file_data), "bytes")

    chunks = []
    i = 0
    while i < len(file_data):
        chunks.append(file_data[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE

    print("Total packets to send:", len(chunks))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver = (args.host, args.port)

    for seq in range(len(chunks)):
        packet = make_packet(seq, chunks[seq])
        sock.sendto(packet, receiver)
        print(f"Sent packet {seq} ({len(chunks[seq])} bytes)")

        ack_data, _ = sock.recvfrom(8)
        ack_seq = struct.unpack("!I", ack_data)[0]
        print(f"Got ACK for packet {ack_seq}")

    end_packet = make_packet(len(chunks), b"")
    sock.sendto(end_packet, receiver)
    print("Sent END packet. Transfer done.")

    sock.close()

main()
