# frozen_string_literal: true

module Guardian
  class Stats
    attr_reader :total_processed, :total_anomalies, :anomaly_rate, :status_distribution, :cache

    def initialize(data)
      @total_processed = data["total_processed"]
      @total_anomalies = data["total_anomalies"]
      @anomaly_rate = data["anomaly_rate"]
      @status_distribution = data["status_distribution"] || {}
      @cache = data["cache"] || {}
    end

    def approval_rate
      return 0 if @total_processed.zero?
      (@status_distribution["approved"].to_f / @total_processed * 100).round(2)
    end

    def to_s
      "Processed: #{@total_processed} | Anomalies: #{@total_anomalies} (#{(@anomaly_rate * 100).round(2)}%)"
    end
  end
end
