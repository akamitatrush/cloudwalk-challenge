# frozen_string_literal: true

module Guardian
  class Anomaly
    attr_reader :timestamp, :alert_level, :score, :violations, :transaction

    def initialize(data)
      @timestamp = data["timestamp"]
      @alert_level = data["alert_level"]
      @score = data["score"]
      @violations = data["violations"] || []
      @transaction = data["transaction"]
    end

    def critical?
      @alert_level == "CRITICAL"
    end

    def to_s
      "[#{@alert_level}] #{@timestamp} - Score: #{@score}"
    end
  end
end
