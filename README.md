# EECE 4830 Network Design Project

## Overview
This repo has my implementation for the network design project. Phase 1 covers a basic UDP echo program and file transfer using RDT 1.0. Phase 2 upgrades to RDT 2.2 with checksums, sequence numbers, and retransmission over an unreliable channel with bit errors. Phase 3 upgrades to RDT 3.0 by adding a countdown timer to handle packet loss (both data loss and ACK loss).

## Team
| Name | Email |
|---|---|
| Sinjini Bhattacharjee | sinjini.bx@gmail.com |

## Demo Video
- Phase 1: https://youtu.be/8d3UtI3cKqU
- Phase 2: https://youtu.be/JzjmPTGw_FM
- Phase 3: (to be submitted via Canvas)

---

## Repo Structure

src/               - all Python source files
scripts/           - experiment runner and plot script
docs/              - design documents
data/              - input files
results/           - output files, CSV data, plots
README.md
contribution.txt

---

## Requirements
- Python 3.x
- matplotlib for plots: pip install matplotlib
- No other external libraries needed

---

## Phase 1 - How to Run

### Phase 1a - UDP Echo

Terminal 1:
python src/udp_server.py

Terminal 2:
python src/udp_client.py

### Phase 1b - RDT 1.0 File Transfer

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp

---

## Phase 2 - How to Run

### Option 1: No errors

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp --data-error-rate 0

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp --ack-error-rate 0

### Option 2: ACK bit-errors

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp --data-error-rate 0

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp --ack-error-rate 0.3

### Option 3: Data bit-errors

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp --data-error-rate 0.3

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp --ack-error-rate 0

---

## Phase 3 - How to Run

### Option 1: No loss and no bit-errors

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp

### Option 2: ACK bit-errors (30% error rate)

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp --ack-error-rate 0.3

### Option 3: Data bit-errors (30% error rate)

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp --data-error-rate 0.3

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp

### Option 4: ACK packet loss (30% loss rate)

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp --ack-loss-rate 0.3

### Option 5: Data packet loss (30% loss rate)

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp --data-loss-rate 0.3

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/480-360-sample.bmp

### Verify file integrity
md5 data/480-360-sample.bmp
md5 results/received.bmp

---

## Reproducing the Performance Plots

Step 1 - Run experiments:
python scripts/run_experiments.py

This generates results/phase3_times.csv

Step 2 - Generate plot:
python scripts/plot_results.py

This generates results/phase3_plot.png

---

## Known Limitations
- RDT 3.0 handles bit errors and packet loss, but is non-pipelined (one packet at a time), which is slow at high loss rates
- High loss or error rates will cause many retransmissions and timeouts
- Pipelining is added in Phase 5
