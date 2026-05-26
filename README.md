# EECE 4830 Network Design Project

## Overview
This repo has my implementation for the network design project. Phase 1 covers a basic UDP echo program and file transfer using RDT 1.0.

## Team
| Name | Email |
|---|---|
| Sinjini Bhattacharjee | sinjini.bx@gmail.com |

## Demo Video
Private YouTube link: (https://youtu.be/8d3UtI3cKqU)

---

## Repo Structure

src/ - all Python source files
docs/ - design document
data/ - input files (e.g. sample.bmp)
results/ - output files from receiver
README.md

---

## Requirements
- Python 3.x
- No external libraries needed

---

## How to Run

### Phase 1a – UDP Echo

Open two terminals.

Terminal 1:
python src/udp_server.py

Terminal 2:
python src/udp_client.py

Expected output on server:
Server is running on port 9000
Received from client: HELLO
Echoed message back to ('127.0.0.1', 9001)

Expected output on client:
Sent to server: HELLO
Echo from server: HELLO

### Phase 1b – RDT 1.0 File Transfer

Open two terminals. Put a BMP file in the data/ folder.

Terminal 1:
python src/receiver.py --port 9000 --out results/received.bmp

Terminal 2:
python src/sender.py --host 127.0.0.1 --port 9000 --file data/sample.bmp

To verify the file transferred correctly run:
md5 data/sample.bmp
md5 results/received.bmp

Both hashes should match.

---

## Known Limitations
- No error handling since Phase 1 uses RDT 1.0 which assumes a perfect channel
