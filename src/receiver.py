import socket
import struct
import argparse
import random
import os

CHUNK_SIZE = 1024
HEADER_SIZE = 7

def calc_checksum(data):
    return sum(data) % 65536

def make_ack(seq_bit):
    header_no_checksum = struct.pack("!BIH", seq_bit, 0, 0)
    checksum = calc_checksum(header_no_checksum)
    return struct.pack("!BIH", seq_bit, 0, checksum)

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
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--data-error-rate", type=float, default=0.0)
    parser.add_argument("--data-loss-rate", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log-level", type=str, default="info")
    args = parser.parse_args()

    random.seed(args.seed)
    verbose = args.log_level in ("debug", "info")

    folder = os.path.dirname(args.out)
    if folder:
        os.makedirs(folder, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", args.port))
    print("Receiver listening on port", args.port)

    output_file = open(args.out, "wb")
    packets_received = 0
    expected_seq = 0
    last_ack = None

    while True:
        raw, sender_addr = sock.recvfrom(HEADER_SIZE + CHUNK_SIZE)

        seq_bit = get_seq_bit(raw)

        if seq_bit == 2:
            if verbose:
                print("Received END packet. Done.")
            break

        if args.data_loss_rate > 0 and random.random() < args.data_loss_rate:
            if verbose:
                print(f"Dropped DATA packet seq_bit={seq_bit}")
            continue

        if args.data_error_rate > 0 and random.random() < args.data_error_rate:
            raw = corrupt_packet(raw)
            if verbose:
                print(f"Injected error into DATA packet seq_bit={seq_bit}")

        if is_corrupt(raw) or seq_bit != expected_seq:
            if verbose:
                print(f"Bad packet (corrupt or wrong seq), sending last ACK")
            if last_ack is not None:
                sock.sendto(last_ack, sender_addr)
            else:
                resend_bit = 1 - expected_seq
                sock.sendto(make_ack(resend_bit), sender_addr)
        else:
            _, length, _ = struct.unpack("!BIH", raw[:HEADER_SIZE])
            payload = raw[HEADER_SIZE:HEADER_SIZE + length]
            output_file.write(payload)
            packets_received += 1
            if verbose:
                print(f"Received packet seq_bit={seq_bit} ({length} bytes)")

            ack = make_ack(seq_bit)
            last_ack = ack
            sock.sendto(ack, sender_addr)
            if verbose:
                print(f"Sent ACK seq_bit={seq_bit}")

            expected_seq = 1 - expected_seq

    output_file.close()
    sock.close()
    print(f"File saved to {args.out} ({packets_received} packets received)")

main()
