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
read -r -d '' timetable << 'EOF'
23:30 07:30 sleep
07:30 08:30 brkfst
08:30 10:00 gym
10:00 12:00 paper
12:00 14:00 work
14:00 14:30 lunch
14:30 15:00 flex
15:00 18:00 work
18:00 18:30 flex
18:30 19:30 dinner
19:30 22:30 work
22:30 23:00 flex
23:00 23:30 lang
EOF

# Check current time against each time range
event_found=0
idx_found=0
while read line; do
    # Extract times and event from the line
    # sed for removing leading and ending space and tab
    start_time=$(echo $line | awk '{print $1}')
    end_time=$(echo $line | awk '{print $2}')
    event=$(echo $line | awk '{$1=$2=""; print $0}' | sed 's/^[ \t]*//;s/[ \t]*$//') 

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
while IFS= read -r line; do
    printf "%-8s %-8s %-s" $(echo $line | awk '{print $1, $2, $3" "$4" "$5" "$6" "$7" "$8}')
    if [[ $event_found -eq 1 ]] && [[ $idx_found -eq $cur_idx ]]; then
        printf " ⬅"
    fi
    printf "\n"
    ((cur_idx++))
done <<< "$timetable"
