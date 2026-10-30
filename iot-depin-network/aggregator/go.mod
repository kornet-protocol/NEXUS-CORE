module github.com/kornet-protocol/iot-depin-network

go 1.22

// Prevent go mod download from trying to fetch this private module from proxy
replace github.com/kornet-protocol/iot-depin-network => ../
