# billing module

This module used for upload and sale fee estimation.

- `robin8_billing`
    - `Robin8_Billig` --- class name
        - `__init__` --- init class with the configuration file.
        - `estimate_upload_fee` --- get fee estimation of content uploading
        - `estimate_sale_fee` --- get fee estimation of saling content
        - `estimate_change_owner_fee` --- get fee estimation of changing content owner
        - `estimate_set_access_level_fee` --- get fee estimation of setting access level
        - `estimate_set_descr_fee` --- get fee estimation of setting description

Example of configuration file provided below.

```bash
    {
		"sell_content_fee": "0.2",
		"change_owner_fee": "0.3",
		"set_access_level_fee": "0.4",
		"make_cid_fee": "0.2",
		"set_descr_fee": "0.2",
		"gasLimit": "250000",
		"gasPrice": "0.00000049",
		"price_per_kilobyte": "0.01"
    }
```

More details you can find in `robin8_billing/billing` file.
