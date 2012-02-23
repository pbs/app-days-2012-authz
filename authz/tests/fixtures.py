TEST_CONSUMERS = [
    {"key": 'ABC', "name": "Consumer ABC", "secret": "CBA"},
    {"key": 'DEF', "name": "Consumer DEF", "secret": "FED"},
    {"key": 'XYZ', "name": "Consumer XYZ", "secret": "ZYX"}
]


TEST_POLICIES = [
    {
        "consumer_key": "XYZ",
        "rid": "rid:pbs:api:program/test-program",
        "actions": set(["get", "put"])
    },
    {
        "consumer_key": "XYZ",
        "rid": "rid:pbs:api:station/*",
        "actions": set(["get", "put", "delete"])
    },
    {
        "consumer_key": "XYZ",
        "rid": "rid:pbs:api:*/*",
        "actions": set(["get"])
    },
    {
        "consumer_key": "ABC",
        "rid": "rid:pbs:api:station/*",
        "actions": set(["get"])
    }
]
