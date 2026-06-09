# Network Design Project – Phase Proposal & Design Document (Phase 3 of 5)

**Team Name:** Solo  
**Members:** Sinjini Bhattacharjee, sinjini.bx@gmail.com  
**GitHub Repo URL:** https://github.com/sinjini08/eece4830-network-design (username: sinjini08)  
**Phase:** 3  
**Submission Date:** June 2026  
**Version:** v2 (updated from Phase 2)

---

## 0) Executive Summary

Phase 3 builds on Phase 2 by upgrading from RDT 2.2 to RDT 3.0. The key new thing in this phase is a countdown timer on the sender side. In Phase 2 we could handle bit errors but if a packet was just lost entirely, the sender would wait forever. Now when the sender sends a packet and the timer runs out before a valid ACK arrives, it retransmits automatically. I also added two new scenarios: Option 4 (ACK loss injected at the sender) and Option 5 (Data loss injected at the receiver). The receiver itself doesn't change much from Phase 2 — the RDT 3.0 receiver is the same as the RDT 2.2 receiver, except now there's an extra flag for data loss injection. The performance plot now has 5 lines instead of 3.

---

## 1) Phase Requirements

### 1.1 Demo Deliverable

Screen recording showing all five scenarios and the plot.

- **Private YouTube link:** (to be filled in at submission)

### 1.2 Required Demo Scenarios

| Scenario | What will be configured | Expected behavior | What we will see |
|---|---|---|---|
| Option 1 | No loss, no errors | Clean transfer, hashes match | Terminal showing transfer complete |
| Option 2 | ACK errors at sender (--ack-error-rate 0.3) | Sender detects bad ACKs and retransmits | Terminal showing retransmissions |
| Option 3 | Data errors at receiver (--data-error-rate 0.3) | Receiver detects corrupt data, sender retransmits | Terminal showing retransmissions |
| Option 4 | ACK loss at sender (--ack-loss-rate 0.3) | Sender times out and retransmits | Terminal showing timeouts |
| Option 5 | Data loss at receiver (--data-loss-rate 0.3) | Receiver silently drops, sender times out and retransmits | Terminal showing timeouts |

### 1.3 Required Figures / Plots

| Figure | X-axis | Y-axis | Sweep range | Output file |
|---|---|---|---|---|
| Completion time vs error/loss rate | Rate (%) | Time (seconds) | 0% to 95%, step 5% | results/phase3_plot.png |

---

## 2) Phase Plan

### 2.1 Scope

- **New stuff added:** countdown timer on sender, socket timeout, ACK loss injection (Option 4), data loss injection (Option 5), updated experiment and plot scripts for 5 options
- **Same as Phase 2:** UDP sockets, 1024-byte packets, checksum, alternating seq bits, bit-error injection, file reassembly
- **Out of scope:** pipelining (Phase 5)

### 2.2 Acceptance Criteria

- [ ] Sender has a countdown timer using socket.settimeout()
- [ ] Sender retransmits when timer expires
- [ ] Option 4 drops ACKs at the sender with --ack-loss-rate
- [ ] Option 5 drops data packets at the receiver with --data-loss-rate
- [ ] All 5 options work and files match after transfer
- [ ] Plot generated with 5 lines and correct axes

### 2.3 Work Breakdown

Solo - all work by Sinjini Bhattacharjee.

---

## 3) Architecture + State Diagrams

### 3.1 RDT 3.0 Sender State Diagram

The RDT 3.0 sender adds a timer compared to RDT 2.2:

Wait for call 0:
  -> send pkt seq=0, start timer
  -> Wait for ACK 0

Wait for ACK 0:
  if timeout: retransmit, restart timer
  if ACK corrupt or wrong seq: retransmit, restart timer
  if good ACK 0: stop timer, go to Wait for call 1

Wait for call 1:
  -> send pkt seq=1, start timer
  -> Wait for ACK 1

Wait for ACK 1:
  if timeout: retransmit, restart timer
  if ACK corrupt or wrong seq: retransmit, restart timer
  if good ACK 1: stop timer, go to Wait for call 0

### 3.2 RDT 3.0 Receiver State Diagram

The receiver is the same as RDT 2.2 (per the spec):

Wait for 0:
  if corrupt or seq!=0: send last ACK
  if good seq=0: write data, send ACK(0), go to Wait for 1

Wait for 1:
  if corrupt or seq!=1: send last ACK
  if good seq=1: write data, send ACK(1), go to Wait for 0

For loss injection (Option 5): when a data packet is dropped at the receiver, no ACK is sent. The sender timer eventually expires and it retransmits.

### 3.3 How the Timer Works

I use Python's socket.settimeout() to set a timeout on the sender socket. When recvfrom() raises socket.timeout, the sender catches it and retransmits the same packet, then calls recvfrom() again with the same timeout. This continues until a valid ACK is received.

### 3.4 Component Responsibilities

- sender.py - sends RDT 3.0 packets, handles ACK errors and ACK loss, uses countdown timer, retransmits on timeout
- receiver.py - same as Phase 2 receiver plus data loss injection flag
- scripts/run_experiments.py - runs all 5 options at all rates, saves CSV
- scripts/plot_results.py - reads CSV and generates 5-line plot

### 3.5 Message Flow

[file] -> sender -> UDP -> receiver -> [output file]
       <- ACK (with possible injected errors or loss) <-

For Option 4: ACK is received at sender but then dropped before processing (simulates ACK loss).
For Option 5: Data packet is received at receiver but then dropped before processing (simulates data loss).

---

## 4) Packet Format

Same as Phase 2 - no changes needed.

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

- Sender: list of chunks, current seq_bit (0 or 1), socket timeout set to 0.5 seconds
- Receiver: expected_seq (starts at 0), last_ack (last ACK sent, used for retransmits)

### 5.2 Module Map

src/sender.py              - RDT 3.0 sender with timeout
src/receiver.py            - RDT 3.0 receiver (same as 2.2 + loss flag)
scripts/run_experiments.py - runs all 5 options
scripts/plot_results.py    - generates 5-line plot
results/phase3_times.csv
results/phase3_plot.png

---

## 6) Protocol Logic

### 6.1 Sender Behavior (Updated for Phase 3)

1. Read file, split into chunks
2. seq_bit = 0
3. sock.settimeout(0.5)
4. For each chunk: send packet, wait for ACK
5. If socket.timeout fires: retransmit
6. If ack-loss-rate > 0 and random drop: raise timeout manually (Option 4)
7. If ack-error-rate > 0 and random corrupt: corrupt ACK (Option 2)
8. If ACK corrupt or wrong seq: retransmit
9. If ACK good: flip seq_bit, move to next chunk
10. Send END packet when done

### 6.2 Receiver Behavior (Updated for Phase 3)

1. expected_seq = 0
2. Receive packet
3. If seq_bit == 2: END, stop
4. If data-loss-rate > 0 and random drop: silently discard, continue (Option 5)
5. If data-error-rate > 0 and random corrupt: corrupt packet (Option 3)
6. If corrupt or wrong seq: send last ACK
7. If good: write payload, send ACK(seq_bit), flip expected_seq

### 6.3 Error and Loss Injection

| Option | Where injected | How |
|---|---|---|
| Option 2 | Sender, on received ACK | Flip a random byte with probability ack-error-rate |
| Option 3 | Receiver, on received data | Flip a random byte with probability data-error-rate |
| Option 4 | Sender, on received ACK | Drop ACK entirely with probability ack-loss-rate |
| Option 5 | Receiver, on received data | Drop packet entirely with probability data-loss-rate |

Seed set with --seed for reproducibility.

### 6.4 Timeout Value

Default timeout is 0.5 seconds. At high loss rates many timeouts will fire which makes transfers slow - this is expected behavior for a non-pipelined protocol.

---

## 7) Experiments + Metrics Plan

### 7.1 Measurement

- Start timer just before first packet is sent
- Stop timer after END packet is sent
- 3 runs per rate per option, averaged
- Logging disabled during timing runs (--log-level error)
- Receiver timeout set to 120 seconds for high loss rate runs

### 7.2 Output

- CSV: results/phase3_times.csv (columns: option, rate, avg_time)
- Plot: results/phase3_plot.png with 5 lines

---

## 8) Edge Cases + Test Plan

### 8.1 Edge Cases

| Edge case | Why it matters | Expected behavior |
|---|---|---|
| ACK corrupt on very first packet | No previous ACK to fall back on | Retransmit seq=0 |
| 95% loss rate | Almost every packet needs timeout + retransmit | Transfer completes but very slowly |
| Data loss on last packet | File might be missing last chunk | Sender retransmits on timeout |
| ACK loss on first packet | Sender never sees ACK | Timer fires, retransmit |

### 8.2 Tests

- Option 1: md5 hash check to confirm byte-for-byte match
- Option 2 at 30% error rate: verify file still correct after transfer
- Option 3 at 30% error rate: verify file still correct after transfer
- Option 4 at 30% loss rate: verify file still correct after transfer
- Option 5 at 30% loss rate: verify file still correct after transfer

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
    phase3_times.csv
    phase3_plot.png
contribution.txt
README.md

---

## 10) Team Plan

### 10.1 Task Ownership

| Task | Owner | Done when |
|---|---|---|
| sender.py RDT 3.0 (timer + loss) | Sinjini Bhattacharjee | Options 4 and 5 work |
| receiver.py (loss injection) | Sinjini Bhattacharjee | Option 5 works |
| Experiment + plot scripts | Sinjini Bhattacharjee | Plot generated with 5 lines |
| README + design doc | Sinjini Bhattacharjee | TA can run everything |

### 10.2 Milestones

- Milestone 1: RDT 3.0 working for Option 1 (timer added but no errors/loss)
- Milestone 2: Options 2 and 3 working (bit errors, same as Phase 2)
- Milestone 3: Options 4 and 5 working (packet loss + timer)
- Milestone 4: Plots generated, everything submitted
