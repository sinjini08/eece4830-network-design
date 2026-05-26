# Network Design Project – Phase Proposal & Design Document (Phase 1 of 5)

**Team Name:** Solo  
**Members:** Sinjini Bhattacharjee, sinjini.bx@gmail.com  
**GitHub Repo URL:** https://github.com/sinjini08/eece4830-network-design (username: sinjini08)  
**Phase:** 1  
**Submission Date:** May 2026  
**Version:** v1

---

## 0) Executive Summary

Phase 1 has two parts. In part 1a I implement a basic UDP client and server where the client sends a message like "HELLO" and the server sends it back. In part 1b I implement RDT 1.0 file transfer over UDP. The sender reads a BMP file, breaks it into 1024 byte chunks, and sends one chunk at a time. The receiver writes each chunk to a file and sends an ACK back. Since RDT 1.0 assumes the channel is perfect there is no error handling needed. The transfer is done when the sender sends an end packet with no data. I will verify the transfer worked by comparing the MD5 hash of the original and received files.

---

## 1) Phase Requirements

### 1.1 Demo Deliverable

Screen recording showing the required scenarios.

- **Private YouTube link:** (https://youtu.be/8d3UtI3cKqU)

### 1.2 Required Demo Scenarios

| Scenario | What will be configured | Expected observable behavior | What we will see in the video |
|---|---|---|---|
| 1 | UDP client sends "HELLO" to server, both on same machine different ports | Server prints the message and echoes it back | Two terminals showing both sides |
| 2 | Sender sends a BMP file to receiver over UDP | Receiver saves the file and hashes match | Two terminals showing packets and final hash check |

### 1.3 Required Figures / Plots

N/A

---

## 2) Phase Plan

### 2.1 Scope

- **New behaviors added:** UDP echo (1a), RDT 1.0 file transfer (1b)
- **Out of scope:** checksums, retransmission, pipelining (those are later phases)

### 2.2 Acceptance Criteria

- [ ] Server runs on port 9000, client on port 9001
- [ ] Client sends "HELLO" and gets it back
- [ ] Sender splits file into 1024 byte packets
- [ ] Sender waits for ACK before sending next packet
- [ ] Receiver writes chunks in order to output file
- [ ] MD5 hash of received file matches original
- [ ] README has commands to run both parts

### 2.3 Work Breakdown

Individual work by Sinjini Bhattacharjee.

---

## 3) Architecture + State Diagrams

### 3.1 State Diagrams

**Phase 1a:**

Client sends "HELLO" --> Server receives and prints it --> Server echoes back --> Client prints echo

**Phase 1b:**

Sender reads file --> splits into chunks --> sends packet --> waits for ACK --> sends next packet --> sends END
Receiver waits --> gets packet --> writes to file --> sends ACK --> waits again --> gets END --> closes file

### 3.2 Component Responsibilities

- **udp_server.py** – listens on port 9000, receives message, sends it back
- **udp_client.py** – sends "HELLO" to server, prints the reply
- **sender.py** – reads file, sends packets one at a time, waits for ACK each time
- **receiver.py** – receives packets, writes to file, sends ACKs

### 3.3 Message Flow

Phase 1a:
udp_client (port 9001) --> UDP --> udp_server (port 9000)
                       <-- echo <--

Phase 1b:
[input file] --> sender --> UDP --> receiver --> [output file]
                       <-- ACK <--

---

## 4) Packet Format

### 4.1 Packet Types

- Data packet – has a header and file chunk
- ACK packet – just 4 bytes sent back to the sender
- End packet – header with 0 bytes of payload to signal done

### 4.2 Header Fields

| Field | Size | Type | Description |
|---|---:|---|---|
| seq_num | 4 bytes | unsigned int | which packet this is |
| length | 4 bytes | unsigned int | how many bytes of data |
| payload | up to 1024 bytes | bytes | the file chunk |

Header is 8 bytes total. Encoded with struct.pack("!II", seq_num, length).
ACK is just struct.pack("!I", seq_num).

---

## 5) Data Structures + Module Map

### 5.1 Key Data Structures

- Sender reads the whole file into bytes and slices it into a list of chunks
- Receiver opens the output file and writes each chunk as it arrives

### 5.2 Module Map

src/udp_client.py
src/udp_server.py
src/sender.py
src/receiver.py

No shared module, kept everything separate to keep it simple.

---

## 6) Protocol Logic

### 6.1 Sender Behavior

1. Read the file
2. Split into 1024 byte chunks
3. For each chunk: send packet, wait for ACK
4. Send END packet when done

Pseudocode:
read file
chunks = split into 1024 byte pieces
for each chunk:
    send packet(seq, chunk)
    wait for ACK
send END packet

### 6.2 Receiver Behavior

1. Listen for packets
2. If data: write to file, send ACK
3. If END: close file and stop

Pseudocode:
open output file
loop:
    receive packet
    if length == 0: stop
    write payload to file
    send ACK

### 6.3 Error/Loss Injection

N/A – RDT 1.0 assumes a perfect channel.

---

## 7) Experiments + Metrics Plan

N/A

---

## 8) Edge Cases + Test Plan

### 8.1 Edge Cases

| Edge case | Why it matters | Expected behavior |
|---|---|---|
| Last packet smaller than 1024 bytes | File size is not always a multiple of 1024 | Receiver uses length field to write the right number of bytes |
| END packet | Signals transfer is done | Receiver closes file and exits loop |

### 8.2 Tests

- Send a BMP file and compare MD5 hashes of original and received file
- Check the number of packets printed matches what is expected

---

## 9) Repo Structure

src/
    udp_client.py
    udp_server.py
    sender.py
    receiver.py
docs/
    DESIGN_DOCUMENT.md
data/
    sample.bmp
results/
README.md

---

## 10) Team Plan

### 10.1 Task Ownership

| Task | Owner | Target date | Definition of done |
|---|---|---|---|
| Phase 1a | Sinjini Bhattacharjee | Week 1 | Echo works |
| Phase 1b | Sinjini Bhattacharjee | Week 1 | File hash matches |
| README | Sinjini Bhattacharjee | Week 1 | TA can run it |

### 10.2 Milestones

- Milestone 1: Phase 1a working
- Milestone 2: Phase 1b working, hash verified
- Milestone 3: Repo clean, submitted on Canvas
