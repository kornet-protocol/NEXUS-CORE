package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func testPacket() TelemetryPacket {
	return TelemetryPacket{
		NodeID:      "node-1",
		Timestamp:   time.Now().Unix(),
		PayloadHash: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
		Signature:   "signature",
		DataType:    "air_quality",
	}
}

func TestIngestRejectsMalformedPackets(t *testing.T) {
	aggregator := NewAggregator("http://validator.invalid")
	if err := aggregator.Ingest(TelemetryPacket{NodeID: "node-1"}); err == nil {
		t.Fatal("Ingest() error = nil, want validation error")
	}
	if pending := aggregator.Stats()["pending"]; pending != 0 {
		t.Fatalf("pending = %d, want 0", pending)
	}
}

func TestFlushToValidatorRemovesDeliveredPackets(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			t.Errorf("method = %s, want POST", request.Method)
		}
		writer.WriteHeader(http.StatusAccepted)
	}))
	defer server.Close()

	aggregator := NewAggregator(server.URL)
	aggregator.Ingest(testPacket())
	if err := aggregator.FlushToValidator(); err != nil {
		t.Fatalf("FlushToValidator() error = %v", err)
	}
	if pending := aggregator.Stats()["pending"]; pending != 0 {
		t.Fatalf("pending = %d, want 0", pending)
	}
}

func TestFlushToValidatorKeepsPacketsOnFailure(t *testing.T) {
	aggregator := NewAggregator("http://127.0.0.1:1/unreachable")
	aggregator.Ingest(testPacket())
	if err := aggregator.FlushToValidator(); err == nil {
		t.Fatal("FlushToValidator() error = nil, want delivery error")
	}
	if pending := aggregator.Stats()["pending"]; pending != 1 {
		t.Fatalf("pending = %d, want 1", pending)
	}
}
