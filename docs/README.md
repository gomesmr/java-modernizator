<p align="center" margin="20 0"><a href="https://www.stackspot.com/"> <img src="https://assets-global.website-files.com/62a0b1f9e1d99a7b7c0a6b54/62a0b1f9e1d99a3c880a6b63_StackSpot%20logo.svg" alt="logo do time" width="30%" style="max-width:100%;"/></a></p>

# Java Modernizator
[![Status do Projeto](https://img.shields.io/badge/Status-Estável-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)]()
[![StackSpot AI SDK](https://img.shields.io/badge/StackSpot_AI_SDK-latest-purple.svg)]()
[![Licença](https://img.shields.io/badge/Licença-Interna-red.svg)]()

## Sumário
1. [**Descrição do Projeto**](#descrição-do-projeto)
2. [**Como Usar e Pré-requisitos**](#como-usar-e-pré-requisitos)
3. [**Estrutura do Repositório**](#estrutura-do-repositório)
4. [**Como Executar Localmente**](#como-executar-localmente)
5. [**Como Executar com Docker**](#como-executar-com-docker)
6. [**Testes**](#testes)
7. [**Como Contribuir**](#como-contribuir)
8. [**Equipe Responsável e Contato**](#equipe-responsável-e-contato)
9. [**Referências e Links Úteis**](#referências-e-links-úteis)
10. [**Licenciamento**](#licenciamento)

---

## Descrição do Projeto

### O que é?
O Java Modernizator é uma ferramenta automatizada desenvolvida para modernizar código Java legado utilizando inteligência artificial da StackSpot. Analisa, atualiza e gera relatórios sobre arquivos Java, facilitando a evolução de projetos existentes.

### Funcionalidades Principais
- Análise automatizada de arquivos Java legados
- Modernização de código utilizando StackSpot AI
- Geração de relatórios detalhados
- Execução em lote de múltiplos arquivos
- Integração facilitada via linha de comando

### Arquitetura
O projeto segue os princípios de arquitetura definidos abaixo:
- **API**: Não expõe endpoints HTTP próprios; utiliza CLI ou como serviço interno.
- **Application**: Serviços de orquestração para modernização e geração de relatórios.
- **Domain**: Entidades e modelos do processo de modernização, como arquivos Java e resultados.
- **Infrastructure**: Integração com sistemas externos, manipulação de arquivos e requisições à StackSpot AI.

## Como Usar e Pré-requisitos

### Pré-requisitos
Para utilizar e desenvolver neste projeto, você precisará de:

#### Software Necessário
- **Python 3.7+**
- **IDE** de sua preferência:
  - VSCode
  - PyCharm
  - Sublime Text

#### Acessos Necessários
Solicite os seguintes acessos via [IU Acessos](https://acessos.seusistema.com/):
- Grupo de acesso ao repositório
- Permissão para instalação de dependências Python

#### Credenciais de API
1. Configure credenciais StackSpot no arquivo `secrets.json` na raiz do projeto:
```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "realm": "zup"
}
```

## Estrutura do Repositório

```
.
├── application/
│   ├── modernization_service.py
│   └── report_generator.py
├── domain/
│   ├── entities.py
│   └── exceptions.py
├── infrastructure/
│   ├── file_system.py
│   └── stackspot_client.py
├── config/
│   └── settings.py
├── assets/
│   ├── main-paths.txt
│   └── tests-paths.txt
├── main.py
├── requirements.txt
├── README.md
├── setup.py
├── secrets-example.json
```

## Como Executar Localmente

### Configuração Inicial
1. **Clone o repositório**
```bash
git clone https://github.com/suaempresa/java-modernizator.git
cd java-modernizator
```
2. **Instale as dependências**
```bash
pip install -r requirements.txt
```
3. **Configure o arquivo `secrets.json` na raiz (ver exemplo acima).**

### Executando a Aplicação

```bash
# (Opcional) Validar setup do projeto
python setup.py

# Executar o modernizador
python main.py
```

A aplicação será executada em modo CLI.

## Como Executar com Docker

Nenhum arquivo Docker foi identificado neste repositório.

## Testes

Não foram identificados scripts ou diretórios específicos para testes automáticos ou manuais no repositório entregue.

## Como Contribuir

Para contribuir com o projeto:
1. Faça um fork do repositório.
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -am 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

### Diretrizes de Contribuição
- Siga os padrões de código do projeto.
- Atualize a documentação conforme necessário.
- Certifique-se de que todas as funcionalidades estejam testadas antes de enviar o PR.

Para dúvidas, entre em contato pelo e-mail: **modernizator@suasquad.com**

## Equipe Responsável e Contato

### Squad Responsável
**Squad Modernização**

### Contatos
- **E-mail da Equipe**: modernizator@suasquad.com
- **Documentação Oficial**: [Portal de Documentação](https://docs.suaempresa.com/java-modernizator)

### Suporte
1. Abra uma issue no repositório.
2. Entre em contato por e-mail.
3. Consulte a documentação oficial.

## Referências e Links Úteis

### Documentação Técnica e Recursos

- [StackSpot AI SDK Documentation](https://pypi.org/project/stackspot/)
- [Python Official Docs](https://docs.python.org/3/)
- [Portal de Credenciais](https://credenciais.suaempresa.com/)
- [IU Acessos](https://acessos.seusistema.com/)

## Licenciamento

Este projeto é de **uso exclusivamente interno** da SuaEmpresa. Todos os direitos reservados.  
**Licença**: Propriedade intelectual da SuaEmpresa - Uso interno apenas.

---

**Status do Projeto**: 🚀 Estável  
*Última atualização: 2024-06*