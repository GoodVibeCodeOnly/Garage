"""Parse messy ledger lines and print an aligned treasury report."""

raw_lines = [
    "prussia, 1200 ,340",
    "  AUSTRIA,1530,  910",
    "bavaria,410,455",
    "saxony ,  680,212  ",
]

rows = []
for line in raw_lines:                       # loops are lesson 05; read this as "for each line"
    name, income, expenses = line.split(",")
    rows.append((name.strip().title(), int(income), int(expenses)))

print("Parsed:", rows[0], "\n")

NAME_W, NUM_W = 10, 10
header = f"{'Country':<{NAME_W}}{'Income':>{NUM_W}}{'Expenses':>{NUM_W}}{'Net':>{NUM_W}}{'Margin':>9}"
print(header)
print("-" * len(header))

total_in = total_out = 0
for name, income, expenses in rows:
    net = income - expenses
    margin = net / income
    print(f"{name:<{NAME_W}}{income:>{NUM_W},}{expenses:>{NUM_W},}{net:>+{NUM_W},}{margin:>9.1%}")
    total_in += income
    total_out += expenses

print("-" * len(header))
total_net = total_in - total_out
print(f"{'TOTAL':<{NAME_W}}{total_in:>{NUM_W},}{total_out:>{NUM_W},}{total_net:>+{NUM_W},}{total_net / total_in:>9.1%}")

print(f"\nCSV export: {','.join(str(x) for x in rows[0])}")
print(f"Debug view: {total_net=}")
