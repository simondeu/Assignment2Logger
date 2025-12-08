import csv
from pathlib import Path

base_dir = Path(__file__).parent
raw_log = base_dir / "Rawdata.unknown"
target_ssid = "eduroam"  # Change to "eduroam"


def log_to_csv(log_path, target_ssid, pos):
    columns_to_keep = ["datetime", "MAC Address", "SSID", "Signal Strength"]
    x,y = pos[0], pos[1]
    filtered_rows = []
    header = None

    with open(log_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        

        for row in reader:
            

            # 1. Process header
            if header is None:
                header = row

                # Name the first column manually
                header[0] = "datetime"

                # Determine which column indexes to keep
                keep_indices = [header.index(c) for c in columns_to_keep if c in header]

                # Add cleaned header to results
                filtered_rows.append([header[i] for i in keep_indices])
                continue

            # 2. Filter by SSID
            print(header)
            ssid_value = row[header.index("SSID")]
            if ssid_value != target_ssid:
                continue

            # 3. Keep only selected columns
            cleaned_row = [row[i] for i in keep_indices]
            filtered_rows.append(cleaned_row)


    # 4. Write output
    output_path = base_dir / f"data/Live_log_{x}_{y}.csv"
    with open(output_path, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerows(filtered_rows)

    return output_path


#print(log_to_csv(raw_log, target_ssid))
