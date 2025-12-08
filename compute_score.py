import csv
from collections import defaultdict
from statistics import mean
import math  # Needed for Euclidean distance (square root)
from Log_to_csv_mvp import log_to_csv

print("\n" + "=" * 170)
print("                                                                     WI-FI FINGERPRINTING")
print("                                                                         TREASURE MAP")
print("=" * 170)

# =======================
# KNOBS FOR TREASURE HUNT
# =======================

# MINIMUM RELIABILITY: as a fraction
MIN_RELIABILITY_PERCENT = input("Minimum reliability percentage (default 0): ")
if MIN_RELIABILITY_PERCENT == "":
    MIN_RELIABILITY_PERCENT = 0.00
else:
    MIN_RELIABILITY_PERCENT = float(MIN_RELIABILITY_PERCENT) / 100.0

# Missing-signal penalty (dBm)
MISSING_PENALTY_RSS = input("Missing penalty RSS (default: -100): ")
if MISSING_PENALTY_RSS == "":
    MISSING_PENALTY_RSS = -100
else:
    MISSING_PENALTY_RSS = int(MISSING_PENALTY_RSS)

# Scoring algorithm (M or E)
SCORING_ALGORITHM = input("Choose scoring algorithm, (default) M=Manhattan or E=Euclidean: ")
if SCORING_ALGORITHM == "":
    SCORING_ALGORITHM = "M"
else:
    SCORING_ALGORITHM = SCORING_ALGORITHM.strip().upper()

# Refreshing time
REFRESHING_TIME = input("Refreshing time in seconds (default 2): ")
if REFRESHING_TIME == "":
    REFRESHING_TIME = 2
else:
    REFRESHING_TIME = float(REFRESHING_TIME)

# Difference tolerance
TOLL = input("Tolerance (default 3): ")
if TOLL == "":
    TOLL = 3
else:
    TOLL = float(TOLL)

# =========
# LOAD DATA
# =========

target_files = {
    "Location_1" : "location_1.csv",
    "Location_2" : "location_2.csv",
    "Location_3" : "location_3.csv",
    "Location_4" : "location_4.csv",
}

# ====================
# PROCESSING FUNCTIONS
# ====================

def process_csv_fingerprint(filepath):

    mac_rss_values = defaultdict(list)              # values are lists (become rss_list)
    total_rows = 0

    with open(filepath, 'r', newline='') as file:
        reader = csv.reader(file)
        # Handle potential different headers or skip first row
        header = next(reader, None)

        # quick checks
        for row in reader:
            if len(row) < 4: continue # check valid row length
            ssid = row[2].strip()
            if "eduroam" not in ssid.lower():  # check if "eduroam" is listed
                continue
            total_rows += 1
            mac = row[1].strip()                    # collect MAC
            try:
                rss = int(row[3].strip())           # collect RSS
                mac_rss_values[mac].append(rss)     # (key <- mac): (value <- rss_list)
            except ValueError:
                continue

    if total_rows == 0:
        print("   [WARNING] No valid Eduroam data found in file.")
        return None, 0, 0

    # FILTERING
    final_fingerprint = {}
    dropped_macs = 0

    for mac, rss_list in mac_rss_values.items():
        # Frequency Check: How often did this MAC appear?
        observation_count = len(rss_list)
        reliability = observation_count / total_rows    # as proportion

        if reliability >= MIN_RELIABILITY_PERCENT:
            # stable signal -> Add Average RSS to fingerprint
            avg_rss = round(mean(rss_list))
            final_fingerprint[mac] = avg_rss
        else:
            # It's noise
            dropped_macs += 1

    # print(f"   [DONE] Kept {len(final_fingerprint)} stable APs. Dropped {dropped_macs} noisy signals.")
    kept_count = len(final_fingerprint)
    return final_fingerprint, kept_count, total_rows

def score(target_fp, live_fp):
    final_score = 0

    if SCORING_ALGORITHM == "M":    # Manhattan
        for mac, target_rss in target_fp.items():
            if mac in live_fp:
                final_score += abs(target_rss - live_fp[mac])
            else:
                final_score += abs(target_rss - MISSING_PENALTY_RSS)

    elif SCORING_ALGORITHM == 'E':
        sum_sq_diff = 0             # Euclidean
        for mac, target_rss in target_fp.items():
            if mac in live_fp:
                diff = target_rss - live_fp[mac]
                sum_sq_diff += (diff ** 2)
            else:
                diff = target_rss - MISSING_PENALTY_RSS
                sum_sq_diff += (diff ** 2)
        final_score = math.sqrt(sum_sq_diff)

    # Penalize strong alien signals
    for mac, live_rss in live_fp.items():
        if mac not in target_fp and live_rss > -60:
            final_score += 20
    return final_score

def compute_score(live_observation):
    targets = {}
    for location, location_path in target_files.items():
        fp, kept, total = process_csv_fingerprint(location_path)
        if not fp:
            print(f"Warning: no fingerprint for {location}, skipping.")
            continue
        targets[location] = {"fp": fp, "kept": kept, "total": total}

    live_fp, live_kept, live_total = process_csv_fingerprint(live_observation)
    if not live_fp:
        print("Warning: no live fingerprint, skipping this cycle.")

    score_lst = []
    for location, target_info in targets.items():
        target_fp = target_info["fp"]
        live_score = score(target_fp, live_fp)
        score_lst.append((location, live_score))
    return score_lst