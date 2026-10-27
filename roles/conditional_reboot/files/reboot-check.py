#!/usr/bin/python3
"""Only reboot when enabled, in the maintenance window, and required by the OS."""
import argparse
import datetime
import json
import logging
from pathlib import Path
import subprocess


def required(config, run=subprocess.run):
    if config['requirement_file']:
        return Path(config['requirement_file']).exists()
    result = run(config['requirement_command'], capture_output=True, text=True, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError('Reboot requirement check failed; refusing to reboot')
    return result.returncode == 1


def in_window(config, now):
    if config['day_filter_enabled'] and not (
        now.isoweekday() == config['day_of_week']
        and config['day_of_month_range'][0] <= now.day <= config['day_of_month_range'][1]
    ):
        return False
    scheduled = now.replace(hour=config['hour'], minute=config['minute'], second=0, microsecond=0)
    return 0 <= (now - scheduled).total_seconds() < config['window_minutes'] * 60


def execute(config, now=None, dry_run=False, run=subprocess.run):
    now = now or datetime.datetime.now()
    if not config['enabled']:
        return 'disabled'
    if not in_window(config, now):
        return 'outside maintenance window'
    if not required(config, run):
        return 'no reboot required'
    if dry_run:
        return 'reboot required (dry run)'
    run(config['reboot_command'], check=True)
    return 'reboot requested'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s',
                        filename=config['log_path'] or None)
    try:
        logging.info(execute(config, dry_run=args.dry_run))
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        logging.error('%s', error)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
