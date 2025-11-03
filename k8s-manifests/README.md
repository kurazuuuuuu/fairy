# Kubernetes Manifests for Fairy

ArgoCD用のKubernetesマニフェスト

## 構成

- `fairy.yml` - ArgoCD Application定義
- `manifests.yaml` - Deployment/Service定義
- `kustomization.yml` - Kustomize設定

## デプロイ前の準備

### 1. Secretの作成

```bash
kubectl create secret generic fairy-secrets \
  --from-literal=discord-bot-token=YOUR_DISCORD_TOKEN \
  --from-literal=gemini-api-key=YOUR_GEMINI_KEY \
  --from-literal=mongodb-uri=YOUR_MONGODB_URI \
  -n argocd-prod
```

### 2. Image Pull Secretの作成

```bash
kubectl create secret docker-registry ghcr-registry-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  -n argocd-prod
```

## ArgoCD Applicationのデプロイ

```bash
kubectl apply -f fairy.yml -n argocd
```

## コンポーネント

- **fairy-backend-api**: FastAPI (Port 8000)
- **fairy-backend-bot**: Discord Bot
- **fairy-frontend**: Vue.js + Nginx (Port 80)
