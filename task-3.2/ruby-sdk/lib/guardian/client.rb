# frozen_string_literal: true

module Guardian
  class Client
    include HTTParty
    
    attr_reader :api_url, :api_key

    def initialize(api_url: nil, api_key: nil)
      @api_url = api_url || Guardian.api_url || "http://localhost:8001"
      @api_key = api_key || Guardian.api_key
    end

    def health
      get("/health")
    end

    def stats
      Stats.new(get("/stats"))
    end

    def send_transaction(status:, count:)
      response = post("/transaction", { status: status, count: count })
      Transaction.new(response)
    end

    def send_batch(transactions)
      response = post("/transactions/batch", { transactions: transactions })
      response
    end

    def anomalies(limit: 50, level: nil)
      params = { limit: limit }
      params[:level] = level if level
      response = get("/anomalies", params)
      response["anomalies"].map { |a| Anomaly.new(a) }
    end

    def shugo
      @shugo ||= Shugo.new(self)
    end

    private

    def get(path, params = {})
      request(:get, path, query: params)
    end

    def post(path, body = {})
      request(:post, path, body: body.to_json, headers: { "Content-Type" => "application/json" })
    end

    def request(method, path, options = {})
      options[:headers] ||= {}
      options[:headers]["X-API-Key"] = @api_key if @api_key

      response = self.class.send(method, "#{@api_url}#{path}", options)
      handle_response(response)
    rescue Errno::ECONNREFUSED, SocketError => e
      raise ConnectionError, "Cannot connect to #{@api_url}: #{e.message}"
    end

    def handle_response(response)
      case response.code
      when 200..299
        JSON.parse(response.body)
      when 429
        raise RateLimitError, "Rate limit exceeded. Retry after #{response['retry_after']}s"
      when 401, 403
        raise APIError, "Authentication failed"
      else
        raise APIError, "API error: #{response.code} - #{response.body}"
      end
    end
  end
end
