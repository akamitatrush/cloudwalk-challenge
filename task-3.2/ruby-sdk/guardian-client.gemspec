# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "guardian-client"
  spec.version       = "1.0.0"
  spec.authors       = ["Sérgio Henrique"]
  spec.email         = ["sergio@lognullsec.com"]

  spec.summary       = "Ruby SDK for Transaction Guardian API"
  spec.description   = "A Ruby client library and CLI for interacting with Transaction Guardian - CloudWalk Monitoring Intelligence Challenge"
  spec.homepage      = "https://github.com/akamitatrush/cloudwalk-challenge"
  spec.license       = "MIT"
  spec.required_ruby_version = ">= 2.7.0"

  spec.files         = Dir["lib/**/*", "bin/*", "README.md"]
  spec.bindir        = "bin"
  spec.executables   = ["guardian"]
  spec.require_paths = ["lib"]

  spec.add_dependency "httparty", "~> 0.21"
  spec.add_dependency "thor", "~> 1.3"
  spec.add_dependency "terminal-table", "~> 3.0"
  spec.add_dependency "colorize", "~> 1.1"

  spec.add_development_dependency "rspec", "~> 3.12"
  spec.add_development_dependency "webmock", "~> 3.19"
end
