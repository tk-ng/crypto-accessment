from behave import *
from jsonschema import validate, ValidationError
import requests
from datetime import datetime, timedelta, timezone
from schemas.candlestick_schema import schema as candlestick_schema
from concurrent.futures import ThreadPoolExecutor
import time


@given('the API endpoint is "{url}"')
def set_api_endpoint(context, url):
    context.endpoint = url


@when('we send a GET request with "instrument_name" as "{instrument}", "timeframe" as "{timeframe}", "count" as "{count}", "start_ts" as "{start_ts}", and "end_ts" as "{end_ts}"')
def send_get_request_to_endpoint(context, instrument, timeframe, count, start_ts, end_ts):
    payload = {"instrument_name": instrument} if instrument != "None" else {}

    def to_int_or_none(s):
        if s and s.isdigit():
            return int(s)
        elif s == "None":
            return None
        else:
            return s

    optional_params = {
        "timeframe": timeframe if timeframe != "None" else None,
        "count": to_int_or_none(count),
        "start_ts": to_int_or_none(start_ts),
        "end_ts": to_int_or_none(end_ts)
    }

    for k, v in optional_params.items():
        if v is not None:
            payload[k] = v

    context.current_time = int(datetime.now(
        timezone.utc).timestamp() * 1000)  # in milliseconds
    context.one_day_ago_time = int(
        (datetime.now(timezone.utc) - timedelta(days=1)).replace(hour=0,
                                                                 minute=0, second=0, microsecond=0).timestamp() * 1000
    )
    context.response = requests.get(context.endpoint, params=payload)
    context.params = payload
    context.json_content = context.response.json()


@when("I send 120 requests to the endpoint in under 1 second")
def send_rapid_requests(context):
    def send_request():
        try:
            return requests.get(context.endpoint, params={"instrument_name": "AAVE_USD"})
        except Exception as e:
            return e

    with ThreadPoolExecutor(max_workers=120) as executor:
        start = time.time()
        context.responses = list(executor.map(
            lambda _: send_request(), range(120)))
        context.duration = time.time() - start


@then('the response should match the JSON schema')
def check_resp_result(context):
    try:
        validate(instance=context.json_content, schema=candlestick_schema)
    except ValidationError as e:
        assert False, f"schema validation error: {e.message}"


@then('the response header content-type is "{content_type}"')
def check_content_type(context, content_type):
    assert context.response.headers[
        'content-type'] == content_type, f'Incorrect Header: Content-Type: {context.response.headers['content-type']}. Expected: {content_type}'


@then('the response status code should be {status_code:d}')
def check_resp_status_code(context, status_code):
    assert context.response.status_code == status_code, f'Incorrect status code: {context.response.status_code}. Expected: {status_code}'


@then('each item interval in the response should match the specified "timeframe", or default to "1m" if not provided')
def check_interval(context):
    result_interval = context.json_content["result"]["interval"]
    if "timeframe" in context.params:
        assert result_interval == context.params[
            "timeframe"], f"Incorrect interval: {result_interval}"
    else:
        assert result_interval == "1m", f"Incorrect interval: {result_interval}"


@then('the number of items in the response should be less than or equal to the specified "count", or default to 25 if not provided')
def check_count(context):
    result_data = context.json_content["result"]["data"]

    if "count" in context.params:
        assert len(
            result_data) <= context.params["count"], f"Incorrect count: {len(result_data)}"
    else:
        assert len(result_data) <= 25, f"Incorrect count: {len(result_data)}"


@then('each item "t" timestamp should be greater than the specified "start_ts", or 1 day ago if "start_ts" is not specified')
def check_start_timestamp(context):
    result_data = context.json_content["result"]["data"]

    if "start_ts" in context.params:
        start_ts = context.params["start_ts"]
        for i, el in enumerate(result_data):
            assert el["t"] >= start_ts, (
                f'Item at index {i} has "t" = {el["t"]}, which is less than the specified start_ts = {start_ts}'
            )
    else:
        expected_start = context.one_day_ago_time
        for i, el in enumerate(result_data):
            assert el["t"] >= expected_start, (
                f'Item at index {i} has "t" = {el["t"]}, which is less than default start_ts = {expected_start} (1 day ago)'
            )


@then('each item "t" timestamp should be less than "end_ts" if "end_ts" is specified')
def check_end_timestamp(context):
    result_data = context.json_content["result"]["data"]

    if "end_ts" in context.params:
        end_ts = context.params["end_ts"]
        for i, el in enumerate(result_data):
            assert el["t"] <= end_ts, (
                f'Item at index {i} has "t" = {el["t"]}, which is more than the specified end_ts = {end_ts}'
            )
    else:
        expected_end = context.current_time
        for i, el in enumerate(result_data):
            assert el["t"] <= expected_end, (
                f'Item at index {i} has "t" = {el["t"]}, which is more than default end_ts = {expected_end} (1 day ago)'
            )


@then('the response error code should be {error_code:d} and message should be "{error_message}"')
def check_error_code_message(context, error_code, error_message):
    actual_code = context.json_content.get("code")
    actual_message = context.json_content.get("message")

    assert actual_code == error_code, f"Expected error code '{error_code}', but got '{actual_code}'"
    assert actual_message == error_message, f"Expected error message '{error_message}', but got '{actual_message}'"


@then("I should see at least one 429 Too Many Requests response")
def check_rate_limit(context):
    print(context.responses)
    status_codes = [
        r.status_code for r in context.responses if hasattr(r, 'status_code')]
    count_429 = status_codes.count(429)
    if context.duration <= 1:  # Only checks if 429 status_code exists if duration is within 1 second
        assert count_429 > 0, f"Expected at least one 429, got {count_429} in {context.duration:.2f} seconds."
