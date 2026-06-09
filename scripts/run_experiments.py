import subprocess
import time
import csv
import os
import sys

rates = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
NUM_RUNS = 5
FILE = "data/480-360-sample.bmp"
PORT = 9000
OUT_FILE = "results/received_temp.bmp"
CSV_OUT = "results/phase3_times.csv"

def run_once(option, error_rate, seed):
    rate = error_rate / 100.0

    ack_err = 0.0
    data_err = 0.0
    ack_loss = 0.0
    data_loss = 0.0

    if option == 1:
        pass
    elif option == 2:
        ack_err = rate
    elif option == 3:
        data_err = rate
    elif option == 4:
        ack_loss = rate
    elif option == 5:
        data_loss = rate

    receiver_cmd = [
        sys.executable, "src/receiver.py",
        "--port", str(PORT),
        "--out", OUT_FILE,
        "--data-error-rate", str(data_err),
        "--data-loss-rate", str(data_loss),
        "--seed", str(seed),
        "--log-level", "error"
    ]
    sender_cmd = [
        sys.executable, "src/sender.py",
        "--host", "127.0.0.1",
        "--port", str(PORT),
        "--file", FILE,
        "--ack-error-rate", str(ack_err),
        "--ack-loss-rate", str(ack_loss),
        "--seed", str(seed),
        "--log-level", "error"
    ]

    receiver_proc = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.3)

    start = time.time()
    sender_proc = subprocess.Popen(sender_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sender_out, _ = sender_proc.communicate()
    elapsed = time.time() - start

    receiver_proc.wait(timeout=120)

    for line in sender_out.decode().splitlines():
        if "Transfer done in" in line:
            try:
                elapsed = float(line.split("Transfer done in")[1].split("seconds")[0].strip())
            except:
                pass

    return elapsed

os.makedirs("results", exist_ok=True)

rows = []

for option in [1, 2, 3, 4, 5]:
    print(f"\nRunning Option {option}...")
    for rate in rates:
        run_times = []
        for run in range(NUM_RUNS):
            print(f"  Option {option}, rate={rate}%, run {run+1}/{NUM_RUNS}")
            try:
                t = run_once(option, rate, seed=run)
                run_times.append(t)
            except Exception as e:
                print(f"  Error: {e}")
                run_times.append(0)
        avg = sum(run_times) / len(run_times)
        rows.append({"option": option, "rate": rate, "avg_time": avg})
        print(f"  avg time = {avg:.4f}s")

with open(CSV_OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["option", "rate", "avg_time"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nResults saved to {CSV_OUT}")
