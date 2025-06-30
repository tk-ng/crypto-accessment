Feature: Test Crypto.com public/get-candlestick endpoint

  Background:
    Given the API endpoint is "https://api.crypto.com/exchange/v1/public/get-candlestick"
  
  Scenario Outline: 200 Responses
    When we send a GET request with "instrument_name" as "<instrument_name>", "timeframe" as "<timeframe>", "count" as "<count>", "start_ts" as "<start_ts>", and "end_ts" as "<end_ts>"
    Then the response should match the JSON schema
    And the response header content-type is "application/json"
    And the response status code should be <status_code>
    And each item interval in the response should match the specified "timeframe", or default to "1m" if not provided
    And the number of items in the response should be less than or equal to the specified "count", or default to 25 if not provided
    And each item "t" timestamp should be greater than the specified "start_ts", or 1 day ago if "start_ts" is not specified
    And each item "t" timestamp should be less than "end_ts" if "end_ts" is specified


    Examples: Valid Params
        | instrument_name | timeframe | count | start_ts      | end_ts              | status_code |
        | 1INCHUSD-PERP   | None      | None  | None          | None                | 200         |
        | 1INCH_USD       | 5m        | None  | None          | None                | 200         |
        | 1INCH_USDT      | M15       | 10    | None          | None                | 200         |
        | AAVEUSD-PERP    | None      | 20    | None          | None                | 200         |
        | AAVE_USD        | H12       | 5     | 1613544000000 | None                | 200         |
        | ADA_USD         | 7D        | 20    | 1739145600000 | 1750636800000       | 200         |
        | 1INCHUSD-PERP   | None      | 20    | 1739145600000 | 1750636800000       | 200         |
        | 1INCH_USD       | 5m        | None  | 1739145600000 | 1750636800000       | 200         |


  Scenario Outline: Negative Test Cases
    When we send a GET request with "instrument_name" as "<instrument_name>", "timeframe" as "<timeframe>", "count" as "<count>", "start_ts" as "<start_ts>", and "end_ts" as "<end_ts>"
    Then the response header content-type is "application/json"
    And the response status code should be <status_code>
    And the response error code should be <error_code> and message should be "<error_message>"

    Examples: Invalid Params
        | instrument_name | timeframe | count | start_ts      | end_ts              | status_code | error_code | error_message            |
        | None            | None      | None  | None          | None                | 400         | 40003      | Invalid request          |
        | INV_INST_NAME   | None      | None  | None          | None                | 400         | 40004      | Invalid instrument_name  |
        | ADA_USD         | 13h       | None  | None          | None                | 400         | 40003      | Invalid request          |
        | AAVEUSD-PERP    | None      | inv   | None          | None                | 500         | 50001      | Internal error           |
        | AAVEUSD-PERP    | None      | 0     | None          | None                | 400         | 40004      | Count must be positive   |
        | AAVEUSD-PERP    | None      | -1    | None          | None                | 400         | 40004      | Count must be positive   |
        | AAVE_USD        | None      | None  | inv           | None                | 500         | 50001      | Internal error           |
        | ADA_USD         | None      | None  | None          | inv                 | 500         | 50001      | Internal error           |


  Scenario: Sending more than 100 requests in 1 second triggers rate limit
    When I send 120 requests to the endpoint in under 1 second
    Then I should see at least one 429 Too Many Requests response