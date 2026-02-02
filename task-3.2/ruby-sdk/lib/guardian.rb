# frozen_string_literal: true

require "httparty"
require "json"

require_relative "guardian/version"
require_relative "guardian/client"
require_relative "guardian/transaction"
require_relative "guardian/anomaly"
require_relative "guardian/shugo"
require_relative "guardian/stats"

module Guardian
  class Error < StandardError; end
  class APIError < Error; end
  class ConnectionError < Error; end
  class RateLimitError < Error; end

  class << self
    attr_accessor :api_url, :api_key

    def configure
      yield self
    end
  end
end
