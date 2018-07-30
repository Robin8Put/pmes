
var test = {
    "message": {				            // signed json
        "post_data_to_blockchain": [
            {		            // server request handler method (create user, create profile etc.)
                "message": { // signed users json
                    "param1": "value", // method parameter: parameter value
                    "param2": "value",
                    "txid": null,
                    "error": null,
                    "response": null
                },
                "signature": "signature", // users signature
                "public_key": "public_key", // users public key
            },
            {
                "message": {
                    "param1": "value", // method parameter: parameter value
                    "param2": "value",
                    "txid": null,
                    "error": null,
                    "response": null
                },
                "signature": "signature", // users signature
                "public_key": "public_key",
            },
        ],
        "update_description": [{
            "message":			    // signed users json
                {
                    "param1": "value", // method parameter: parameter value
                    "param2": "value",
                    "txid": null,
                    "error": null,
                    "response": null
                },
                "signature": "signature", // users signature
                "public_key": "public_key",
            }
        ],
        "send": [{
            "message":{
                    "input": "address1", // sender addresses
                    "output": "address2", // receiver addresses
                    "amount": "value",
                    "coinid": "coinid",          // blockchain type
                    "txid": null, // txid will filled with response
                    "error": null,
                    "response": null
                },
                "signature": "signature", // users signature
                "public_key": "public_key", // users public key
            }
        ],
    },
    "decimal": 8,
    "signature": "signature",
    "public_key": "public key",
    "callbackURL": "some_url" // PMES backend reply send to this endpoint
}
