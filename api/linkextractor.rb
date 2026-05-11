#!/usr/bin/env ruby
# encoding: utf-8

require "sinatra"
require "open-uri"
require "uri"
require "nokogiri"
require "json"
require "redis"

set :protection, :except=>:path_traversal

use_cache = ENV.fetch("USE_CACHE", "true") == "true"

redis = nil
if use_cache
  redis = Redis.new(url: ENV["REDIS_URL"] || "redis://localhost:6379")
  puts "[Ruby API] Redis conectado: #{ENV['REDIS_URL'] || 'redis://localhost:6379'}"
else
  puts "[Ruby API] Iniciando SEM cache."
end

Dir.mkdir("logs") unless Dir.exist?("logs")
cache_log = File.new("logs/extraction.log", "a")

get "/" do
  "Usage: http://<hostname>[:<prt>]/api/<url>"
end

get "/api/*" do
  url = [params['splat'].first, request.query_string].reject(&:empty?).join("?")
  cache_status = "BYPASS"
  jsonlinks = nil

  if use_cache && redis
    cache_status = "HIT"
    jsonlinks = redis.get(url)
    cache_status = "MISS" if jsonlinks.nil?
  end

  if jsonlinks.nil?
    jsonlinks = JSON.pretty_generate(extract_links(url))
    redis.set(url, jsonlinks) if use_cache && redis
  end

  cache_log.puts "#{Time.now.to_i}\t#{cache_status}\t#{url}"
  cache_log.flush

  status 200
  headers "content-type" => "application/json"
  body jsonlinks
end

def extract_links(url)
  links = []
  doc = Nokogiri::HTML(open(url))
  doc.css("a").each do |link|
    text = link.text.strip.split.join(" ")
    begin
      links.push({
        text: text.empty? ? "[IMG]" : text,
        href: URI.join(url, link["href"])
      })
    rescue
    end
  end
  links
end
