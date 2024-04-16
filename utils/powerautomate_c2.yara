rule PowerAutomateC2_InitialFlow {
    meta:
        author = "t-tani"
        description = "Rule to detect Legacy Power Automate package created by PowerAutomate C2"
        date = "2023/11/27"

    strings:
        $a1 = "apisMap.json"
        $a2 = "connectionsMap.json"
        $a3 = "manifest.json"
        $a4 = "definition.json"
        $x1 = {e2 a0 89 e2 a0 97 e2 a0 91 e2 a0 81 e2 a0 9e e2 a0 91 e2 a0 99 e2 a0 80 e2 a0 83 e2 a0 bd e2 a0 80 e2 a0 9e e2 a0 91 e2 a0 81 e2 a0 8d e2 a0 a7}
    
    condition:
        uint16(0) == 0x4B50 and all of them
}