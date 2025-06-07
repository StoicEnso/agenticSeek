# Azure DeepSeek R1 Integration with AgenticSeek

## Prerequisites

1. Azure subscription with access to Azure AI Foundry
2. AgenticSeek installed and working
3. Python environment with required packages

## Step 1: Deploy DeepSeek R1 in Azure AI Foundry

### Enable Azure AI Inference Service (Required!)

1. Go to [Azure AI Foundry portal](https://ai.azure.com)
2. Click the **Preview features** icon in the top navigation bar
3. Turn on **"Deploy models to Azure AI model inference service"** feature
4. Close the panel

### Deploy DeepSeek R1 Model

1. Go to **Model catalog** section
2. Search for "DeepSeek-R1" 
3. Click on the model card
4. Click **Deploy**
5. Accept terms and conditions
6. **Important**: Choose **"Azure AI Inference Service"** deployment type (not serverless)
7. Give your deployment a name (e.g., "deepseek-r1-deployment")
8. Click **Deploy**

### Get Your Endpoint Details

After deployment completes:

1. Go to your deployment page
2. Copy the **Target URI** - it should look like:
   ```
   https://YOUR-RESOURCE-NAME.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview
   ```
3. Copy your **API Key**

## Step 2: Configure the Azure Proxy

### Update azure_server_adapterv2.py

Edit the configuration block in `azure_server_adapterv2.py`:

```python
# ─────────────── EDIT ONLY THIS BLOCK ───────────────
AZURE_ENDPOINT = "https://YOUR-RESOURCE-NAME.services.ai.azure.com"  # Your Azure AI Foundry endpoint (without /models suffix)
AZURE_KEY      = "YOUR_ACTUAL_API_KEY_HERE"  # Your API key from Azure
MODEL_NAME     = "DeepSeek-R1"  # Use the deployment name you chose
# ─────────────────────────────────────────────────────
```

**Important Notes:**
- Remove `/models/chat/completions?api-version=2024-05-01-preview` from the endpoint URL
- Use just the base URL: `https://YOUR-RESOURCE-NAME.services.ai.azure.com`
- Replace `YOUR-RESOURCE-NAME` with your actual Azure resource name
- Use `DeepSeek-R1` as the model name (this is the deployment name)

## Step 3: Install Dependencies

```bash
pip install azure-ai-inference fastapi uvicorn
```

## Step 4: Start the Azure Proxy Server

```bash
cd /path/to/your/agenticSeek
python azure_server_adapterv2.py
```

You should see:
```
Starting Azure DeepSeek-R1 proxy server...
Azure Endpoint: https://YOUR-RESOURCE-NAME.services.ai.azure.com
Model: DeepSeek-R1
Listening on: http://0.0.0.0:3333
```

## Step 5: Configure AgenticSeek

Your `config.ini` should already be configured correctly:

```ini
[MAIN]
is_local = False
provider_name = server
provider_model = DeepSeek-R1
provider_server_address = http://127.0.0.1:3333
# ... other settings
```

## Step 6: Test the Integration

### Test the proxy directly:

```bash
curl -X POST "http://127.0.0.1:3333/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 100
  }'
```

### Test with AgenticSeek:

```bash
python cli.py
```

Then ask a simple question like "Hello, how are you?"

## Troubleshooting

### Common Issues:

1. **"400 - Content has no body" error**
   - Make sure you enabled "Azure AI Inference Service" preview feature
   - Verify you deployed to Azure AI Inference Service, not serverless

2. **"URL can not be found" error**
   - Check your endpoint URL format
   - Ensure you're using the base URL without `/models/chat/completions`
   - Verify your Azure resource name is correct

3. **"413 Request body too large" error**
   - This happens with serverless deployments
   - Redeploy using Azure AI Inference Service instead

4. **Authentication errors**
   - Verify your API key is correct
   - Check that your Azure subscription has access to the model

### Verification Steps:

1. **Check Azure deployment status:**
   - Go to Azure AI Foundry → Models + endpoints
   - Verify your deployment shows as "Succeeded"
   - Note the exact Target URI format

2. **Test Azure endpoint directly:**
   ```bash
   curl -X POST "https://YOUR-RESOURCE-NAME.services.ai.azure.com/models/chat/completions?api-version=2024-05-01-preview" \
     -H "api-key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"role": "user", "content": "Hello"}],
       "model": "DeepSeek-R1"
     }'
   ```

3. **Check proxy health:**
   ```bash
   curl http://127.0.0.1:3333/health
   ```

## Expected Behavior

When working correctly:

1. AgenticSeek sends requests to the proxy at `http://127.0.0.1:3333`
2. Proxy forwards requests to Azure AI Foundry
3. Azure returns DeepSeek R1 responses with `<think>` reasoning blocks
4. Proxy extracts the final answer and returns it to AgenticSeek
5. AgenticSeek displays the response

## Performance Notes

- DeepSeek R1 is a reasoning model and may take longer to respond
- The model generates both reasoning (`<think>` blocks) and final answers
- Reasoning content counts toward token usage and costs
- Consider using distilled versions for faster responses if available

## Support

If you continue having issues:

1. Check the Azure AI Foundry documentation
2. Verify your Azure subscription has the necessary permissions
3. Ensure you're using the latest version of the Azure AI Inference SDK
4. Check Azure service status for any outages 