# Troubleshooting

```
Error: Error reading IAM Role scatter-lambda-role: :
	status code: 404, request id:
```

This happens when terraform tries to reconcile the model from deployed
resources after localstack has been restarted. Because localstack loses
iam roles on restart the terraform state does not match the infrastructure
state and terraform fails. Run ```make clean``` from project root.

###
```
Error: error deleting S3 Bucket (work): BucketNotEmpty: The bucket you tried to delete is not empty
	status code: 409, request id: , host id:
```

This happens when a bucket contains data on deletion. Add force_destroy=true to the terraform bucket description.
