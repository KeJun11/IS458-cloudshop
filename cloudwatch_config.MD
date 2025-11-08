### REQUEST LATENCY FOR DB
{
    "view": "timeSeries",
    "stacked": false,
    "metrics": [
        [ "AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", "test-dev-carts", "Operation", "GetItem", { "region": "us-east-1" } ],
        [ "...", "test-dev-products", ".", ".", { "region": "us-east-1" } ],
        [ "...", "test-dev-user-interactions", ".", "Query", { "region": "us-east-1" } ],
        [ "...", "test-dev-products", ".", "Scan", { "region": "us-east-1" } ],
        [ "...", "test-dev-carts", ".", "UpdateItem", { "region": "us-east-1" } ],
        [ "...", "test-dev-orders", ".", "PutItem", { "region": "us-east-1" } ],
        [ "...", "UpdateItem", { "region": "us-east-1" } ],
        [ "...", "test-dev-carts", ".", "PutItem", { "region": "us-east-1" } ],
        [ "...", "Scan", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "period": 300
}

### SQS
{
    "metrics": [
        [ "AWS/SQS", "NumberOfMessagesSent", "QueueName", "order-processing-dev", { "region": "us-east-1" } ],
        [ ".", "NumberOfMessagesDeleted", ".", ".", { "region": "us-east-1" } ]
    ],
    "view": "timeSeries",
    "stacked": false,
    "region": "us-east-1",
    "title": "SQS",
    "period": 300,
    "stat": "Average"
}

### SES
{
    "metrics": [
        [ "AWS/SES", "Send", { "region": "us-east-1" } ]
    ],
    "view": "timeSeries",
    "stacked": false,
    "region": "us-east-1",
    "period": 300,
    "stat": "Average",
    "title": "Emails Sent"
}

### DYNAMODB
{
    "view": "timeSeries",
    "stacked": false,
    "metrics": [
        [ "AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "test-dev-carts", { "region": "us-east-1" } ],
        [ ".", "ConsumedWriteCapacityUnits", ".", "test-dev-orders", { "region": "us-east-1" } ],
        [ "...", "test-dev-products", { "region": "us-east-1" } ],
        [ ".", "ConsumedReadCapacityUnits", ".", "test-dev-user-interactions", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "title": "DynamoDB",
    "period": 300
}

### DYNAMODB ERRORS
{
    "view": "timeSeries",
    "stacked": true,
    "metrics": [
        [ "AWS/Lambda", "Errors", "FunctionName", "test-dev-create-order", "Resource", "test-dev-create-order", { "region": "us-east-1" } ],
        [ "...", "test-dev-get-products", ".", "test-dev-get-products", { "region": "us-east-1" } ],
        [ "...", "test-dev-get-recommendations", ".", "test-dev-get-recommendations", { "region": "us-east-1" } ],
        [ "...", "test-dev-manage-cart", ".", "test-dev-manage-cart", { "region": "us-east-1" } ],
        [ "...", "test-dev-process-order", ".", "test-dev-process-order", { "region": "us-east-1" } ],
        [ "...", "test-dev-track-event", ".", "test-dev-track-event", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "period": 300
}

### API INVOCATIONS
{
    "view": "timeSeries",
    "stacked": true,
    "metrics": [
        [ "AWS/Lambda", "Invocations", "FunctionName", "test-dev-create-order", "Resource", "test-dev-create-order", { "region": "us-east-1" } ],
        [ "...", "test-dev-get-products", ".", "test-dev-get-products", { "region": "us-east-1" } ],
        [ "...", "test-dev-get-recommendations", ".", "test-dev-get-recommendations", { "region": "us-east-1" } ],
        [ "...", "test-dev-manage-cart", ".", "test-dev-manage-cart", { "region": "us-east-1" } ],
        [ "...", "test-dev-process-order", ".", "test-dev-process-order", { "region": "us-east-1" } ],
        [ "...", "test-dev-track-event", ".", "test-dev-track-event", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "period": 300
}

### API REQUEST COUNT
{
    "view": "timeSeries",
    "stacked": false,
    "metrics": [
        [ "AWS/ApiGateway", "Count", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "title": "API Requests",
    "period": 300
}

### ERRORS
{
    "view": "timeSeries",
    "stacked": false,
    "metrics": [
        [ "AWS/ApiGateway", "5xx", "Stage", "$default", "ApiId", "wo2f11grj3", { "region": "us-east-1" } ]
    ],
    "region": "us-east-1",
    "title": "API Error",
    "period": 300
}
