#!/bin/bash
# Monitor script for duplicate-name validation
# Run after deployment to monitor the first 48 hours
# Usage: ./monitor_deployment.sh

set -e

LOG_FILE="${1:-.../backend/logs/duplicate_name_events.log}"
DURATION_HOURS="${2:-48}"
CHECK_INTERVAL_SECONDS=300 # Check every 5 minutes

echo "🔍 Monitoring Duplicate Name Validation Deployment"
echo "Log file: $LOG_FILE"
echo "Duration: $DURATION_HOURS hours"
echo "Check interval: $CHECK_INTERVAL_SECONDS seconds"
echo "---"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Counters
ACTIVE_ERRORS=0
INACTIVE_ERRORS=0
CHECK_COUNT=0
MAX_CHECKS=$(((DURATION_HOURS * 3600) / CHECK_INTERVAL_SECONDS))

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
	CHECK_COUNT=$((CHECK_COUNT + 1))

	clear
	echo "================================"
	echo "Deployment Monitor - Check #$CHECK_COUNT / $MAX_CHECKS"
	echo "Elapsed: $((CHECK_COUNT * CHECK_INTERVAL_SECONDS / 60)) minutes"
	echo "================================"
	echo ""

	# Count errors
	if [ -f "$LOG_FILE" ]; then
		ACTIVE_COUNT=$(grep -c "DUPLICATE_NAME_ACTIVE" "$LOG_FILE" 2>/dev/null || echo 0)
		INACTIVE_COUNT=$(grep -c "DUPLICATE_NAME_INACTIVE" "$LOG_FILE" 2>/dev/null || echo 0)
		TOTAL_ERRORS=$((ACTIVE_COUNT + INACTIVE_COUNT))

		echo "📊 Error Summary:"
		echo "  Active duplicates:   $ACTIVE_COUNT"
		echo "  Inactive duplicates: $INACTIVE_COUNT"
		echo "  Total errors:        $TOTAL_ERRORS"
		echo ""

		# Check for anomalies
		if [ $TOTAL_ERRORS -gt 1000 ]; then
			echo -e "${RED}⚠️  WARNING: >1000 errors detected!${NC}"
			echo "   Consider investigating or rolling back."
		elif [ $TOTAL_ERRORS -gt 100 ]; then
			echo -e "${YELLOW}⚠️  NOTICE: >100 errors detected${NC}"
			echo "   Normal activity, but keep monitoring."
		else
			echo -e "${GREEN}✓ Normal activity level${NC}"
		fi
		echo ""

		# Show recent errors
		echo "📝 Last 5 errors:"
		tail -5 "$LOG_FILE" | while read line; do
			echo "   $line"
		done
		echo ""

	else
		echo -e "${RED}✗ Log file not found: $LOG_FILE${NC}"
	fi

	# Show next check time
	NEXT_CHECK=$(date -d "+$CHECK_INTERVAL_SECONDS seconds" 2>/dev/null || echo "in $CHECK_INTERVAL_SECONDS seconds")
	echo "Next check: $NEXT_CHECK"

	# Wait before next check
	if [ $CHECK_COUNT -lt $MAX_CHECKS ]; then
		sleep $CHECK_INTERVAL_SECONDS
	fi
done

echo ""
echo "================================"
echo "✓ Monitoring Complete"
echo "================================"
echo ""
echo "📊 Final Summary:"
echo "  Total checks: $CHECK_COUNT"
echo "  Final active errors: $ACTIVE_COUNT"
echo "  Final inactive errors: $INACTIVE_COUNT"
echo "  Total errors: $TOTAL_ERRORS"
echo ""
echo "Next steps:"
echo "  1. Review ADMIN_GUIDE.md for any INACTIVE conflicts"
echo "  2. Check for patterns in error logs"
echo "  3. Confirm performance is acceptable"
echo "  4. Enable feature in production if all is well"
