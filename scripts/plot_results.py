import csv
import matplotlib.pyplot as plt

CSV_IN = "results/phase3_times.csv"
PLOT_OUT = "results/phase3_plot.png"

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
plt.title("RDT 3.0 Completion Time vs Error/Loss Rate")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(PLOT_OUT)
print(f"Plot saved to {PLOT_OUT}")
plt.show()
