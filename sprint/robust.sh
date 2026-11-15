#!/bin/bash
# Robustness arm (prereg): neutral re-check at all three levels, runset.json "robust" (60 items), Haiku (4 shards)
# then Sonnet (2 shards). Checks the plan budget before each model. Log: sprint/logs/robust.log
cd "$(dirname "$0")/.."
LOG=sprint/logs/robust.log
for spec in "claude-haiku-5-5 haiku 4 1" "claude-sonnet-5-5 sonnet 2 3"; do
  set -- $spec
  can=$($BUDGET_CHECK $4 2>&1); rc=$?
  echo "$(date -Is) $2 robust: can_rc=$rc $can" >> $LOG
  [ $rc -eq 0 ] || { echo "$(date -Is) STOP: can refused" >> $LOG; exit 2; }
  for ((k=0; k<$3; k++)); do .venv/bin/python sprint/run_shard.py --model $1 --ids sprint/runset.json --key robust \
      --arm neutral --shard $k --nshards $3 --out sprint/out/shards/$2_robust.$k.jsonl >> sprint/logs/$2_robust.$k.log 2>&1 & done
  wait
  echo "$(date -Is) $2 robust done items=$(cat sprint/out/shards/$2_robust.?.jsonl | grep -c '"rebuttal3"')" >> $LOG
done
echo "$(date -Is) ROBUST DONE" >> $LOG
