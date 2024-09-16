# Currency Tracking Service
The Currency Tracking Service relies on European Central Bank Data (https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html). Exchange rates are fetched every working day and stored in the database.

## Resources Used

- AWS Lambda
- AWS SQS
- AWS API GATEWAY
- AWS DynamoDB
- AWS Cloudwatch Event
- AWS SNS

## Arch Diagram
![alt text](https://github.com/NarendrenSaravanan/currency-tracker/blob/main/arch_diagram.png?raw=true)


## Installation Steps for local development

### Installing Serverless and deps
```
npm install -g serverless
npm install
```
### Deploy Code
```
sls deploy
```
Note: Configure your credentials in AWS cli as default

### Future Use cases
1. Add authentication to Api gateway deployment
2. Add Cleanup logic to remove older currency data stored in DynamoDB
3. Add SES integration on SNS side to get realtime notifications in case of failures