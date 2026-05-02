# OSQuery Insider Threat Configuration

This folder contains the OSQuery configuration and log aggregator for the Healthcare AI Security Platform.

## Structure
```
osquery/
├── config/
│   ├── osquery.conf          # Main OSQuery configuration
│   └── packs/
│       └── insider_threat.conf   # Custom query pack
├── aggregator/
│   ├── log_aggregator.py     # FastAPI server for log collection
│   ├── data_exporter.py      # Export logs for ML training
│   └── requirements.txt
└── sample_data/
    └── synthetic_logs.json   # Synthetic training data
```

## Quick Start
1. Copy `osquery.conf` to your OSQuery config directory
2. Run `pip install -r aggregator/requirements.txt`
3. Start aggregator: `python aggregator/log_aggregator.py`
4. OSQuery will push logs to `http://localhost:8080/logs`
