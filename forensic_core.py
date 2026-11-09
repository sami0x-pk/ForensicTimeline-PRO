import csv
import heapq
from datetime import datetime, timedelta

SEVERITY = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

def load_events(path):
    events = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "source", "event_type", "severity", "details"}

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Invalid CSV columns")

        for row in reader:
            dt = datetime.strptime(
                row["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
            severity = row["severity"].upper().strip()

            if severity not in SEVERITY:
                severity = "LOW"

            events.append({
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "source": row["source"],
                "event_type": row["event_type"],
                "severity": severity,
                "details": row["details"]
            })

    return events


def merge_sort(events):
    if len(events) <= 1:
        return events[:]

    mid = len(events) // 2
    left = merge_sort(events[:mid])
    right = merge_sort(events[mid:])

    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]["timestamp"] <= right[j]["timestamp"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    return result + left[i:] + right[j:]


def binary_search(events, target):
    low, high = 0, len(events) - 1

    while low <= high:
        mid = (low + high) // 2
        value = events[mid]["timestamp"]

        if value == target:
            return mid
        elif value < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def hash_statistics(events):
    stats = {
        "sources": {},
        "event_types": {},
        "severities": {}
    }

    for event in events:
        for category, key in [
            ("sources", "source"),
            ("event_types", "event_type"),
            ("severities", "severity")
        ]:
            value = event[key]
            stats[category][value] = stats[category].get(value, 0) + 1

    return stats


def top_n_events(events, n=5):
    return heapq.nlargest(
        n, events,
        key=lambda e: SEVERITY[e["severity"]]
    )


def merge_sorted_sources(sources):
    heap = []

    for source_id, source in enumerate(sources):
        if source:
            heapq.heappush(
                heap, (source[0]["timestamp"], source_id, 0, source[0])
            )

    result = []

    while heap:
        _, source_id, index, event = heapq.heappop(heap)
        result.append(event)

        next_index = index + 1
        if next_index < len(sources[source_id]):
            item = sources[source_id][next_index]
            heapq.heappush(
                heap, (item["timestamp"], source_id, next_index, item)
            )

    return result


def incident_windows(events, minutes=10, min_events=2):
    ordered = merge_sort(events)
    windows = []

    for start in range(len(ordered)):
        start_time = datetime.strptime(
            ordered[start]["timestamp"], "%Y-%m-%d %H:%M:%S"
        )

        group = []

        for end in range(start, len(ordered)):
            end_time = datetime.strptime(
                ordered[end]["timestamp"], "%Y-%m-%d %H:%M:%S"
            )

            if end_time - start_time > timedelta(minutes=minutes):
                break

            group.append(ordered[end])

        if len(group) >= min_events:
            windows.append(group)

    return windows