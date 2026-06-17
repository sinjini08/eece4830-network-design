# Network Design Project – Phase Proposal & Design Document (Phase 4 of 5)

**Team Name:** Solo  
**Members:** Sinjini Bhattacharjee, sinjini.bx@gmail.com  
**GitHub Repo URL:** https://github.com/sinjini08/eece4830-network-design (username: sinjini08)  
**Phase:** 4  
**Submission Date:** 16 June 2026  
**Version:** v3 (updated from Phase 3)

---

## 0) Executive Summary

Phase 4 builds on Phase 3 by upgrading from RDT 3.0 to Go-Back-N (GBN). The key new thing in this phase is pipelined sending — instead of waiting for each packet to be acknowledged before sending the next one, the sender now maintains a window of N unacknowledged packets in flight at once. This makes transfers significantly faster. The sender uses cumulative ACKs and on timeout retransmits all packets in the window starting from the oldest unacknowledged one. The receiver only accepts in-order packets and discards anything out of order. This phase also adds two new performance charts: one showing how completion time changes with window size, and one comparing all four phases.

---

## 1) Phase Requirements

### 1.1 Demo Deliverable

Screen recording showing all five scenarios and the plots.

- **Private YouTube link:** (https://youtu.be/Q9Q3QGNUzAw)

### 1.2 Required Demo Scenarios

| Scenario | What will be configured | Expected behavior | What we will see |
|---|---|---|---|
| Option 1 | No loss, no errors | Clean transfer, hashes match | Terminal showing transfer complete |
| Option 2 | ACK errors at sender (--ack-error-rate 0.3) | Sender ignores corrupt ACKs, times out, resends window | Terminal showing retransmissions |
| Option 3 | Data errors at receiver (--data-error-rate 0.3) | Receiver discards corrupt packets, sender resends window | Terminal showing retransmissions |
| Option 4 | ACK loss at sender (--ack-loss-rate 0.3) | Sender times out and resends window | Terminal showing timeouts |
| Option 5 | Data loss at receiver (--data-loss-rate 0.3) | Receiver drops packets, sender times out and resends window | Terminal showing timeouts |

### 1.3 Required Figures / Plots

| Figure | X-axis | Y-axis | Output file |
|---|---|---|---|
| Chart 1: completion time vs error/loss rate | Rate (%) | Time (seconds) | results/phase4_chart1.png |
| Chart 2: completion time vs window size | Window size | Time (seconds) | results/phase4_chart2.png |
| Chart 3: phase comparison | Phase | Time (seconds) | results/phase4_chart3.png |

---

## 2) Phase Plan

### 2.1 Scope

- **New stuff added:** GBN pipelining, window size N, sender buffer, cumulative ACKs, Go-Back-N retransmission, 3 performance charts
- **Same as Phase 3:** UDP sockets, 1024-byte packets, checksum, bit-error injection, loss injection, file reassembly
- **Out of scope:** Selective Repeat (Phase 5)

### 2.2 Acceptance Criteria

- [ ] Sender maintains window of N unacknowledged packets
- [ ] Sender retransmits entire window on timeout
- [ ] Receiver discards out-of-order packets
- [ ] All 5 options work and files match after transfer
- [ ] Chart 1 generated with 5 lines
- [ ] Chart 2 generated with window sizes 1,2,5,10,20,50
- [ ] Chart 3 generated comparing Phase 1,2,3,4

### 2.3 Work Breakdown

Solo - all work by Sinjini Bhattacharjee.

---

## 3) Architecture + State Diagrams

### 3.1 GBN Sender Logic

Wait for call:
  while nextseqnum < base + window_size:
    send packet[nextseqnum]
    nextseqnum++
  wait for ACK (with timeout)
  if timeout: nextseqnum = base, resend window
  if corrupt ACK or dropped ACK: continue
  if good ACK(n): base = n + 1

### 3.2 GBN Receiver Logic

Wait:
  receive packet
  if END: stop
  if loss injection: drop, continue
  if corrupt or wrong seq: send last ACK
  if correct seq: write payload, send ACK, expected_seq++

### 3.3 Key Difference from Phase 3

In Phase 3, only one packet was in flight at a time. In Phase 4, up to N packets are in flight. On timeout, all packets from base to nextseqnum are retransmitted. This is the Go-Back-N behavior.

### 3.4 Sequence Numbers

Sequence numbers cycle through 0-253. 255 is reserved for the END packet signal. This gives enough space for the window sizes used in this phase.

### 3.5 Component Responsibilities

- sender.py - GBN sender with window, pipelining, cumulative ACKs, timeout
- receiver.py - GBN receiver, in-order delivery only
- scripts/run_experiments.py - runs all 5 options and window size sweep
- scripts/plot_results.py - generates all 3 charts

---

## 4) Packet Format

Same as Phase 3 - no changes needed.

### 4.1 Packet Types

- Data packet: header + file chunk
- ACK packet: header with 0-byte payload
- End packet: seq_num=255, no payload

### 4.2 Header Fields

| Field | Size | Type | Description |
|---|---:|---|---|
| seq_num | 1 byte | unsigned int | 0-253 (cycling), 255 = END |
| length | 4 bytes | unsigned int | payload size in bytes |
| checksum | 2 bytes | unsigned int | sum of all bytes mod 65536 |
| payload | up to 1024 bytes | bytes | file chunk |

---

## 5) Data Structures + Module Map

### 5.1 Key Data Structures

- Sender: list of all packets (pre-built), base pointer, nextseqnum pointer, window size N, socket timeout 0.5 seconds
- Receiver: expected_seq counter, last_ack (last ACK sent)

### 5.2 Module Map

src/sender.py              - GBN sender
src/receiver.py            - GBN receiver
scripts/run_experiments.py - runs all 5 options + window sweep
scripts/plot_results.py    - generates 3 charts
results/phase4_times.csv
results/phase4_window.csv
results/phase_comparison.csv
results/phase4_chart1.png
results/phase4_chart2.png
results/phase4_chart3.png

---

## 6) Protocol Logic

### 6.1 Sender Behavior

1. Read file, split into 1024-byte chunks
2. Pre-build all packets with cycling sequence numbers (0-253)
3. base = 0, nextseqnum = 0
4. sock.settimeout(0.5)
5. While base < total packets:
   - Send all packets from nextseqnum up to base + window_size
   - Wait for ACK
   - If timeout: reset nextseqnum to base, resend window
   - If ACK dropped (ack-loss-rate): continue
   - If ACK corrupt (ack-error-rate): continue
   - If good ACK: advance base by 1
6. Send END packet

### 6.2 Receiver Behavior

1. expected_seq = 0
2. Receive packet
3. If seq_num == 255: END, stop
4. If data-loss-rate > 0 and random drop: discard (Option 5)
5. If data-error-rate > 0 and random corrupt: corrupt (Option 3)
6. If corrupt or seq != expected: send last ACK
7. If good: write payload, send ACK, increment expected_seq

### 6.3 Error and Loss Injection

| Option | Where | How |
|---|---|---|
| Option 2 | Sender, on received ACK | Flip random byte with probability ack-error-rate |
| Option 3 | Receiver, on received data | Flip random byte with probability data-error-rate |
| Option 4 | Sender, on received ACK | Drop ACK with probability ack-loss-rate |
| Option 5 | Receiver, on received data | Drop packet with probability data-loss-rate |

### 6.4 Timeout Value

Default timeout is 0.5 seconds. At high loss rates the window gets retransmitted repeatedly which makes transfers slow, but GBN is still faster than Phase 3 because multiple packets are sent before each timeout.

---

## 7) Experiments + Metrics Plan

### 7.1 Chart 1 Measurement

- 5 options x 20 rates x 5 runs each
- Logging disabled (--log-level error)
- Window size fixed at 10

### 7.2 Chart 2 Measurement

- Fixed 10% data loss rate (Option 5)
- Window sizes: 1, 2, 5, 10, 20, 50
- 5 runs per window size, averaged

### 7.3 Chart 3 Measurement

- Fixed 10% loss/error rate
- One bar per phase (Phase 1, 2, 3, 4)
- Uses baseline transfer times from each phase

### 7.4 Output Files

- results/phase4_times.csv
- results/phase4_window.csv
- results/phase_comparison.csv

---

## 8) Edge Cases + Test Plan

### 8.1 Edge Cases

| Edge case | Expected behavior |
|---|---|
| Window larger than remaining packets | Sender only sends remaining packets |
| Sequence number wraparound at 254 | Cycles back to 0 correctly |
| Timeout with large window | All packets from base retransmitted |
| 95% loss rate | Transfer completes slowly but correctly |

### 8.2 Tests

- Option 1: md5 hash check
- Option 2 at 30%: file still correct
- Option 3 at 30%: file still correct
- Option 4 at 30%: file still correct
- Option 5 at 30%: file still correct

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
    phase4_times.csv
    phase4_window.csv
    phase_comparison.csv
    phase4_chart1.png
    phase4_chart2.png
    phase4_chart3.png
contribution.txt
README.md

---

## 10) Observations and Conclusions

### 10.1 Optimal Window Size

Based on Chart 2, performance improves as window size increases up to a point, then levels off. A window size of 10-20 appears optimal for this file size and network conditions. Very large windows like 50 do not improve much because the bottleneck becomes timeout and retransmission overhead.

### 10.2 Optimal Timeout Value

A timeout of 0.5 seconds works well on localhost. Too small causes unnecessary retransmissions. Too large causes slow recovery from actual loss.

### 10.3 Phase Comparison

GBN (Phase 4) is significantly faster than RDT 3.0 (Phase 3) due to pipelining. Phase 1 and Phase 2 are fast but do not handle loss. Phase 4 handles both loss and errors while maintaining good throughput.

---

## 11) Team Plan

### 11.1 Task Ownership

| Task | Owner | Done when |
|---|---|---|
| sender.py GBN | Sinjini Bhattacharjee | All 5 options work |
| receiver.py GBN | Sinjini Bhattacharjee | In-order delivery correct |
| Experiment + plot scripts | Sinjini Bhattacharjee | All 3 charts generated |
| README + design doc | Sinjini Bhattacharjee | TA can run everything |

### 11.2 Milestones

- Milestone 1: GBN working for Option 1
- Milestone 2: Options 2, 3, 4, 5 working
- Milestone 3: All 3 charts generated
- Milestone 4: Everything submitted
