import csv

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys


def sum(base_val, new_val):
    if base_val is None:
        base_val = 0
    if new_val is None:
        new_val = 0
    return int(base_val) + int(new_val)


def merge_counts(base_val, curr_val):
    if base_val is None:
        base_val = {}
    if curr_val is None:
        curr_val = {}
    keys = {key for key, _ in base_val.items()}
    keys = keys.union({key for key, _ in curr_val.items()})
    return {key: avg(base_val.get(key, None), curr_val.get(key, None)) for key in keys}


def avg(base_val, new_val):
    if (base_val is None or base_val == '') and (new_val is None or new_val == ''):
        return None
    if (base_val is None or base_val == '') and (new_val is not None and new_val != ''):
        return int(float(new_val))
    if new_val is None or new_val == '':
        return base_val
    return round((int(float(base_val)) + int(float(new_val))) / 2)


def same(base_val, new_val):
    return base_val or new_val


def count(base_val, new_val):
    if base_val is None:
        base_val = 0
    return base_val + 1


class DataTable:
    def __init__(self, header, rows):
        self.rows = rows
        self.header = header

    def distinct(self, col_name, sort=False):
        col_index = self.header.index(col_name)
        items = [item for item in set([row[col_index] for row in self.rows])]
        if sort:
            items.sort(reverse=True)
        return items

    def group_by(self, group_key_func, project_func, group_funcs):
        result = {}
        for row in self.rows:
            curr_row = {col: row[index] for index, col in enumerate(self.header)}
            curr_row = project_func(curr_row)
            group_key = group_key_func(curr_row)
            base_row = result.get(group_key, None) or {}
            new_row = {col: func(base_row.get(col, None), curr_row.get(col, None)) for col, func
                       in group_funcs.items()}
            # print(f"  {base_row}\n +{curr_row}\n=>{new_row}\n")
            result[group_key] = new_row
        return result


def project(row):
    if row.get("batchDurationInSeconds", None):
        row["duration"] = {int(row["count"]): int(float(row["batchDurationInSeconds"]))}
    return row


def load_data():
    with open('measurements.csv', 'r') as file:
        csvin = csv.reader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        header = next(csvin)
        rows = [row for row in csvin]
        return DataTable(header, rows)


def generate_graph(grouped_data):
    plt.xscale('log')
    plt.yscale('log')
    colors = iter(["red", "blue", "green", "gray", "orange", "pink", "brown"])
    for variant, data in grouped_data.items():
        durations = data["duration"]
        counts = [key for key, value in durations.items()]
        counts.sort(reverse=True)
        durations = [durations.get(count, None) for count in counts]
        line, = plt.plot(counts, durations, color=next(colors), linestyle='solid', linewidth=1)
        line.set_label(variant)
    plt.ylabel('Duration [sec]')
    plt.xlabel('Records [pcs]')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
    plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
    plt.legend()
    plt.grid(True)
    plt.draw()
    fig = plt.gcf()
    fig.set_size_inches(15, 8, forward=True)
    fig.savefig("doc/report.png", dpi=75)


def report():
    data = load_data()
    grouped_data = data.group_by(group_key_func=lambda row: row["variant"],
                                 project_func=project,
                                 group_funcs={"variant": same,
                                              "duration": merge_counts})
    generate_graph(grouped_data)


if __name__ == "__main__":
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        print("Python 3.8 or higher is required.")
        print("Sorry, your python is {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    report()
