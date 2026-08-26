# 🔑 Configuração Kaggle API - Guia Completo

## 📋 O que é Kaggle API?

A Kaggle API permite baixar datasets diretamente da linha de comando, sem precisar usar o navegador. Essencial para automatizar o download de dados do projeto.

---

## 🚀 Passo a Passo: Obter Token Kaggle

### 1️⃣ Criar Conta Kaggle (se ainda não tiver)

1. Acesse: https://www.kaggle.com/
2. Clique em **"Sign Up"** (canto superior direito)
3. Preencha o formulário com seus dados
4. Confirme seu email

**Alternativa:** Entrar com Google, GitHub ou Apple

---

### 2️⃣ Gerar Token API

**Importante:** Você precisa estar logado no Kaggle!

#### No Computador:

1. Acesse: https://www.kaggle.com/settings/account
2. Role até encontrar a seção **"API"**
3. Clique em **"Create New API Token"**

   ![Criar Token](./token_creation.png)

4. Um arquivo `kaggle.json` será **baixado automaticamente**

   ```json
   {
     "username": "seu_usuario_kaggle",
     "key": "abc123xyz456..."
   }
   ```

---

### 3️⃣ Configurar no Computador

#### macOS / Linux:

```bash
# 1. Criar pasta .kaggle (se não existir)
mkdir -p ~/.kaggle

# 2. Copiar o arquivo baixado
cp ~/Downloads/kaggle.json ~/.kaggle/

# 3. Definir permissões (IMPORTANTE!)
chmod 600 ~/.kaggle/kaggle.json

# 4. Verificar
cat ~/.kaggle/kaggle.json
```

#### Windows (PowerShell):

```powershell
# 1. Criar pasta
mkdir $env:USERPROFILE\.kaggle

# 2. Copiar arquivo
Copy-Item $env:USERPROFILE\Downloads\kaggle.json -Destination $env:USERPROFILE\.kaggle\

# 3. Verificar
type $env:USERPROFILE\.kaggle\kaggle.json
```

---

## ✅ Verificar Configuração

### Testar autenticação:

```bash
kaggle datasets list | head -5
```

**Saída esperada:**
```
Dataset Title                          Size    Downloads  Votes
───────────────────────────────────────────────────────────────
Bank Marketing                         400 KB  5000       150
Customer Churn Prediction               2 MB   3000       120
...
```

Se não funcionar, execute:

```bash
# Instalar/atualizar Kaggle CLI
pip install --upgrade kaggle

# Verificar instalação
kaggle --version
```

---

## 💾 Estrutura do Arquivo `kaggle.json`

```json
{
  "username": "seu_usuario_kaggle",
  "key": "sua_chave_api_secreta_aqui"
}
```

### Campos:

- **username**: Seu nome de usuário no Kaggle
  - Encontra em: https://www.kaggle.com/settings/account
  - Exemplo: `vagnerasilva`

- **key**: Sua chave API
  - Gerada automaticamente no passo 2️⃣
  - Parece com: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## 🔒 Segurança - IMPORTANTE!

### ⚠️ NUNCA faça isso:

```bash
❌ git add .kaggle/kaggle.json
❌ Compartilhar o arquivo com outros
❌ Colocar a chave em código público
❌ Fazer commit do arquivo
```

### ✅ Verificar se está seguro:

```bash
# Ver permissões do arquivo
ls -la ~/.kaggle/kaggle.json
# Esperado: -rw------- (600)

# Ver conteúdo (APENAS LOCALMENTE)
cat ~/.kaggle/kaggle.json
```

### 🛡️ Se comprometer a chave:

1. Acesse: https://www.kaggle.com/settings/account
2. Clique em **"Create New API Token"** (invalida o anterior)
3. Siga os passos 3️⃣ novamente

---

## 📥 Usar no Projeto

### Baixar um dataset:

```bash
kaggle datasets download -d usuario/dataset-name -p data/raw/
```

### Baixar arquivo específico:

```bash
kaggle datasets download -d usuario/dataset-name --unzip -p data/raw/
```

### Listar seus datasets:

```bash
kaggle datasets list -s "bank"
```

---

## 🐛 Troubleshooting

### Erro: "Credentials not found"

```
❌ OSError: Could not find kaggle.json. Make sure it's located in...
```

**Solução:**
```bash
# Verificar localização
ls ~/.kaggle/kaggle.json

# Se não existir, repetir passo 3️⃣
```

---

### Erro: "Permission denied"

```
❌ PermissionError: [Errno 13] Permission denied
```

**Solução:**
```bash
# Corrigir permissões
chmod 600 ~/.kaggle/kaggle.json
```

---

### Erro: "Command not found: kaggle"

```
❌ kaggle: command not found
```

**Solução:**
```bash
# Instalar Kaggle CLI
pip install kaggle

# Verificar instalação
kaggle --version
```

---

## 📚 Recursos Úteis

- **Kaggle Settings**: https://www.kaggle.com/settings/account
- **Kaggle Datasets**: https://www.kaggle.com/datasets
- **Kaggle CLI Docs**: https://github.com/Kaggle/kaggle-api

---

## 🎯 No Contexto do Projeto

Este projeto usa a Kaggle API para baixar automaticamente **4 bases de dados** de marketing bancário:

```bash
# O notebook faz isso automaticamente:
cd notebooks/
jupyter notebook 01_EDA.ipynb

# Célula 4️⃣: Executa downloads com cache
# Se kaggle.json estiver configurado, baixa os dados
# Se não estiver, mostra mensagem de erro com link para download manual
```

---

## ✅ Checklist de Configuração

- [ ] Conta Kaggle criada
- [ ] Acessei: https://www.kaggle.com/settings/account
- [ ] Criei novo token API
- [ ] Arquivo `kaggle.json` baixado
- [ ] Copiei para `~/.kaggle/kaggle.json`
- [ ] Defini permissões: `chmod 600`
- [ ] Testei: `kaggle datasets list`
- [ ] Pronto para usar o projeto!

---

**Dúvidas?** Consulte a [documentação oficial](https://github.com/Kaggle/kaggle-api) ou nosso README.md

