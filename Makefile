image="minigolf:latest"
azure_image="meineappregistry.azurecr.io/minigolf:v1"

build:
	docker build --rm -t $(image) .
build_azure:
	docker build --platform linux/amd64 --rm -t $(image) .

tag: build_azure
	docker tag $(image) $(azure_image) 

run: build
	docker run -it --rm -p 8000:8000 $(image)


azure_login:
	az login

#acr: #azure_login
#        az group create --name meine-app-gruppe --location germanywestcentral

#registry: acr
#        az acr create \
#          --resource-group meine-app-gruppe \
#          --name meineappregistry \
#          --sku Basic \
#          --admin-enabled true

acr_login: #registry
	az acr login --name meineappregistry

push: tag
	docker push $(azure_image)

create_env: #registry
	az containerapp env create \
	  --name meine-app-env \
	  --resource-group meine-app-gruppe \
	  --location germanywestcentral

ACR_PASSWORD="51vMHmbfIHkcKMfbiUaBq71vSG1wsIm5oVqChA9omieV2ouITxGZJQQJ99CCACPV0roEqg7NAAACAZCRVZN7"
deploy: create_env
	az containerapp create \
	  --name meine-minigolf-app \
	  --resource-group meine-app-gruppe \
	  --environment meine-app-env \
	  --image $(azure_image) \
	  --target-port 8000 \
	  --ingress external \
	  --registry-server meineappregistry.azurecr.io \
	  --registry-username meineappregistry \
	  --registry-password $(ACR_PASSWORD) \
	  --cpu 0.5 --memory 1.0Gi

get_url:
	az containerapp show \
	  --name meine-minigolf-app \
	  --resource-group meine-app-gruppe \
	  --query "properties.configuration.ingress.fqdn" -o tsv
clean_up:
