# ===== INSTALAÇÃO DO DOCKER =====

## Opção 1: Docker Desktop (Windows - Recomendado)

### Pré-requisitos:
- Windows 10 Pro, Enterprise ou Home (build 22000+)
- 4GB RAM mínimo
- Virtualização habilitada no BIOS

### Passos:

1. **Download**
   - Acesse: https://www.docker.com/products/docker-desktop
   - Clique em "Download for Windows"

2. **Instalação**
   - Execute o instalador
   - Marque "Install required Windows components for WSL 2"
   - Reinicie o computador se necessário

3. **Verificação**
   ```powershell
   docker --version
   docker run hello-world
   ```

### Se receber erro "Docker daemon not running":
   ```powershell
   # Abra Docker Desktop a partir do Menu Iniciar
   # Ou execute:
   & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

---

## Opção 2: WSL 2 + Docker CLI (Windows - Avançado)

```powershell
# 1. Instalar WSL 2
wsl --install

# 2. Instalar Docker no WSL 2
wsl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Iniciar Docker daemon
sudo service docker start
```

---

## Opção 3: Rodar SEM Docker (Recomendado por enquanto)

Se não deseja instalar Docker, use o método direto com Python:

```powershell
cd project-langchain

# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar aplicação
python app.py

# 3. Rodar testes
pytest tests/ -v
```

---

## Diagnóstico (Windows)

Se instalou mas não funciona:

```powershell
# Verificar se está no PATH
where docker

# Se não encontrar, adicione:
# Variáveis de Ambiente (Advanced System Settings)
# Add to PATH: C:\Program Files\Docker\Docker\resources\bin

# Reinicie PowerShell e tente:
docker --version

# Se ainda não funcionar:
# Abra Docker Desktop manualmente e tente novamente
```

---

## Próximas Etapas

Você gostaria de:

1. **Instalar Docker Desktop** - Rodar tudo em container
2. **Rodar sem Docker** - Direto com Python no seu sistema
3. **Ambos** - Uma versão local + Docker para produção

Me avise qual preferir!
