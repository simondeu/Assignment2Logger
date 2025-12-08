import matplotlib.pyplot as plt
import numpy as np
loc1 = {"Mac1": 491, "Mac2": 235, "Mac3": 752, "Mac4": 1522, "Mac5":1445, "Mac6": 491, "Mac7": 235, "Mac8": 752, "Mac9": 1522, "Mac10":1445}
loc2 = {"Mac1": 491, "Mac2": 235, "Mac3": 752, "Mac4": 1522, "Mac5":1445, "Mac6": 491, "Mac7": 235, "Mac8": 752, "Mac9": 1522, "Mac10":1445}
loc3 = {"Mac1": 491, "Mac2": 235, "Mac3": 752, "Mac4": 1522, "Mac5":1445, "Mac6": 491, "Mac7": 235, "Mac8": 752, "Mac9": 1522, "Mac10":1445}

locations = [loc1, loc2, loc3]
bar_width = 1/len(locations)

locations = [loc1, loc2, loc3]
names = ["Loc1", "Loc2", "Loc3"]

addresses = list(loc1.keys())
x = np.arange(len(addresses)) * 1.5
width = 1 / len(locations)        # bar width

fig, ax = plt.subplots(figsize=(12, 5))

for i, loc in enumerate(locations):
    ax.bar(x + i*width, list(loc.values()), width, label=names[i],edgecolor='black')

ax.set_xticks(x + width)  #for x labels
ax.set_xticklabels(addresses, rotation=45)

ax.legend()
ax.grid(which='major', linestyle='--', linewidth=0.8, alpha=0.7)

ax.set_axisbelow(True)
ax.set_ylabel("RSSI",fontsize=12)
ax.set_xlabel("Mac Addresses",fontsize=12)
ax.set_title("RSSI at Given Location for MAC Addresses", fontsize=14)
plt.tight_layout()
plt.show()