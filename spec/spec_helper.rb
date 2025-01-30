# Require all of the necessary gems
require 'rspec'
require 'capybara/rspec'
require 'rack/jekyll'
require 'rack/test'
require "selenium/webdriver"
require 'pry'

RSpec.configure do |config|
	config.include Capybara::DSL

	config.expect_with :rspec do |expectations|
		expectations.include_chain_clauses_in_custom_matcher_descriptions = true
	end

	config.mock_with :rspec do |mocks|
		mocks.verify_partial_doubles = true
	end

	# Configure Capybara to use Selenium.
	Capybara.register_driver :selenium do |app|
		Capybara::Selenium::Driver.new(app, browser: :chrome)
	end

	Capybara.register_driver :chrome do |app|
		Capybara::Selenium::Driver.new(app, browser: :chrome)
	end

	Capybara.register_driver :headless_chrome do |app|
		capabilities = Selenium::WebDriver::Remote::Capabilities.chrome(
		chromeOptions: { args: %w(headless disable-gpu) }
	)

	Capybara::Selenium::Driver.new app,
		browser: :chrome,
		desired_capabilities: capabilities
	end

	Capybara.javascript_driver = :headless_chrome
	Capybara.app = Rack::Jekyll.new(force_build: true)

end
