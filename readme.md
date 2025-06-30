# Crypto.com WebSocket Automation Test Suite

This test suite uses [Behave](https://behave.readthedocs.io/) for BDD-style automated testing of the Crypto.com exchange REST and WebSocket APIs.

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/tk-ng/crypto-accessment.git
cd <the-cloned-repo-directory>
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate     # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests with Behave

```bash
behave # Runs both REST and Websocket APIs tests
behave features/task_1_api_get_candlestick.feature # Runs REST API tests only
behave features/task_2_ws_book_subscription.feature # Runs Websocket API tests only
```

---

## What This Test Suite Covers

---

## REST API Testing Capabilities

### ✅ Endpoint: `GET /public/get-candlestick`

This test suite verifies the behavior of Crypto.com's candlestick REST API with the following coverage:

- **Schema Validation**  
  Ensures the response structure conforms to the expected JSON schema using `jsonschema`.

- **Header Validation**  
  Confirms correct `Content-Type` header is returned in responses.

- **Status Code Assertion**  
  Asserts expected HTTP status codes (e.g., `200 OK`, `429 Too Many Requests`, etc.).

- **Query Parameter Logic**

  - Validates the effect of query params like `instrument_name`, `timeframe`, `count`, `start_ts`, and `end_ts`.
  - Defaults are tested when parameters are omitted (e.g., default `timeframe = 1m`, `count = 25`, etc.).

- **Time Range Validation**

  - Ensures that timestamps (`t`) in the returned candlestick data:
    - Start from `start_ts` or 1 day ago by default.
    - End at `end_ts` or the current time.

- **Rate Limiting Test**
  - Simulates high-volume requests (120 in <1 second) and verifies the server returns HTTP 429 as expected.

---

## Common Automation Coverage

The following types of tests are included in this suite:

- ✅ GET request execution and response capture
- ✅ Input parameter combination and edge case testing
- ✅ Fallback/default behavior when optional parameters are not provided
- ✅ Schema validation using `jsonschema`
- ✅ Rate limiting enforcement (429 detection)
- ✅ High concurrency handling using `ThreadPoolExecutor`
- ✅ Full BDD flow using Behave for scenario tracking and readability

---

### ✅ WebSocket Testing Capabilities

- **Connection Verification**  
  Ensures successful connection to Crypto.com's WebSocket endpoint.

- **Valid Subscription Scenarios**  
  Subscribes with combinations of `instrument_name`, `depth`, `subscription_type`, and `update_frequency`, asserting:

  - Response matches expected values.
  - Data matches provided depth.
  - Schema validity using `jsonschema`.

- **Invalid Subscription Scenarios**  
  Tests malformed or unsupported combinations and verifies proper error codes and messages.

- **Schema Validation**  
  Uses separate JSON Schemas for:

  - Snapshot-only responses.
  - Snapshot-and-update or delta responses.

- **Update Frequency Validation**  
  Verifies that messages are sent at the expected interval (default or user-defined). |

---

## Common Automation Coverage

These are the typical test areas this framework automates:

- ✅ WebSocket connection handling
- ✅ Dynamic subscription message generation
- ✅ Schema-based payload validation
- ✅ Interval timing enforcement
- ✅ Rate-limiting and error handling
- ✅ BDD-style scenario reporting via `behave`

---

## Notes

- Websocket received message capture is limited to **10 messages per run** (can be configured).
- Make sure your environment has **stable internet** to ensure reliability.

---

## Contact

For issues or contributions, please open a pull request or file an issue in the repository.
