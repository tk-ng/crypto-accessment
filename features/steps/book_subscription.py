from behave import *
from websocket import WebSocketApp, WebSocketTimeoutException, WebSocketConnectionClosedException
from jsonschema import validate, ValidationError
from functools import partial
from schemas.book_snapshot_schema import schema as snapshot_schema
from schemas.book_delta_update_schema import schema as delta_update_schema
import time
import json
import threading


def on_message(wsapp, message, context):
    # Limit the amount of messages to be processed for testing purpose
    if len(context.received_msg) <= 10:
        context.received_msg.append(
            # convert ts to be in milliseconds
            {**message, "timestamp": time.time()*1000})


def on_close(wsapp, close_status_code, close_msg, context):
    """If the websocket connection closes it should have one of the 
    predefined Websocket Termination Codes
    """
    print(f"WebSocket closed with code: {close_status_code}")
    print(f"Message: {close_msg}")

    context.ws_thread.join()

    assert close_status_code in [
        1000, 1006, 1013], f"Unexpected close code: {close_status_code} with message: {close_msg}"


@given('the WebSocket is connected to the endpoint "{url}"')
def step_given_ws_endpoint(context, url):
    context.endpoint = url
    context.received_msg = []
    context.wsapp = WebSocketApp(
        url, on_message=partial(on_message, context=context), on_close=partial(on_close, context=context))
    try:
        wst = threading.Thread(target=context.wsapp.run_forever)
        wst.daemon = True
        wst.start()
    except (WebSocketTimeoutException, WebSocketConnectionClosedException):
        print("WebSocket closed or timed out gracefully.")
    time.sleep(2)  # Ensure connection is established


@when('I subscribe to orderbook channel for "{instrument_name}" with depth {depth} and subscription type "{subscription_type}" and update frequency {update_frequency}')
def step_when_subscribe(context, instrument_name, depth, subscription_type, update_frequency):
    def to_val_or_none(val):
        if val == "None":
            return None
        else:
            return val

    params = ["instrument_name", "depth",
              "subscription_type", "update_frequency"]
    context.params = {k: to_val_or_none(locals()[k]) for k in params}

    msg = {
        "id": 1,
        "method": "subscribe",
        "params": {
            "channels": [f"book.{context.params["instrument_name"]}.{context.params["depth"]}"],
        }
    }

    if subscription_type != "None":
        msg["params"]["book_subscription_type"] = subscription_type
    if update_frequency != "None":
        msg["params"]["book_update_frequency"] = update_frequency

    context.wsapp.send(json.dumps(msg))


@then('the response fields matches the parameters if specified, else match default')
def step_then_check_resp_params(context):
    for i, msg in enumerate(context.received_msg):
        result = msg["result"]
        if context.params.get("instrument_name"):
            assert result["instrument_name"] == context.params[
                "instrument_name"], f"Response message has incorrect instrument_name: {result["instrument_name"]}. Expected: {context.params["instrument_name"]}"
        assert result["subscription"] == f"book.{context.params["instrument_name"]}.{context.params["depth"]}", f"Response message has incorrect subscription channel: {result["subscription"]}"
        if context.params["subscription_type"]:
            assert result[
                "channel"] == "book", f"Response message has incorrect : {result["channel"]}. Expected: 'book'"
        else:
            assert result[
                "channel"] == "book.update", f"Response message has incorrect : {result["channel"]}. Expected: 'book.update'"
        assert result["depth"] == int(
            context.params["depth"]), f"Response message has incorrect : {result["depth"]}. Expected: {context.params["depth"]}"

        assert len(result["data"]["asks"]) == int(
            context.params["depth"]), "asks count mismatches depth"
        assert len(result["data"]["bids"]) == int(
            context.params["depth"]), "bids count mismatches depth"


@then('I receive a subscription confirmation with code 0')
def step_then_subscription_confirmed(context):
    for i, msg in enumerate(context.received_msg):
        assert msg.get(
            "code") == 0, f"Response message with code != 0 found in message index {i} with message: {msg}"


@then('the subscription confirmation matches the subscription schema')
def step_then_subscription_confirmation_schema(context):
    for i, msg in enumerate(context.received_msg):
        try:
            if context.params["subscription_type"] == "SNAPSHOT_AND_UPDATE":
                validate(instance=msg, schema=delta_update_schema)
            else:
                validate(instance=msg, schema=snapshot_schema)
        except ValidationError as e:
            assert False, f"schema validation error: {e.message}"


@then('the response update frequency is within the specified else default interval')
def step_then_subscription_confirm_frequency(context):
    if context.params["update_frequency"]:
        update_frequency = context.params["update_frequency"]
    else:
        update_frequency = 500 if context.params.get(
            "subscription_type") == None or context.params.get("subscription_type") == "SNAPSHOT" else 10
    for i in range(1, len(context.received_msg)):
        period = context.received_msg[i]["timestamp"] - \
            context.received_msg[i-1]["timestamp"]
        period_ms = int(period * 1000)
        assert period_ms <= update_frequency, "Message was sent outside of the expected interval."


@then('the response message should consist of error code {code:d} and message "{message}"')
def step_then_verify_error_resp(context, code, message):
    for msg in context.received_msg:
        assert msg.get("code") == code
        assert msg.get("message") == message
