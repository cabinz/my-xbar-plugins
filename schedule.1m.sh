#!/bin/bash

# Get the current time in HH:MM format
current_time=$(date +"%H:%M")

# Convert current time to minutes since midnight for easier comparison
current_minutes=$((10#$(echo $current_time | cut -d: -f1) * 60 + 10#$(echo $current_time | cut -d: -f2)))

# Function to convert HH:MM time to minutes since 00:00
to_minutes() {
    hour=$(echo $1 | cut -d: -f1)
    minute=$(echo $1 | cut -d: -f2)
    echo $((10#$hour * 60 + 10#$minute))
}

# Time table
# Each line in the format "Begin_Time End_Time Event_Name"
csv_file="/Applications/SwiftBar/schedule/.timetable.csv"
timetable=$(cat "$csv_file")

# Check current time against each time range
event_found=0
idx_found=0
while IFS=',' read -r start_time end_time event; do
    # Convert times to minutes since midnight
    start_minutes=$(to_minutes $start_time)
    end_minutes=$(to_minutes $end_time)

    if [[ $start_minutes -gt $end_minutes ]]; then
        # Events spans midnight
        if [[ $current_minutes -ge $start_minutes || $current_minutes -lt $end_minutes ]]; then
            echo $event
            event_found=1
            break
        fi
    elif [[ $current_minutes -ge $start_minutes && $current_minutes -lt $end_minutes ]]; then
        # Normal events within daytime
        echo $event
        event_found=1
        break
    fi
    ((idx_found++))
done <<< "$timetable"

if [[ $event_found -eq 0 ]]; then
    echo "no event"
fi

echo "---"
# echo "$timetable"
cur_idx=0
while IFS=',' read -r start_time end_time event; do
    printf "%-10s %-10s %-s" $start_time $end_time $event
    if [[ $event_found -eq 1 ]] && [[ $idx_found -eq $cur_idx ]]; then
        echo -n " ⬅"
    fi
    echo "" # newline 
    ((cur_idx++))
done <<< "$timetable"
