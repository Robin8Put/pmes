pragma solidity ^0.4.21;
contract Robin8 {

    // contract owner address: high accessLevel always
    address owner;

    // CID will take the values 1,2,3,...
    uint32 nextCID = 1;
    
    struct CUSandOwner {
        string CUS;
        address Owner;
    }
    
    // CID => CUSandOwner
    mapping(uint32 => CUSandOwner) CIDtoCUSandOwner;

    // CID => price
    mapping(uint32 => uint) CIDtoPrice;

    // CUS-hash => CID
    mapping(string => uint32) CUStoCID;
    
    // CID => description
    mapping(uint32 => string) public CIDtoDescription;

    // Access level mapping [address]
    // 0 - access denied
    // 1 - can setCIDdescr
    // 2 - can makeCID
    // 3 - can saleAccess
    // 4 - can changeOwner
    // 5 - can setAccessLevel
    mapping(address => uint8) public publishersMap;

    // last accessString for each CID
    mapping(uint32 => string) public lastAccessString;

    // when new CID created
    event newCID(uint32 CID, string CUS, string description, uint price);

    // when set new access level to publishersMap
    event newAccessLevel(address addr, uint8 level);

    // when set new description
    event newCIDdescription(address addr, uint32 CID, string description);

    // when set new owner for CID
    event newOwnerForCID(address addr, uint32 CID, string accessString);

    // when buyer wants to buy content
    event newOffer(address addr, uint32 CID, uint offerPrice, string buyerAccessString);

    // when seller accepts offer and sells content
    event saleAccessForCID(address addr, uint32 CID, string sellerAccessString);

    // when seller rejects offer
    event offerRejected(address addr, uint32 CID);

    /**
     * This function is called once when deploy a smart contract
     */
    constructor() public
    {
        // to prevent repeated calls
        require (owner == 0);
        // set owner address
        owner = msg.sender;
    }

    /**
     * Set Access Level for specified address
     *
     * @param publisherAddr for which the accessLevel is set
     * @param accessLevel 0-deny, 1-descr.only, 2-makeCID, 3-for call this function
     */
    function setAccessLevel(
        address publisherAddr,
        uint8 accessLevel
    )
        public
        minAccessLevel(5)
    {
        publishersMap[publisherAddr] = accessLevel;

        emit newAccessLevel(publisherAddr, accessLevel);
    }

    /**
     * @param CUS Content Unical String
     */
    function makeCID(
        string CUS,
        address OwnerID,
        string description,
        uint price
    )
        public
        minAccessLevel(2)
        returns (uint32)
    {
        // To prevent create already exist
        uint32 CID = CUStoCID[CUS];
        require(CID == 0);

        CID = nextCID++;
        CUStoCID[CUS] = CID;
        CIDtoCUSandOwner[CID] = CUSandOwner(CUS, OwnerID);

        CIDtoDescription[CID] = description;
        CIDtoPrice[CID] = price;

        emit newCID(CID, CUS, description, price);

        return CID;
    }

    function setPrice(
        uint32 cid,
        uint price
    )
        public
        minAccessLevel(3)
    {
        require(cid > 0 && cid < nextCID);
        CIDtoPrice[cid] = price;
    }

    function getPrice(
        uint32 cid
    )
        public
        constant
        returns(uint)
    {
        return CIDtoPrice[cid];
    }

    /**
     * Getter CID by CUS
     *
     * @param CUS Content Unical String
     */
    function getCID(
        string CUS
    )
        public
        constant
        returns (uint32)
    {
        return CUStoCID[CUS];
    }

    function getCUS(
        uint32 CID
    )
        public
        constant
        returns (string)
    {
        return CIDtoCUSandOwner[CID].CUS;
    }

    function getOwner(
        uint32 CID
    )
        public
        constant
        returns (address)
    {
        return CIDtoCUSandOwner[CID].Owner;
    }

    /**
     * Description setter
     */
    function setCIDdescription(
        uint32 CID,
        string description
    )
        public
        minAccessLevel(1)
    {
        require(CID > 0 && CID < nextCID);

        CIDtoDescription[CID] = description;

        emit newCIDdescription(msg.sender, CID, description);
    }

    function changeOwner(
        uint32 CID,
        address newOwnerID,
        string accessString
    )
        public
        minAccessLevel(4)
    {
        // require(msg.sender == CIDtoCUSandOwner[CID].Owner);
        lastAccessString[CID] = accessString;
        CIDtoCUSandOwner[CID].Owner = newOwnerID;

        emit newOwnerForCID(newOwnerID, CID, accessString);
    }

    function sellContent(
        uint32 CID,
        address buyerID,
        string accessString

    )
        public
        minAccessLevel(3)
    {
        // require(msg.sender == CIDtoCUSandOwner[CID].Owner);
        lastAccessString[CID] = accessString;

        emit saleAccessForCID(buyerID, CID, accessString);
    }
    function makeOffer(
        uint32 CID,
        address buyerID,
        uint price,
        string buyerAccessString // buyer_access_string for asymetric encryption
    )
    public
    minAccessLevel(3)
    {
        emit newOffer(buyerID, CID, price, buyerAccessString);
    }

    function rejectOffer(
        uint32 CID,
        address buyerID
    )
    public
    minAccessLevel(3)
    {
        emit offerRejected(buyerID, CID);
    }


    modifier minAccessLevel(uint8 level) {
        if(msg.sender != owner) {
            require(publishersMap[msg.sender] >= level);
        }
        _;
    }
}
