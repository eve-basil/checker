# checker

Worker intended for periodic retrieval and storage of market prices utilizing the following APIs:
- [eve-basil/watches](https://github.com/eve-basil/watches)
- [Eve-Central MarketStat API](http://dev.eve-central.com/evec-api/start#marketstat)
- [eve-basil/prices](https://github.com/eve-basil/prices)

## Project Status
This is currently a prototype.

## Usage
This application expects 4 environmental variables to be available at runtime:
- `WATCHES_URL`: The URL to find typeIDs to check (e.g. `https://api.hostna.me:19991/watches`)
- `EVECENTRAL_URL`: The URL to find price data at (e.g. `https://api.eve-central.com/api/marketstat`)
- `SYSTEM_ID`: The systemID to fetch price data for (e.g. `30000142` for Jita)
- `PRICES_URL`: The URL to store price data under (e.g. `https://api.hostna.me:19992/prices`)

This application is appropriate for periodic execution, e.g. with crontab

```
# Example cron entry
40 20 * * * someuser source $HOME/.profile; python /path/to/checker.py >> $HOME/log/checker.log 2>&1

```
