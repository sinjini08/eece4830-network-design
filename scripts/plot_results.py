import csv
import matplotlib.pyplot as plt

CSV_IN = "results/phase2_times.csv"
PLOT_OUT = "results/phase2_plot.png"

rates1, times1 = [], []
rates2, times2 = [], []
rates3, times3 = [], []

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
        else:
            rates3.append(rate)
            times3.append(avg)

plt.figure(figsize=(10, 6))
plt.plot(rates1, times1, marker="o", label="Option 1 - No errors")
plt.plot(rates2, times2, marker="s", label="Option 2 - ACK bit-error")
plt.plot(rates3, times3, marker="^", label="Option 3 - Data bit-error")

plt.xlabel("Error Rate (%)")
plt.ylabel("Completion Time (seconds)")
plt.title("RDT 2.2 Completion Time vs Error Rate")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOT_OUT)
print(f"Plot saved to {PLOT_OUT}")
plt.show()
