import time
import csv
from collections import defaultdict
from statistics import mean
import math  # Needed for Euclidean distance (square root)

from BKMap import BKMap

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

# ====================
# PROCESSING FUNCTIONS
# ====================

"""Reads (datetime,MAC Address,SSID,Signal Strength) CSV, 
filters out unstable signals, and calculates mean RSSI (mac : avg_rss)"""
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

# =========
# LOAD DATA
# =========

def log_to_csv(log):                                # <---------- HENRYK'S CODE (log_to_csv function)
    return log

target_files = {
    "Location_1" : "location_1.csv",
    "Location_2" : "location_2.csv",
    "Location_3" : "location_3.csv",
    "Location_4" : "location_4.csv",
}

    # live log refreshes continuously
live_log = "location_2.csv"                         # <---------- SIMON'S CODE
    # transform to readable csv file
LIVE_OBSERVATION = log_to_csv(live_log)

# ==================
# SCORING ALGORITHMS                                # <---------- DAMAN's CODE
# ==================

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


def hotter_or_colder(current_scores, previous_scores):
    current_time = time.ctime()
    if previous_scores:
        # previous_scores is [(loc, score, frac), ...]
        prev_dict = {loc: score for loc, score, _ in previous_scores}
    else:
        prev_dict = {}

    display = []

    for loc, score, frac in current_scores:
        if loc in prev_dict:
            prev_score = prev_dict[loc]
            diff = score - prev_score
            if diff < -TOLL:
                status = "HOTTER"
            elif diff > TOLL:
                status = "COLDER"
            else:
                status = "SAME"
        else: status = "BEGIN"

        display.append((score, status, frac))

    while len(display) < 4:
        display.append((0, "N/A", "0/0"))

    score1, status1, frac1 = display[0]
    score2, status2, frac2 = display[1]
    score3, status3, frac3 = display[2]
    score4, status4, frac4 = display[3]


    # Print row
    print(
        f"{current_time:<24} | {int(score1):<10} | {status1:<8} | {frac1:<8} || "
        f"{int(score2):<10} | {status2:<8} | {frac2:<8} || "
        f"{int(score3):<10} | {status3:<8} | {frac3:<8} || "
        f"{int(score4):<10} | {status4:<8} | {frac4:<8}"
    )


# ========
# PLOTTING
# ========

def fingerprint_plot(fingerprint1, fingerprint2):  # <---------- ARDA'S CODE
    pass


# ============================================================================================
#                                       TREASURE MAP INTERFACE
# ============================================================================================

def main():

    Map = BKMap(filename='LoggingFile.txt', scoreFunc=score)

    # 0. Loading targets DICT <- location (str) : fingerprint (MAC:avg_rss)
    targets = {}
    for location, location_path in target_files.items():
        fp, kept, total = process_csv_fingerprint(location_path)
        if not fp:
            print(f"Warning: no fingerprint for {location}, skipping.")
            continue
        targets[location] = {"fp": fp, "kept": kept, "total": total}

    print("Targets loaded, treasure hunt begins...")

        # Track history
    previous_scores = []

        # Header
    print("\n" + "=" * 170)
    print(
        f"{'TIME':<24} | {'SCORE 1':<10} | {'STATUS 1':<8} | {'STABLE 1':<7} || "
        f"{'SCORE 2':<10} | {'STATUS 2':<8} | {'STABLE 2':<7} || "
        f"{'SCORE 3':<10} | {'STATUS 3':<8} | {'STABLE 3':<7} || "
        f"{'SCORE 4':<10} | {'STATUS 4':<8} | {'STABLE 4':<7}")
    print("-" * 170)

    while True:
    # 1. Loading live/current fingerprint
        live_fp, live_kept, live_total = process_csv_fingerprint(LIVE_OBSERVATION)
        if not live_fp:
            print("Warning: no live fingerprint, skipping this cycle.")
            time.sleep(REFRESHING_TIME)
            continue

    # 2. Calculate score
        current_scores = []
        for location, target_info in targets.items():
            target_fp = target_info["fp"]
            s = score(target_fp, live_fp)
            current_scores.append((location, s, f"{target_info['kept']}/{target_info['total']}"))

    # 3. Plot fingerprints


    # 4. Hotter or Colder?
        hotter_or_colder(current_scores, previous_scores)

    # 5. Update history
        previous_scores = current_scores

    # 6. Refresh
        time.sleep(REFRESHING_TIME)


# =============================================================================================
if __name__ == "__main__":
    main()




