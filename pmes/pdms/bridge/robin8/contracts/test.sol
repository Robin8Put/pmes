pragma solidity ^0.4.23;

contract Test {
    
    uint num;
    string str;
    
    function Test(uint a, string b) {
        num = a;
        str = b;
    }
    
    function get_num() returns (uint) {
        return num;
    }
    
    function get_str() returns (string) {
        return str;
    }
    
    function get_all() returns (uint, string) {
        return (num, str);
    }
    
    function add_num(uint a) returns (uint) {
        return num + a;
    }
    
    function set_num(uint a) returns (uint) {
	uint old = num;	
	num = a;
	return old;
    }
    
    function set_str(string s) returns (string) {
	string old = str;
	str = s;
	return old;
    }
}
