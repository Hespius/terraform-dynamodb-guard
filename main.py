import os
import hcl2
import subprocess

# Função para executar o terraform plan e capturar a saída
def run_terraform_plan():
    try:
        result = subprocess.run(['terraform', 'plan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar terraform plan: {e}")
        return ""

# Função para fazer o parse de arquivos Terraform e verificar aws_dynamodb_table
def parse_terraform_file(filepath):
    with open(filepath, 'r') as file:
        try:
            data = hcl2.load(file)
            # Verifica se o recurso aws_dynamodb_table está presente
            if 'resource' in data:
                for resource_type, resources in data['resource'].items():
                    if resource_type == 'aws_dynamodb_table':
                        return True
            # Verifica se há módulos referenciados
            if 'module' in data:
                return check_module_for_dynamodb(data['module'])
        except Exception as e:
            print(f"Erro ao processar o arquivo {filepath}: {e}")
    return False

# Função para verificar se algum módulo referenciado cria um aws_dynamodb_table
def check_module_for_dynamodb(modules):
    for module in modules:
        # Se o módulo for remoto (ex: no GitHub), vamos clonar e analisar
        if 'source' in modules[module] and modules[module]['source'].startswith('git::'):
            print(f"Módulo remoto encontrado: {modules[module]['source']}")
            return check_remote_module_for_dynamodb(modules[module]['source'])
        # Se o módulo for local, procuramos no diretório
        else:
            print(f"Módulo local encontrado: {module}")
            return search_in_terraform_files(module)
    return False

# Função para verificar se algum módulo remoto contém aws_dynamodb_table
def check_remote_module_for_dynamodb(module_source):
    module_dir = "/tmp/terraform_module"
    # Clona o repositório Git do módulo remoto
    try:
        subprocess.run(['git', 'clone', module_source, module_dir], check=True)
        # Verifica arquivos .tf no módulo clonado
        for file in os.listdir(module_dir):
            if file.endswith('.tf'):
                if parse_terraform_file(os.path.join(module_dir, file)):
                    return True
    except Exception as e:
        print(f"Erro ao clonar o módulo remoto {module_source}: {e}")
    return False

# Função para buscar nos arquivos .tf os módulos ou recursos que criam uma tabela DynamoDB
def search_in_terraform_files(module_name=None):
    terraform_files = [f for f in os.listdir('.') if f.endswith('.tf')]
    for file in terraform_files:
        with open(file, 'r') as f:
            content = f.read()
            if module_name and module_name in content:
                if parse_terraform_file(file):
                    print(f"Módulo {module_name} em {file} tenta criar uma tabela DynamoDB.")
                    return True
            elif parse_terraform_file(file):
                print(f"Recurso DynamoDB encontrado no arquivo {file}.")
                return True
    return False

# Função principal para verificar todos os arquivos e módulos
def check_all_files_for_dynamodb():
    print("Executando terraform plan...")
    plan_output = run_terraform_plan()

    if 'aws_dynamodb_table' in plan_output:
        print("Recursos aws_dynamodb_table encontrados no plano:\n")
        
        # Encontrar e analisar módulos ou recursos do plano
        lines = plan_output.splitlines()
        for line in lines:
            if 'aws_dynamodb_table' in line:
                print(f"  - {line.strip()}")
                if 'module.' in line:
                    module_name = line.split('.')[1]  # Exemplo: module.example_module
                    print(f"  -> Verificando o módulo: {module_name}")
                    files = search_in_terraform_files(module_name)
                    if not files:
                        print(f"  Não foi possível encontrar o módulo {module_name} nos arquivos .tf.")
            else:
                print("\nNenhum recurso aws_dynamodb_table encontrado no plano.")
    else:
        print("\nNenhum recurso aws_dynamodb_table foi detectado no terraform plan.")
        print("\nVerificando os arquivos .tf manualmente...")

        # Analisa diretamente os arquivos .tf se o `terraform plan` não encontrar
        found_dynamodb = search_in_terraform_files()
        if not found_dynamodb:
            print("\nNenhum arquivo .tf tenta criar uma tabela DynamoDB.")

# Executar a função principal
check_all_files_for_dynamodb()
