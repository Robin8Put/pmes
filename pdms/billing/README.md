# billing module

This module used for upload and sale fee estimation.

- `robin8_billing`
    - `Robin8_Billig` --- class name
        - `__init__` --- init class with the configuration file.
        - `estimate_upload_fee` --- get upload fee estimation
        - `estimate_sale_fee` --- get sale fee estimation

Example of configuration file provided below.

```bash
    {
        "robin8_fee": "0.2",
        "gasLimit": "250000",
        "gasPrice": "0.00000049",
        "price_per_kilobyte": "0.01",
        ...
    }
```

More details you can find in `robin8_billing/billing` file.
