# インフラ
## ネットワーク
- Webフロント・バックエンド：Cloudflare Tunnel→→→Homelab (Kubernetes Cluster)

## データベース
- **MongoDB**: Kubernetes上で動作 (Namespace: `argocd-prod`)
    - Manifest: `k8s-manifests/mongodb.yaml`
    - PersistentVolumeClaim: `mongodb-pvc` (5Gi)

## Kubernetes Manifests
プロジェクトルートの `k8s-manifests/` ディレクトリで管理されています。

- `backend-api.yaml`: FastAPIバックエンドのDeployment/Service
- `backend-bot.yaml`: Discord BotのDeployment
- `frontend.yaml`: VueフロントエンドのDeployment/Service
- `mongodb.yaml`: MongoDBのDeployment/Service/PVC
- `fairy.yml`: ArgoCD Application定義
- `kustomization.yml`: Kustomize設定