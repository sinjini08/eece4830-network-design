import csv
import matplotlib.pyplot as plt

# Chart 1: completion time vs error/loss rate
CSV_IN = "results/phase4_times.csv"
PLOT_OUT1 = "results/phase4_chart1.png"

rates1, times1 = [], []
rates2, times2 = [], []
rates3, times3 = [], []
rates4, times4 = [], []
rates5, times5 = [], []

with open(CSV_IN, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        option = int(row["option"])
        rate = int(row["rate"])
        avg = float(row["avg_time"])
        if option == 1:
            rates1.append(rate)
            times1.append(avg)
        elif option == 2:
            rates2.append(rate)
            times2.append(avg)
        elif option == 3:
            rates3.append(rate)
            times3.append(avg)
        elif option == 4:
            rates4.append(rate)
            times4.append(avg)
        else:
            rates5.append(rate)
            times5.append(avg)

plt.figure(figsize=(10, 6))
plt.plot(rates1, times1, marker="o", label="Option 1 - No loss/errors")
plt.plot(rates2, times2, marker="s", label="Option 2 - ACK bit-error")
plt.plot(rates3, times3, marker="^", label="Option 3 - Data bit-error")
plt.plot(rates4, times4, marker="D", label="Option 4 - ACK loss")
plt.plot(rates5, times5, marker="x", label="Option 5 - Data loss")
plt.yscale("log")
plt.xlabel("Error/Loss Rate (%)")
plt.ylabel("Completion Time (seconds, log scale)")
plt.title("GBN Phase 4 Completion Time vs Error/Loss Rate")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(PLOT_OUT1)
print(f"Chart 1 saved to {PLOT_OUT1}")
plt.close()

# Chart 2: completion time vs window size
CSV_WINDOW = "results/phase4_window.csv"
PLOT_OUT2 = "results/phase4_chart2.png"

window_sizes = []
window_times = []

with open(CSV_WINDOW, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        window_sizes.append(int(row["window_size"]))
        window_times.append(float(row["avg_time"]))

plt.figure(figsize=(10, 6))
plt.plot(window_sizes, window_times, marker="o", color="purple")
plt.xlabel("Window Size")
plt.ylabel("Completion Time (seconds)")
plt.title("GBN Completion Time vs Window Size (10% Data Loss)")
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOT_OUT2)
print(f"Chart 2 saved to {PLOT_OUT2}")
plt.close()

# Chart 3: phase comparison
CSV_PHASE = "results/phase_comparison.csv"
PLOT_OUT3 = "results/phase4_chart3.png"

phases = []
phase_times = []

with open(CSV_PHASE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        phases.append(row["phase"])
        phase_times.append(float(row["avg_time"]))

plt.figure(figsize=(10, 6))
plt.bar(phases, phase_times, color=["blue", "orange", "green", "red"])
plt.xlabel("Phase")
plt.ylabel("Completion Time (seconds)")
plt.title("Phase Comparison at 10% Loss/Error Rate")
plt.grid(True, axis="y")
plt.tight_layout()
plt.savefig(PLOT_OUT3)
print(f"Chart 3 saved to {PLOT_OUT3}")
plt.close()
