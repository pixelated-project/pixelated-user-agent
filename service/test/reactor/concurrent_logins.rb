#
# Copyright (c) 2015 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.


# We use this script to simulate the login of multiple concurrent users, with
# one login per second.
#
# To use it, you need:
# -ruby
# -pre-created users
#
# This can be run with `ruby concurrent_logins.rb <x>`
# where x is the number of users you want to login.
#
# It was created to measure login times internally on the application with
# varying number of users
require 'fileutils'

USER_PATTERN = "loadtest%d"
PASSWORD_PATTERN = "password_%d"
COUNT = ARGV[0].to_i

def header_options
  "--header 'X-Requested-With: XMLHttpRequest' --header 'X-XSRF-TOKEN: blablabla'"
end

def cookies
  "--cookie 'XSRF-TOKEN: blablabla'" 
end

def curl_command
  "curl --silent"
end

def login_command(user_index, username, password)
  FileUtils.rm "/tmp/user#{user_index}.cookie", force: true
  "#{curl_command} -X POST --data 'username=#{username}&password=#{password}' --cookie-jar /tmp/user#{user_index}.cookie -w '%{http_code}|%{time_total}' --output '/dev/null' #{cookies} #{header_options} http://localhost:3333/login"
end

def check_inbox(user_index)
  "#{curl_command} --cookie /tmp/user#{user_index}.cookie http://localhost:3333"
end

def complete_login(user_index, user, password)
  start = Time.now
  login_response = `#{login_command(user_index, user, password)}`
  status_code, total_time = login_response.split("|")
  puts "Login request #{total_time}"
  if status_code.to_i == 200
    interstitial = Time.now
    begin
      sleep 0.05
      inbox = `#{check_inbox(user_index)}`
    end until /compose-trigger/.match(inbox)
    puts "Login loading #{sprintf('%.3f',Time.now - interstitial)}"
    puts "Login total #{sprintf('%.3f',Time.now - start)}"
  else
    puts "Login failed with #{status_code} #{sprintf('%.3f',Time.now - start)}"
  end
end

def multi_login
  ts = (1...(1+COUNT)).map do |user_index|
    t = Thread.new do
      username = USER_PATTERN % [user_index]
      password = PASSWORD_PATTERN % [user_index]
      complete_login(user_index, username, password)
    end
    sleep 1
    t
  end

  ts.each(&:join)
end

multi_login
