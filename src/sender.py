import socket
import struct
import argparse
import random
import time

CHUNK_SIZE = 1024
HEADER_SIZE = 7  # 1 (seq_bit) + 4 (length) + 2 (checksum)

def calc_checksum(data):
    return sum(data) % 65536

def make_packet(seq_bit, data):
    header_no_checksum = struct.pack("!BIH", seq_bit, len(data), 0)
    checksum = calc_checksum(header_no_checksum + data)
    header = struct.pack("!BIH", seq_bit, len(data), checksum)
    return header + data

def is_corrupt(packet):
    if len(packet) < HEADER_SIZE:
        return True
    seq_bit, length, received_checksum = struct.unpack("!BIH", packet[:HEADER_SIZE])
    payload = packet[HEADER_SIZE:HEADER_SIZE + length]
    test_header = struct.pack("!BIH", seq_bit, length, 0)
    expected = calc_checksum(test_header + payload)
    return received_checksum != expected

def get_seq_bit(packet):
    return struct.unpack("!B", packet[:1])[0]

def corrupt_packet(packet):
    data = bytearray(packet)
    idx = random.randint(0, len(data) - 1)
    data[idx] ^= 0xFF
    return bytes(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--ack-error-rate", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-level", type=str, default="info")
    args = parser.parse_args()

    random.seed(args.seed)
    verbose = args.log_level in ("debug", "info")

    with open(args.file, "rb") as f:
        file_data = f.read()

    chunks = []
    i = 0
    while i < len(file_data):
        chunks.append(file_data[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE

    if verbose:
        print("File size:", len(file_data), "bytes")
        print("Total packets:", len(chunks))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver = (args.host, args.port)

    start_time = time.time()

    seq_bit = 0
    i = 0
    while i < len(chunks):
        packet = make_packet(seq_bit, chunks[i])
        sock.sendto(packet, receiver)
        if verbose:
            print(f"Sent packet {i} seq_bit={seq_bit}")

        while True:
            ack, _ = sock.recvfrom(16)

            if args.ack_error_rate > 0 and random.random() < args.ack_error_rate:
                ack = corrupt_packet(ack)
                if verbose:
                    print(f"Injected error into ACK for packet {i}")

            if is_corrupt(ack) or get_seq_bit(ack) != seq_bit:
                if verbose:
                    print(f"Bad ACK for packet {i}, retransmitting")
                sock.sendto(packet, receiver)
            else:
                if verbose:
                    print(f"Good ACK for packet {i}")
                break

        seq_bit = 1 - seq_bit
        i += 1

    end_pkt = struct.pack("!BIH", 2, 0, 0)
    sock.sendto(end_pkt, receiver)

    completion_time = time.time() - start_time
    print(f"Transfer done in {completion_time:.4f} seconds")

    sock.close()

main()
