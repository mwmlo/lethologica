#!/bin/sh
az login --service-principal -u $AZURE_APP_ID -p $AZURE_PASSWORD --tenant $AZURE_TENANT
az extension add --name containerapp --upgrade

# Deploy container app
az containerapp up --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --environment $APP_ENV --target-port $TARGET_PORT --ingress external --image $CI_REGISTRY_IMAGE

# Set secrets
az containerapp secret set --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --secrets api-key-prod=$API_KEY_PROD api-key-test=$API_KEY_TEST

# Update container app with secrets
az containerapp update --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --set-env-vars API_KEY_PROD=secretref:api-key-prod API_KEY_TEST=secretref:api-key-test
