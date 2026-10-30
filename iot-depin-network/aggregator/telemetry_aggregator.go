// =====================================================================
// NEXUS KORNET ENGINE: Telemetry Aggregator HTTP Server (Go)
// =====================================================================

package main

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"
)

type TelemetryPacket struct {
	NodeID      string `json:"node_id"`
	Timestamp   int64  `json:"timestamp"`
	PayloadHash string `json:"payload_hash"`
	Signature   string `json:"signature"`
	DataType    string `json:"data_type"`
}

type Aggregator struct {
	mu                sync.Mutex
	packets           []TelemetryPacket
	validatorEndpoint string
	httpClient        *http.Client
}

func NewAggregator(endpoint string) *Aggregator {
	return &Aggregator{
		packets:           make([]TelemetryPacket, 0),
		validatorEndpoint: endpoint,
		httpClient:        &http.Client{Timeout: 10 * time.Second},
	}
}

func (a *Aggregator) Ingest(pkt TelemetryPacket) error {
	if err := validatePacket(pkt); err != nil {
		return err
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	a.packets = append(a.packets, pkt)
	return nil
}

func validatePacket(pkt TelemetryPacket) error {
	if pkt.NodeID == "" {
		return fmt.Errorf("node id is required")
	}
	if pkt.Timestamp <= 0 || pkt.Timestamp > time.Now().Add(5*time.Minute).Unix() {
		return fmt.Errorf("timestamp is outside the accepted window")
	}
	if len(pkt.PayloadHash) != 64 {
		return fmt.Errorf("payload hash must be a SHA-256 hex string")
	}
	if _, err := hex.DecodeString(pkt.PayloadHash); err != nil {
		return fmt.Errorf("payload hash is not valid hex: %w", err)
	}
	if pkt.Signature == "" {
		return fmt.Errorf("signature is required")
	}
	if pkt.DataType == "" {
		return fmt.Errorf("data type is required")
	}
	return nil
}

func (a *Aggregator) FlushToValidator() error {
	a.mu.Lock()
	if len(a.packets) == 0 {
		a.mu.Unlock()
		return nil
	}
	packets := append([]TelemetryPacket(nil), a.packets...)
	a.mu.Unlock()

	payload, err := json.Marshal(packets)
	if err != nil {
		return fmt.Errorf("marshal telemetry: %w", err)
	}
	req, err := http.NewRequest(http.MethodPost, a.validatorEndpoint, bytes.NewReader(payload))
	if err != nil {
		return fmt.Errorf("create validator request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := a.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("send telemetry: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
		return fmt.Errorf("validator returned status %s", resp.Status)
	}

	a.mu.Lock()
	if len(a.packets) >= len(packets) {
		a.packets = a.packets[len(packets):]
	}
	a.mu.Unlock()
	fmt.Printf("Flushed %d packets to %s at %s\n", len(packets), a.validatorEndpoint, time.Now().Format(time.RFC3339))
	return nil
}

func (a *Aggregator) Stats() map[string]int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return map[string]int{"pending": len(a.packets)}
}

func (a *Aggregator) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		if r.URL.Path == "/stats" {
			stats := a.Stats()
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(stats)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	case http.MethodPost:
		if r.URL.Path == "/ingest" {
			var pkt TelemetryPacket
			if err := json.NewDecoder(r.Body).Decode(&pkt); err != nil {
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
				return
			}
			if err := a.Ingest(pkt); err != nil {
				w.WriteHeader(http.StatusBadRequest)
				json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
				return
			}
			w.WriteHeader(http.StatusAccepted)
			json.NewEncoder(w).Encode(map[string]string{"status": "accepted"})
			return
		}
		if r.URL.Path == "/flush" {
			if err := a.FlushToValidator(); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
				return
			}
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(map[string]string{"status": "flushed"})
			return
		}
		w.WriteHeader(http.StatusNotFound)
	default:
		w.WriteHeader(http.StatusMethodNotAllowed)
	}
}

func main() {
	endpoint := os.Getenv("VALIDATOR_ENDPOINT")
	if endpoint == "" {
		endpoint = "http://validator:8080/validate"
	}
	agg := NewAggregator(endpoint)

	mux := http.NewServeMux()
	mux.Handle("/", agg)
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
	})

	server := &http.Server{Addr: ":9090", Handler: mux}

	go func() {
		fmt.Println("Telemetry Aggregator listening on :9090")
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			fmt.Fprintf(os.Stderr, "server error: %v\n", err)
			os.Exit(1)
		}
	}()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	<-sigCh
	fmt.Println("Shutting down...")
	server.Close()
}
