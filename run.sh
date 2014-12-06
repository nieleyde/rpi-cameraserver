#!/bin/bash

set -x

rm -rf live.h264 

# fifos seem to work more reliably than pipes - and the fact that the
# fifo can be named helps ffmpeg guess the format correctly.
mkfifo live.h264

raspivid -w 1280 -h 720 -fps 25 -hf -t 86400000 -b 1800000 -o - | psips > live.h264 &

# Letting the buffer fill a little seems to help ffmpeg to id the stream
sleep 2

ffmpeg -y \
  -i live.h264 \
  -f s16le -i /dev/zero \
  -c:v copy \
  -map 0:0 -map 1:0 \
  -f segment \
  -hls_time 5 \
  -hls_list_size 10 \
  -segment_format mpegts \
  -segment_list "live/live.m3u8" \
  -segment_list_flags live \
  -segment_list_type m3u8 \
  "live/%08d.ts" < /dev/null 

# vim:ts=2:sw=2:sts=2:et:ft=sh
