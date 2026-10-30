FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.mod ./
RUN go mod download
COPY telemetry_aggregator.go .
RUN CGO_ENABLED=0 go build -o /telemetry-aggregator ./telemetry_aggregator.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /telemetry-aggregator /usr/local/bin/telemetry-aggregator
EXPOSE 9090
CMD ["telemetry-aggregator"]
