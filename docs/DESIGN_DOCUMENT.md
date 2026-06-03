# Network Design Project – Phase Proposal & Design Document (Phase 2 of 5)

**Team Name:** Solo  
**Members:** Sinjini Bhattacharjee, sinjini.bx@gmail.com  
**GitHub Repo URL:** https://github.com/sinjini08/eece4830-network-design (username: sinjini08)  
**Phase:** 2  
**Submission Date:** June 2026  
**Version:** v1

---

## 0) Executive Summary

Phase 2 builds on Phase 1 by upgrading to RDT 2.2. The main new things are a checksum to detect bit errors, alternating sequence numbers (0 and 1) to catch duplicates, and retransmission when a bad ACK comes back. RDT 2.2 is NAK-free so the receiver only ever sends ACKs. I test three scenarios: no errors, ACK errors injected at the sender side, and data errors injected at the receiver side. I also measure how long each transfer takes across different error rates (0% to 95%) and plot the results.

---

## 1) Phase Requirements

### 1.1 Demo Deliverable

Screen recording showing all three scenarios and the plot.

- **Private YouTube link:** (to be filled in at submission)

### 1.2 Required Demo Scenarios

| Scenario | What will be configured | Expected behavior | What we will see |
|---|---|---|---|
| Option 1 | No errors | Clean transfer, hashes match | Terminal showing transfer complete |
| Option 2 | ACK errors at sender (--ack-error-rate 0.3) | Sender detects bad ACKs and retransmits | Terminal showing retransmissions |
| Option 3 | Data errors at receiver (--data-error-rate 0.3) | Receiver detects corrupt data, sender retransmits | Terminal showing retransmissions |

### 1.3 Required Figures / Plots

| Figure | X-axis | Y-axis | Sweep range | Output file |
|---|---|---|---|---|
| Completion time vs error rate | Error rate (%) | Time (seconds) | 0% to 95%, step 5% | results/phase2_plot.png |

---

## 2) Phase Plan

### 2.1 Scope

- **New stuff added:** checksum, alternating seq bits, retransmission, error injection flags, timing, experiment script, plot script
- **Same as Phase 1:** UDP sockets, 1024-byte packets, file reassembly
- **Out of scope:** packet loss and timeouts (Phase 3), pipelining (Phase 5)

### 2.2 Acceptance Criteria

- [ ] Checksum computed over full packet
- [ ] Seq bit alternates 0 and 1 for each new packet
- [ ] Sender retransmits if ACK is corrupt or wrong seq
- [ ] Receiver sends duplicate ACK if data is corrupt or wrong seq
- [ ] All 3 options work and files match after transfer
- [ ] Plot generated with correct axes and 3 lines

### 2.3 Work Breakdown

Solo - all work by Sinjini Bhattacharjee.

---

## 3) Architecture + State Diagrams

### 3.1 RDT 2.2 State Diagrams

Sender:

Wait for call 0 -> send pkt seq=0 -> Wait for ACK 0
  if ACK corrupt or wrong seq: retransmit
  if ACK good seq=0: go to Wait for call 1

Wait for call 1 -> send pkt seq=1 -> Wait for ACK 1
  if ACK corrupt or wrong seq: retransmit
  if ACK good seq=1: go to Wait for call 0

Receiver:

Wait for 0:
  if corrupt or seq!=0: send last ACK
  if good seq=0: write data, send ACK(0), go to Wait for 1

Wait for 1:
  if corrupt or seq!=1: send last ACK
  if good seq=1: write data, send ACK(1), go to Wait for 0

### 3.2 Component Responsibilities

- sender.py - sends RDT 2.2 packets, injects ACK errors, retransmits, measures time
- receiver.py - checks checksum and seq, writes to file, sends ACKs, injects data errors
- scripts/run_experiments.py - runs all 3 options at all error rates, saves CSV
- scripts/plot_results.py - reads CSV and generates plot

### 3.3 Message Flow

[file] -> sender -> UDP -> receiver -> [output file]
       <- ACK (with possible injected errors) <-

---

## 4) Packet Format

### 4.1 Packet Types

- Data packet: header + file chunk
- ACK packet: header with 0-byte payload
- End packet: seq_bit=2, no payload

### 4.2 Header Fields

| Field | Size | Type | Description |
|---|---:|---|---|
| seq_bit | 1 byte | unsigned int | 0 or 1 (alternating), 2 = END |
| length | 4 bytes | unsigned int | payload size in bytes |
| checksum | 2 bytes | unsigned int | sum of all bytes mod 65536 |
| payload | up to 1024 bytes | bytes | file chunk |

Header is 7 bytes. Encoded with struct.pack("!BIH", seq_bit, length, checksum).

---

## 5) Data Structures + Module Map

### 5.1 Key Data Structures

- Sender: list of chunks, current seq_bit (0 or 1)
- Receiver: expected_seq (starts at 0), last_ack (last ACK sent, used for retransmits)

### 5.2 Module Map

src/sender.py
src/receiver.py
scripts/run_experiments.py
scripts/plot_results.py
results/phase2_times.csv
results/phase2_plot.png

---

## 6) Protocol Logic

### 6.1 Sender Behavior

1. Read file, split into chunks
2. seq_bit = 0
3. For each chunk: send packet, wait for ACK
4. Possibly corrupt the ACK if ack-error-rate > 0
5. If ACK corrupt or wrong seq: retransmit
6. If ACK good: flip seq_bit, move to next chunk
7. Send END packet when done

### 6.2 Receiver Behavior

1. expected_seq = 0
2. Receive packet
3. If seq_bit == 2: END, stop
4. Possibly corrupt the packet if data-error-rate > 0
5. If corrupt or wrong seq: send last ACK
6. If good: write payload, send ACK(seq_bit), flip expected_seq

### 6.3 Error Injection

- Option 2: sender corrupts ACK with probability ack-error-rate by flipping a random byte
- Option 3: receiver corrupts data packet with probability data-error-rate by flipping a random byte
- Seed set with --seed for reproducibility

---

## 7) Experiments + Metrics Plan

### 7.1 Measurement

- Start timer just before first packet is sent
- Stop timer after END packet is sent
- 5 runs per rate per option, averaged
- Logging disabled during timing runs

### 7.2 Output

- CSV: results/phase2_times.csv (columns: option, rate, avg_time)
- Plot: results/phase2_plot.png

---

## 8) Edge Cases + Test Plan

### 8.1 Edge Cases

| Edge case | Why it matters | Expected behavior |
|---|---|---|
| ACK corrupt on very first packet | No previous ACK to fall back on | Retransmit seq=0 |
| 95% error rate | Almost all packets need retransmit | Transfer completes but slowly |
| Last packet smaller than 1024 bytes | File not multiple of chunk size | Receiver uses length field |

### 8.2 Tests

- Option 1 md5 hash check
- Option 2 at 50% error rate, verify file still correct
- Option 3 at 50% error rate, verify file still correct

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
    480-360-sample.bmp
scripts/
    run_experiments.py
    plot_results.py
results/
    phase2_times.csv
    phase2_plot.png
contribution.txt
README.md

---

## 10) Team Plan

### 10.1 Task Ownership

| Task | Owner | Done when |
|---|---|---|
| sender.py RDT 2.2 | Sinjini Bhattacharjee | All 3 options work |
| receiver.py RDT 2.2 | Sinjini Bhattacharjee | Checksum and seq correct |
| Experiment + plot scripts | Sinjini Bhattacharjee | Plot generated |
| README + design doc | Sinjini Bhattacharjee | TA can run everything |

### 10.2 Milestones

- Milestone 1: RDT 2.2 working for Option 1
- Milestone 2: Options 2 and 3 working
- Milestone 3: Plots done, submitted on Canvas
