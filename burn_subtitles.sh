#!/bin/bash

shopt -s nullglob

for video in *.mkv; do
    base="${video%.*}"
    subtitle="${base}.srt"
    if [ -f "$subtitle" ]; then
        echo "Processing '$video' with subtitles '$subtitle'..."
        ffmpeg -i "$video" -vf "subtitles='$subtitle'" -c:v libx264 -crf 18 -preset slow -c:a copy "${base}_subbed.mkv"
    else
        echo "Subtitle file '$subtitle' not found for '$video'. Skipping."
    fi
done

