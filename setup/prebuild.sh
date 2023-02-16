echo "Setting Project ID: ${GOOGLE_CLOUD_PROJECT}"
gcloud config set project ${GOOGLE_CLOUD_PROJECT}

echo "Enabling Cloud Storage service..."
gcloud services enable storage-component.googleapis.com 

echo "Creating cloud storage bucket..."
gcloud alpha storage buckets create gs://${GOOGLE_CLOUD_PROJECT}-seatera --project=${GOOGLE_CLOUD_PROJECT}

echo "Uploading config.yaml to cloud storage..."
gcloud alpha storage cp ./config.yaml gs://${GOOGLE_CLOUD_PROJECT}-seatera
