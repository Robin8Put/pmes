# Robin8 BlockChain MAIL API

This API provides access to information of Robin8 mailing module.

The API uses the [JSON RPC 2.0](http://www.jsonrpc.org/specification).

API-methods:

- [Send mail](#send-mail)

- [Set mail template](#set-mail-template)

The following is a description of the API-methods:

## Send mail

* **Method:** `sendmail`
  
* **Params**

    `tmp_name=[string]` - template name

    `**array=[dictionary]`

    **Required** `array` fields:

    - from
    - to
    - subject

    **Optional**: other parameters needed for the template

* **Sample response**

    None 


## Set mail template

* **Method:** `settemplate`
  
* **Params**

    `name=[string]` - template name

    `body=[JSON]` - other parameters needed for the template

* **Sample response**

    None
