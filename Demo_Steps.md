### Pre Setup steps
- [ ] Open up dynamo DB
- [ ] Open SQS
- [ ] Open Invoice S3
- [ ] Launch terraform (backend, frontend (rmb to change .env), upload seed data product)
- [ ] Run Tail logs lambda service 

### Lambda service cmds
1a) aws logs tail /aws/lambda/test-dev-track-event --follow --format short
1b) aws logs tail /aws/lambda/test-dev-create-order --follow --format short
2) aws logs tail /aws/lambda/test-dev-process-order --follow --format short

## Flow
1. Showcase user tracker and recommendation system first (refer to lambda for tracker events)
2. Add 3 products electronic, fashion and sports, add to cart (Show the cart DynamoDB)
3. Fill in the correct email, click order
4. Say how `create_order` leads to `order_process` point at lambda service
5. Open up order DynamoDB and SQS monitoring to show the logs
6. Say order_process triggers 3 events
  - External payment (see console log)
  - Create Invoice (See S3)
  - Send email notif to madeinzhongguo123@gmail.com
7. End Demo