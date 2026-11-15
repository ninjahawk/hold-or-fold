#!/bin/bash
# Sonnet in blocks of 50 (prereg cost rule). Before every block: `$BUDGET_CHECK <worst>` (local plan-budget check) and the
# 5-hour meter; if can refuses or 5h >= 70, start no block and re-check every 15 min. Log: sprint/logs/sonnet_blocks.log
cd "$(dirname "$0")/.."
W=${W:-3}
LOG=sprint/logs/sonnet_blocks.log
meter() { ($METER_CMD); }
for L in ${BLOCKS:-100 150 200 250 300}; do
  while true; do
    read wk fh < <(meter)
    can=$($BUDGET_CHECK $W 2>&1); rc=$?
    echo "$(date -Is) block-to-$L weekly=$wk five_hour=$fh can_rc=$rc $can" >> $LOG
    if [ $rc -eq 0 ] && [ "$fh" -lt 70 ]; then break; fi
    if [ $rc -ne 0 ] && [ "$fh" -lt 70 ]; then echo "$(date -Is) STOP: can refused (weekly line)" >> $LOG; exit 2; fi
    sleep 900
  done
  for k in 0 1; do .venv/bin/python sprint/run_shard.py --model claude-sonnet-5-5 --ids sprint/runset.json --shard $k \
      --nshards 2 --limit $L --out sprint/out/shards/sonnet.$k.jsonl >> sprint/logs/sonnet.$k.log 2>&1 & done
  wait
  echo "$(date -Is) block-to-$L done items=$(cat sprint/out/shards/sonnet.?.jsonl | grep -c '"rebuttal3"')" >> $LOG
done
echo "$(date -Is) ALL BLOCKS DONE" >> $LOG
