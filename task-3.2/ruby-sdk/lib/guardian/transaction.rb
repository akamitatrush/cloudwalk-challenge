# frozen_string_literal: true

module Guardian
  class Transaction
    attr_reader :is_anomaly, :alert_level, :anomaly_score, :rule_violations, :recommendation, :metrics, :cached

    def initialize(data)
      @is_anomaly = data["is_anomaly"]
      @alert_level = data["alert_level"]
      @anomaly_score = data["anomaly_score"]
      @rule_violations = data["rule_violations"] || []
      @recommendation = data["recommendation"]
      @metrics = data["metrics"] || {}
      @cached = data["cached"]
    end

    def anomaly?
      @is_anomaly
    end

    def critical?
      @alert_level == "CRITICAL"
    end

    def warning?
      @alert_level == "WARNING"
    end

    def to_h
      { is_anomaly: @is_anomaly, alert_level: @alert_level, anomaly_score: @anomaly_score, rule_violations: @rule_violations, recommendation: @recommendation }
    end
  end
end
