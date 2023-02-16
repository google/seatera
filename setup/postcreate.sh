echo "Setting bucket env variable.." 
gcloud run services update seatera --update-env-vars bucket_name=${GOOGLE_CLOUD_PROJECT}-seatera --region=${GOOGLE_CLOUD_REGION}
