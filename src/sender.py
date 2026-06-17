import socket
import struct
import argparse
import random
import time

CHUNK_SIZE = 1024
HEADER_SIZE = 7
TIMEOUT = 0.5
WINDOW_SIZE = 10

def calc_checksum(data):
    return sum(data) % 65536

def make_packet(seq_num, data):
    seq_byte = seq_num % 254
    header_no_checksum = struct.pack("!BIH", seq_byte, len(data), 0)
    checksum = calc_checksum(header_no_checksum + data)
    header = struct.pack("!BIH", seq_byte, len(data), checksum)
    return header + data

def is_corrupt(packet):
    if len(packet) < HEADER_SIZE:
        return True
    seq_num, length, received_checksum = struct.unpack("!BIH", packet[:HEADER_SIZE])
    payload = packet[HEADER_SIZE:HEADER_SIZE + length]
    test_header = struct.pack("!BIH", seq_num, length, 0)
    expected = calc_checksum(test_header + payload)
    return received_checksum != expected

def get_seq_num(packet):
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
    parser.add_argument("--ack-loss-rate", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-level", type=str, default="info")
    parser.add_argument("--timeout", type=float, default=TIMEOUT)
    parser.add_argument("--window-size", type=int, default=WINDOW_SIZE)
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
        print("Window size:", args.window_size)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    receiver = (args.host, args.port)

    base = 0
    nextseqnum = 0
    packets = []
    for i in range(len(chunks)):
        packets.append(make_packet(i, chunks[i]))

    start_time = time.time()

    while base < len(chunks):
        while nextseqnum < base + args.window_size and nextseqnum < len(chunks):
            sock.sendto(packets[nextseqnum], receiver)
            if verbose:
                print(f"Sent packet {nextseqnum}")
            nextseqnum += 1

        try:
            ack, _ = sock.recvfrom(16)

            if args.ack_loss_rate > 0 and random.random() < args.ack_loss_rate:
                if verbose:
                    print(f"Dropped ACK")
                continue

            if args.ack_error_rate > 0 and random.random() < args.ack_error_rate:
                ack = corrupt_packet(ack)
                if verbose:
                    print(f"Injected error into ACK")

            if is_corrupt(ack):
                if verbose:
                    print(f"Corrupt ACK received, ignoring")
                continue

            ack_num = get_seq_num(ack)
            expected_ack = base % 254

            if ack_num == expected_ack:
                if verbose:
                    print(f"Good ACK {ack_num}, advancing base from {base}")
                base += 1

        except socket.timeout:
            if verbose:
                print(f"Timeout, resending from base={base}")
            nextseqnum = base

    end_pkt = struct.pack("!BIH", 255, 0, 0)
    sock.sendto(end_pkt, receiver)

    completion_time = time.time() - start_time
    print(f"Transfer done in {completion_time:.4f} seconds")

    sock.close()

main()
