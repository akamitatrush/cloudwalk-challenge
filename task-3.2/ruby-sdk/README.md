# 💎 Guardian Client - Ruby SDK

> Ruby SDK and CLI for Transaction Guardian API

## 📦 Installation
```bash
gem install guardian-client
```

Or add to your Gemfile:
```ruby
gem 'guardian-client'
```

## 🚀 Quick Start

### As a Library
```ruby
require 'guardian'

# Configure globally
Guardian.configure do |config|
  config.api_url = "http://34.39.251.57:8001"
  config.api_key = "your-api-key"  # optional
end

# Or create a client
client = Guardian::Client.new(api_url: "http://34.39.251.57:8001")

# Check health
client.health
# => {"status"=>"healthy", "version"=>"2.2.0"}

# Get stats
stats = client.stats
puts stats.total_processed  # => 5000
puts stats.anomaly_rate     # => 0.15

# Send transaction
result = client.send_transaction(status: "approved", count: 150)
puts result.alert_level     # => "NORMAL"
puts result.anomaly?        # => false

# Get anomalies
anomalies = client.anomalies(limit: 10, level: "CRITICAL")
anomalies.each { |a| puts a.to_s }

# Shugo Prediction Engine
client.shugo.status
client.shugo.predict(minutes: 30)
client.shugo.forecast(hours: 6)
client.shugo.patterns
```

## 🖥️ CLI Usage
```bash
# Status
guardian status --url http://34.39.251.57:8001

# Send transaction
guardian transaction approved 150

# List anomalies
guardian anomalies --limit 10 --level CRITICAL

# Shugo commands
guardian shugo status
guardian shugo predict 30
guardian shugo forecast 6
guardian shugo patterns
guardian shugo train
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `guardian status` | Show system status |
| `guardian transaction STATUS COUNT` | Send a transaction |
| `guardian anomalies` | List recent anomalies |
| `guardian shugo status` | Shugo engine status |
| `guardian shugo predict [MIN]` | Predict volume |
| `guardian shugo forecast [HOURS]` | Forecast volume |
| `guardian shugo patterns` | Show patterns |
| `guardian shugo train` | Train with data |
| `guardian version` | Show version |

## 🔧 Options

| Option | Description |
|--------|-------------|
| `--url` | API URL (default: http://localhost:8001) |
| `--key` | API Key for authentication |

## 📄 License

MIT License - CloudWalk Challenge 2026
