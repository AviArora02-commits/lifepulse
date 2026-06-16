param(
  [Parameter(Mandatory=$true)]
  [string]$SpaceId
)

if (-not (Get-Command hf -ErrorAction SilentlyContinue)) {
  throw "Install the Hugging Face CLI first: pip install -U huggingface_hub[cli]"
}

Copy-Item -LiteralPath "SPACE_README.md" -Destination "README.md" -Force
hf repos create $SpaceId --type space --space-sdk docker --exist-ok
hf upload $SpaceId . --type space --exclude ".git/*" --exclude "frontend/node_modules/*" --exclude "backend/__pycache__/*" --exclude "generated_documents/*" --commit-message "Deploy LifePulse demo"
