#!/usr/bin/env python3
"""
Deploy script para LLM Judge API no Kubernetes usando Helm
Baseado no processo definido em requests.ipynb
"""

import subprocess
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import json

try:
    from pyhelm3 import Client
except ImportError:
    print("❌ pyhelm3 não encontrado. Instale com: pip install pyhelm3")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    # Carrega o .env da raiz do projeto
    project_root = Path(__file__).parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"🔧 Carregado .env de: {env_path}")
    else:
        print(f"⚠️ Arquivo .env não encontrado em: {env_path}")
except ImportError:
    print("⚠️ python-dotenv não encontrado. Variáveis .env não serão carregadas automaticamente.")


class K8sDeployer:
    """Deploy automatizado para Kubernetes com Helm"""
    
    def __init__(self, k3s_server: str, registry_port: int = 30500):
        self.k3s_server = k3s_server
        self.registry_url = f"{k3s_server}:{registry_port}"
        self.image_name = "llm-judge-api"
        self.full_image = f"{self.registry_url}/{self.image_name}:latest"
        self.chart_dir = Path("deploy/helm/llm-judge-api").resolve()
        
    def run_command(self, cmd: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Executa comando shell com logging"""
        print(f"🔧 Executando: {cmd}")
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True if capture_output else None
        )
        
        if capture_output and result.stdout:
            print(f"📄 Output: {result.stdout.strip()}")
            
        return result
    
    def build_image(self, platform: str = "linux/arm64", no_cache: bool = True) -> None:
        """Build da imagem Docker"""
        print("📦 === BUILD DA IMAGEM ===")
        
        cache_flag = "--no-cache" if no_cache else ""
        dockerfile_path = "deploy/docker/Dockerfile"
        
        # Verificar se Dockerfile existe
        if not Path(dockerfile_path).exists():
            raise FileNotFoundError(f"Dockerfile não encontrado: {dockerfile_path}")
        
        cmd = f"docker buildx build {cache_flag} --platform {platform} -f {dockerfile_path} -t {self.full_image} . --load"
        
        self.run_command(cmd)
        print("✅ Build da imagem concluído\n")
    
    def push_image(self) -> None:
        """Push da imagem para registry"""
        print("📤 === PUSH PARA REGISTRY ===")
        
        cmd = f"docker push {self.full_image}"
        self.run_command(cmd)
        
        print("✅ Push para registry concluído\n")
    
    def get_api_keys(self) -> Dict[str, str]:
        """Obtém chaves de API necessárias"""
        print("🔐 === CONFIGURAÇÃO DE API KEYS ===")
        
        keys = {}
        
        # OpenRouter API Key (obrigatória)
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        if openrouter_key:
            print("✅ OPENROUTER_API_KEY encontrada no ambiente")
        else:
            print("⚠️ OPENROUTER_API_KEY não encontrada no ambiente")
            openrouter_key = input("Digite sua OPENROUTER_API_KEY (obrigatória): ").strip()
            if not openrouter_key:
                raise ValueError("OPENROUTER_API_KEY é obrigatória")
        
        keys["OPENROUTER_API_KEY"] = openrouter_key
        
        # LangSmith API Key (opcional)
        langsmith_key = os.getenv("LANGSMITH_API_KEY", "")
        if langsmith_key:
            print("✅ LANGSMITH_API_KEY encontrada no ambiente")
        else:
            print("ℹ️ LANGSMITH_API_KEY não encontrada no ambiente")
            langsmith_key = input("Digite sua LANGSMITH_API_KEY (opcional, Enter para pular): ").strip()
        
        keys["LANGSMITH_API_KEY"] = langsmith_key
        
        # Outras keys opcionais
        optional_keys = ["ANTHROPIC_API_KEY", "MISTRAL_API_KEY"]
        for key_name in optional_keys:
            key_value = os.getenv(key_name, "")
            if key_value:
                print(f"✅ {key_name} encontrada no ambiente")
            else:
                print(f"ℹ️ {key_name} não encontrada no ambiente")
                key_value = input(f"Digite sua {key_name} (opcional, Enter para pular): ").strip()
            keys[key_name] = key_value
        
        # Mostrar resumo das keys configuradas
        configured_keys = [k for k, v in keys.items() if v]
        print(f"\n📋 API Keys configuradas: {', '.join(configured_keys)}")
        
        return keys
    
    def create_helm_values(self, api_keys: Dict[str, str], host: str = "laaj.local") -> Dict[str, Any]:
        """Cria configuração de valores para Helm"""
        return {
            "env": {
                "WORKFLOW_TIMEOUT_SECONDS": "120",
                "LOG_LEVEL": "INFO",
                "LANGSMITH_PROJECT_NAME": "llm-as-judge-study",
                "LANGSMITH_TRACING": "true" if api_keys.get("LANGSMITH_API_KEY") else "false",
                "LANGSMITH_ENDPOINT": "https://api.smith.langchain.com"
            },
            "secrets": {
                key: value for key, value in api_keys.items() if value
            },
            "image": {
                "repository": f"{self.registry_url}/{self.image_name}",
                "tag": "latest",
                "pullPolicy": "Always"
            },
            "service": {
                "type": "ClusterIP",
                "port": 8000
            },
            "ingress": {
                "enabled": True,
                "className": "nginx",
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "false"
                },
                "hosts": [
                    {
                        "host": host,
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix"
                            }
                        ]
                    }
                ],
                "tls": []
            },
            "resources": {
                "limits": {"cpu": "256m", "memory": "156Mi"},
                "requests": {"cpu": "100m", "memory": "128Mi"}
            }
        }
    
    async def helm_deploy(self, values: Dict[str, Any], release_name: str = "llm-judge-api", 
                         namespace: str = "default", timeout: str = "90s") -> None:
        """Deploy via Helm"""
        print("🚀 === DEPLOY VIA HELM ===")
        
        # Verificar se chart existe
        if not self.chart_dir.exists():
            raise FileNotFoundError(f"Chart Helm não encontrado: {self.chart_dir}")
        
        # Configurar cliente Helm
        client = Client(default_timeout="300s")
        
        # Carregar chart
        chart = await client.get_chart(str(self.chart_dir))
        
        # Deploy
        print(f"📋 Release: {release_name}")
        print(f"📁 Namespace: {namespace}")
        print(f"⏱️ Timeout: {timeout}")
        
        revision = await client.install_or_upgrade_release(
            release_name,
            chart,
            values,
            namespace=namespace,
            create_namespace=True,
            wait=True,
            atomic=True,
            timeout=timeout
        )
        
        print(f"✅ Deploy Helm concluído! Revision: {revision.revision}\n")
        
    def verify_ingress(self, release_name: str = "llm-judge-api", nginx_http_port: int = 30080) -> None:
        """Verifica status do ingress e mostra URLs de acesso"""
        print("🔍 === VERIFICAÇÃO DE INGRESS ===")
        
        # Obter host do ingress
        result = self.run_command(
            f"kubectl get ingress {release_name} -o jsonpath='{{.spec.rules[0].host}}'",
            capture_output=True,
            check=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            ingress_host = result.stdout.strip()
            
            print(f"\n🌐 API disponível via Nginx Ingress:")
            print(f"   http://{self.k3s_server}:{nginx_http_port}/")
            print(f"   http://{self.k3s_server}:{nginx_http_port}/api/v1/health/")
            print(f"   http://{self.k3s_server}:{nginx_http_port}/docs")
            print(f"   Host configurado: {ingress_host}")
            
            print(f"\n🔧 Para testar com curl:")
            print(f'   curl -H "Host: {ingress_host}" http://{self.k3s_server}:{nginx_http_port}/api/v1/health/')
            
            print(f"\n💡 Configure DNS para resolver {ingress_host} → {self.k3s_server}")
            print(f"   Então acesse: http://{ingress_host}:{nginx_http_port}/")
            
        else:
            print("❌ Não foi possível obter informações do ingress")
        
        # Mostrar status do ingress
        ingress_status = self.run_command(
            f"kubectl get ingress {release_name}",
            capture_output=True,
            check=False
        )
        
        if ingress_status.returncode == 0:
            print(f"\n📊 Status do Ingress:")
            print(ingress_status.stdout)
        else:
            print("\n❌ Ingress não encontrado")
            
    def verify_pods(self, release_name: str = "llm-judge-api") -> None:
        """Verifica status dos pods"""
        print("\n🔍 === STATUS DOS PODS ===")
        
        result = self.run_command(
            f"kubectl get pods -l app.kubernetes.io/name={release_name}",
            capture_output=True,
            check=False
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Não foi possível verificar status dos pods")
    
    async def deploy_full(self, platform: str = "linux/arm64", host: str = "laaj.local", 
                         no_cache: bool = True, skip_build: bool = False) -> None:
        """Processo completo de deploy"""
        print(f"🚀 === DEPLOY COMPLETO PARA K3S ===")
        print(f"🐳 Imagem: {self.full_image}")
        print(f"🏗️  Registry: {self.registry_url}")
        print(f"🎯 Host: {host}\n")
        
        try:
            # 1. Build da imagem (se não pular)
            if not skip_build:
                self.build_image(platform=platform, no_cache=no_cache)
                self.push_image()
            else:
                print("⏭️ Pulando build da imagem\n")
            
            # 2. Configurar API keys
            api_keys = self.get_api_keys()
            
            # 3. Criar valores do Helm
            values = self.create_helm_values(api_keys, host=host)
            
            # 4. Deploy via Helm
            await self.helm_deploy(values)
            
            # 5. Verificar deploy
            self.verify_ingress()
            self.verify_pods()
            
            print("\n🎉 Deploy K3s com Nginx Ingress concluído!")
            
        except Exception as e:
            print(f"\n❌ Erro durante deploy: {e}")
            raise


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Deploy LLM Judge API no Kubernetes")
    parser.add_argument("--k3s-server", required=True, help="IP do servidor K3S")
    parser.add_argument("--registry-port", type=int, default=30500, help="Porta do registry (default: 30500)")
    parser.add_argument("--platform", default="linux/arm64", help="Plataforma Docker (default: linux/arm64)")
    parser.add_argument("--host", default="laaj.local", help="Host do ingress (default: laaj.local)")
    parser.add_argument("--no-cache", action="store_true", help="Build sem cache")
    parser.add_argument("--skip-build", action="store_true", help="Pular build da imagem")
    parser.add_argument("--nginx-port", type=int, default=30080, help="Porta do Nginx Ingress (default: 30080)")
    
    args = parser.parse_args()
    
    deployer = K8sDeployer(args.k3s_server, args.registry_port)
    
    await deployer.deploy_full(
        platform=args.platform,
        host=args.host,
        no_cache=args.no_cache,
        skip_build=args.skip_build
    )


if __name__ == "__main__":
    # Verificar se está sendo executado com uv
    if len(sys.argv) > 0 and "uv" not in sys.argv[0]:
        print("💡 Recomendado executar com: uv run deploy.py")
    
    asyncio.run(main())