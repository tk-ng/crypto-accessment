Feature: Crypto.com orderbook WebSocket client tests

    Background:
        Given the WebSocket is connected to the endpoint "wss://stream.crypto.com/exchange/v1/market"

  
    Scenario Outline: Positive Test Cases
        When I subscribe to orderbook channel for "<instrument_name>" with depth <depth> and subscription type "<subscription_type>" and update frequency <update_frequency>
        Then the subscription confirmation matches the subscription schema
        And I receive a subscription confirmation with code 0 
        And the response fields matches the parameters if specified, else match default
        And the response update frequency is within the specified else default interval
  

        Examples: Valid inputs
        | instrument_name | depth | subscription_type   | update_frequency |
        | BTCUSD-PERP     | 10    | SNAPSHOT_AND_UPDATE | 100              |
        | BTCUSD-PERP     | 10    | None                | None             |
        | AAVEUSD-PERP    | 50    | SNAPSHOT            | 500              |
        | AAVE_USD        | 10    | SNAPSHOT_AND_UPDATE | None             |
  
  
    Scenario Outline: Negative Test Cases
        When I subscribe to orderbook channel for "<instrument_name>" with depth <depth> and subscription type "<subscription_type>" and update frequency <update_frequency>
        Then the response message should consist of error code <code> and message "<message>"
    

        Examples: Invalid inputs
        | instrument_name | depth | subscription_type   | update_frequency | code  | message                                |
        | INVALID         | 10    | None                | None             | 40003 | Unknown symbol                         |
        | None            | 10    | None                | None             | 40003 | Unknown symbol                         |
        | BTCUSD-PERP     | None  | None                | None             | 40003 | Invalid depth                          |
        | BTCUSD-PERP     | 20    | None                | None             | 40003 | Invalid depth                          |
        | BTCUSD-PERP     | inv   | None                | None             | 40003 | Invalid depth                          |
        | AAVEUSD-PERP    | 50    | INVALID_SUB         | None             | 40003 | Invalid book_subscription_type         |
        | AAVE_USD        | 10    | SNAPSHOT_AND_UPDATE | 500              | 40003 | Unsupported depth/interval combination |
        | AAVE_USD        | 10    | None                | 300              | 40003 | Invalid book_update_frequency          |