# frozen_string_literal: true

module Guardian
  class Shugo
    def initialize(client)
      @client = client
    end

    def status
      @client.send(:get, "/shugo/status")
    end

    def predict(minutes: 30)
      @client.send(:get, "/shugo/predict", { minutes: minutes })
    end

    def forecast(hours: 6)
      @client.send(:get, "/shugo/forecast", { hours: hours })
    end

    def patterns
      @client.send(:get, "/shugo/patterns")
    end

    def train
      @client.send(:post, "/shugo/train")
    end

    def ready?
      status["status"] == "ready"
    end
  end
end
